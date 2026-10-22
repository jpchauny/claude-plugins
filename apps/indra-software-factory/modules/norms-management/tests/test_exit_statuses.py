"""The exit statuses of every command, and the unexpected error.

0 success; 1 verify found a problem or report has no report to print;
2 a refusal of build or a usage error, nothing written; 3 the system
stopped build part way; 4 an unexpected error, with its stack trace. An
interrupt keeps Python's default behaviour.

Spec: R34, R62, R64
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from norms_generator import cli
from norms_generator.cli import main
from test_cli import Foundation


def _build(f: Foundation, out: Path, *extra: str) -> int:
    return main(["build", "--foundation", str(f.root), "--out", str(out), *extra])


def _verify(f: Foundation, out: Path) -> int:
    return main(["verify", "--foundation", str(f.root), "--out", str(out)])


def _one_file(tmp_path: Path) -> tuple[Foundation, Path]:
    f = Foundation(tmp_path / "foundation")
    f.write("specs/a.md", "# A\n\nText.\n")
    f.commit()
    return f, tmp_path / "norms"


def _boom(*_args: object, **_kwargs: object) -> None:
    raise RuntimeError("boom")


# --- 0 -----------------------------------------------------------------------


def test_every_command_exits_with_0_on_success_r62(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Build, verify and report exit with status 0 when they do what they are asked.

    Spec: R62
    """
    f, out = _one_file(tmp_path)
    assert _build(f, out) == cli.EXIT_OK == 0
    assert _verify(f, out) == 0
    assert main(["report", "--out", str(out)]) == 0
    assert main(["report", "--out", str(out), "--json"]) == 0
    assert capsys.readouterr().err == ""


def test_help_exits_with_0_r62(capsys: pytest.CaptureFixture[str]) -> None:
    """`--help` prints the usage and exits with status 0.

    Spec: R62
    """
    with pytest.raises(SystemExit) as exc:
        main(["--help"])
    assert exc.value.code == 0
    assert capsys.readouterr().out.startswith("usage: norms-gen")


# --- 1 -----------------------------------------------------------------------


def test_verify_exits_with_1_on_a_problem_r62_r64(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Verify exits with status 1 when it finds a problem.

    Spec: R62, R64
    """
    f, out = _one_file(tmp_path)
    assert _verify(f, out) == cli.EXIT_PROBLEMS == 1  # no JSONL
    assert capsys.readouterr().err.endswith("verify: 1 problems\n")


def test_report_exits_with_1_without_a_report_r62(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Report exits with status 1 when nothing is at its path, or it cannot be opened.

    Spec: R62
    """
    out = tmp_path / "norms"
    assert main(["report", "--out", str(out)]) == 1
    (out / "data" / "report.md").mkdir(parents=True)
    assert main(["report", "--out", str(out)]) == 1
    err = capsys.readouterr().err
    assert err.endswith(f"{out / 'data' / 'report.md'}: cannot be opened: Is a directory\n")


# --- 2 -----------------------------------------------------------------------


def test_a_refusal_exits_with_2_and_writes_nothing_r34_r62(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A refusal of build exits with status 2, and nothing is written.

    Spec: R34, R62
    """
    f = Foundation(tmp_path / "foundation")
    f.write("CLAUDE.md", "# Instructions for agents\n")  # R62: excluded, so no .md file to build
    f.commit()
    out = tmp_path / "norms"
    assert _build(f, out) == cli.EXIT_REFUSED == 2
    assert capsys.readouterr().err.startswith("norms-gen: no .md file to build at ")
    assert not out.exists()


def test_a_usage_error_exits_with_2_r62(capsys: pytest.CaptureFixture[str]) -> None:
    """A usage error, as a missing --foundation or an unknown command, exits with status 2.

    Spec: R62
    """
    for argv in (["build"], ["nope"], []):
        with pytest.raises(SystemExit) as exc:
            main(argv)
        assert exc.value.code == 2
        assert capsys.readouterr().err.startswith("usage: norms-gen")


# --- 3 -----------------------------------------------------------------------


def test_a_build_stopped_by_the_system_exits_with_3_r62(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """A write the system refuses stops build part way, with its message and status 3.

    Spec: R62
    """
    f, out = _one_file(tmp_path)
    jsonl = out / "data" / "tree.jsonl"

    def refuse(path: Path, _store: object) -> None:
        raise PermissionError(13, "Permission denied", str(path))

    monkeypatch.setattr(cli, "write_store", refuse)
    assert _build(f, out) == cli.EXIT_STOPPED == 3
    assert capsys.readouterr().err == f"norms-gen: {jsonl}: cannot be written: Permission denied\n"
    assert (out / "specs-repo-annotated" / "specs" / "a.md").is_file()  # written before it stopped
    assert not jsonl.exists()
    monkeypatch.undo()
    assert _build(f, out) == 0
    assert _verify(f, out) == 0


# --- 4 -----------------------------------------------------------------------


def test_an_unexpected_error_in_build_prints_its_traceback_and_exits_with_4_r62(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """An unexpected error prints `unexpected error: <type>: <message>`, then the stack trace, and exits with 4.

    Spec: R62
    """
    f, out = _one_file(tmp_path)
    monkeypatch.setattr(cli, "assign_ids", _boom)
    assert _build(f, out) == cli.EXIT_UNEXPECTED == 4
    captured = capsys.readouterr()
    assert captured.out == ""
    lines = captured.err.splitlines()
    assert lines[0] == "norms-gen: unexpected error: RuntimeError: boom"
    assert lines[1] == "Traceback (most recent call last):"
    assert any('in build' in line for line in lines)  # the frames, down to where it was raised
    assert any('in _boom' in line for line in lines)
    assert lines[-1] == "RuntimeError: boom"
    assert not out.exists()


def test_an_unexpected_error_in_verify_exits_with_4_not_1_r62_r64(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """An unexpected error in verify is no problem it found: status 4, with the stack trace.

    Spec: R62, R64
    """
    f, out = _one_file(tmp_path)
    assert _build(f, out) == 0
    capsys.readouterr()
    monkeypatch.setattr(cli, "check_file", _boom)
    assert _verify(f, out) == 4
    err = capsys.readouterr().err
    assert err.startswith("norms-gen: unexpected error: RuntimeError: boom\nTraceback (most recent call last):\n")
    assert err.endswith("RuntimeError: boom\n")
    assert "verify: " not in err


def test_the_installed_command_exits_with_4_on_an_unexpected_error_r62(tmp_path: Path) -> None:
    """The process itself ends with status 4, the message and the traceback on standard error.

    Spec: R62
    """
    f, out = _one_file(tmp_path)
    code = (
        "import sys\n"
        "from norms_generator import cli\n"
        "def boom(*a, **k):\n"
        "    raise ValueError('bad value')\n"
        "cli.build = boom\n"
        f"sys.exit(cli.main(['build', '--foundation', {str(f.root)!r}, '--out', {str(out)!r}]))\n"
    )
    done = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=60)
    assert done.returncode == 4
    assert done.stdout == ""
    assert done.stderr.startswith("norms-gen: unexpected error: ValueError: bad value\nTraceback (most recent call last):\n")
    assert done.stderr.endswith("ValueError: bad value\n")


def test_an_interrupt_keeps_pythons_default_behaviour_r62(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """KeyboardInterrupt is not caught as an unexpected error: it leaves main() as Python raised it.

    Spec: R62
    """
    f, out = _one_file(tmp_path)

    def interrupt(*_args: object, **_kwargs: object) -> None:
        raise KeyboardInterrupt

    monkeypatch.setattr(cli, "assign_ids", interrupt)
    with pytest.raises(KeyboardInterrupt):
        _build(f, out)
