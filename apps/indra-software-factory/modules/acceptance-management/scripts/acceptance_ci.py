"""Run the acceptance tests in the continuous integration of ACU-34, and record them.

Usage (by the workflow .github/workflows/acceptance.yml of the acceptance
repository, which /project-management:create-project writes):

    python3 -I acceptance_ci.py --repo <root of the acceptance repository> \
        --work <scratch folder> --produced-by <URL of the run> \
        --token-file <file with CODE_READ_TOKEN> \
        [--git-url <template>] [--date <YYYY-MM-DDTHH:MM:SS+00:00>]

Spec: specs/module.md of acceptance-management. The fields of
acceptance.json ("test_command", "product" and its "build", "env" and
"published"), and the variables ACCEPTANCE_TARGET and ACCEPTANCE_REPORT, are
those of ACU-6; the fields of a line of records/ are those of ACU-35; the steps
are those of ACU-34, in its order:

1. "test_command" empty: says so, writes nothing, ends with 0.
2. Reads the reference commit of each code repository of project.json (layer
   4) with "git ls-remote", using the token CODE_READ_TOKEN, which can only
   read them. The token comes in --token-file, which is deleted as soon as it
   is read; it is refused in the environment, where a "build" or
   "test_command" (same user) could read it in /proc/<pid>/environ. It reaches
   git only in an http.extraHeader of the command line of git calls that end
   before any "build" runs, never in a URL (git writes the URL to FETCH_HEAD).
3. When the last recorded run (the lines of kind "test" of records/ with the
   latest "date") has exactly these reference commits, and no file outside
   records/ differs between its "acceptance_commit" and HEAD: says so, writes
   nothing, ends with 0.
4. Clones the code repository of every entry of "product" at its reference
   commit, all before any "build" runs; then runs "build" of each entry in its
   clone ("published" is not used here: only an
   implementing agent runs it, ACU-49). A failed build writes nothing and
   ends with 1.
5. Runs "test_command" for each folder tests/<ID>/, in the order of the IDs
   (AA before AU, then by number).
6. Adds one line of kind "test" per result to records/<ID>.jsonl, never
   changing a line already there. Every result of a folder is recorded for
   every file of the folder, which is never less strict than ACU-26.

--work must be outside --repo (ACU-34); otherwise it writes nothing and ends
with 1. It runs no git command that writes: the workflow commits and pushes
records/.
"""

import argparse
import base64
import datetime
import hashlib
import json
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

TARGET = re.compile(r"^(AU|AA)-\d+$")
ENV_NAME = re.compile(r"^[A-Z_][A-Z0-9_]*$")
CITATION = re.compile(r"\b([A-Z][A-Z0-9]*-\d+)@([0-9a-f]{8})\b")
UNIT_TAG = re.compile(r"@unit:(AU-\d+)\b")
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+00:00$")  # ACU-35
GIT_URL = "https://github.com/{owner}/{name}.git"


class Failure(Exception):
    pass


def blob_hash(data: bytes) -> str:
    """The hash that git gives to a file with these bytes."""
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def run(cmd, **kw) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def code_repositories(repo: Path) -> list[dict]:
    data = json.loads((repo / "project.json").read_text(encoding="utf-8"))
    return [r for r in data["repositories"] if r["layer"] == 4]


def auth(token: str) -> list[str]:
    """The options of git that give it the token, on its command line only (ACU-34)."""
    if not token:
        return []
    basic = base64.b64encode(f"x-access-token:{token}".encode()).decode()
    return ["-c", f"http.extraHeader=Authorization: Basic {basic}"]


def reference_commit(url: str, name: str, token: str) -> str:
    out = run(["git", *auth(token), "ls-remote", url, "HEAD"])
    if out.returncode or not out.stdout.strip():
        raise Failure(f"cannot read the reference commit of {name}")
    return out.stdout.split()[0]


def clone(url: str, name: str, commit: str, work: Path, token: str) -> Path:
    """Copy one code repository at its reference commit (ACU-34, step 4), leaving no trace of the token."""
    work.mkdir(parents=True, exist_ok=True)
    folder = work / "code" / name.replace("/", "__")
    steps = [
        ["git", "init", "-q", str(folder)],
        ["git", *auth(token), "-C", str(folder), "fetch", "-q", "--depth", "1", url, commit],
        ["git", "-C", str(folder), "checkout", "-q", commit],
    ]
    for step in steps:
        if run(step).returncode:
            raise Failure(f"cannot clone {name} at {commit}")
    (folder / ".git" / "FETCH_HEAD").unlink(missing_ok=True)
    return folder


def build(folder: Path, name: str, entry: dict, env: dict) -> str:
    """Run "build" of one entry of "product" (ACU-34, step 4)."""
    out = run(entry["build"], shell=True, cwd=folder, env=env)
    lines = [line for line in out.stdout.splitlines() if line.strip()]
    if out.returncode or not lines:
        raise Failure(f"the build of {name} failed:\n{out.stdout}{out.stderr}")
    return lines[-1].strip()


def results(report: Path, folder: str, returncode: int) -> list[tuple[str, str]]:
    if report.is_file():
        try:
            root = ET.parse(report).getroot()
        except ET.ParseError:
            root = None
        if root is not None:
            found = []
            for case in root.iter("testcase"):
                name = "::".join(p for p in (case.get("classname"), case.get("name")) if p)
                if case.find("failure") is not None or case.find("error") is not None:
                    found.append((name, "fail"))
                elif case.find("skipped") is not None:
                    found.append((name, "skipped"))
                else:
                    found.append((name, "pass"))
            if found:
                return found
    return [(folder, "pass" if returncode == 0 else "fail")]


def produced_for(repo: Path, target: str) -> tuple[dict, dict]:
    folder = repo / "tests" / target
    files, norms = {}, {}
    own = repo / ("units" if target.startswith("AU-") else "areas") / f"{target}.md"
    sources = [own]
    if own.is_file() and target.startswith("AA-"):
        crossed = sorted(set(UNIT_TAG.findall(own.read_text(encoding="utf-8", errors="replace"))))
        sources += [repo / "units" / f"{u}.md" for u in crossed]
    sources += sorted(p for p in folder.rglob("*") if p.is_file())
    for path in sources:
        if not path.is_file():
            continue
        data = path.read_bytes()
        files[path.relative_to(repo).as_posix()] = blob_hash(data)
        if path.is_relative_to(folder):
            for norm_id, norm_hash in CITATION.findall(data.decode("utf-8", errors="replace")):
                norms[norm_id] = norm_hash
    return dict(sorted(norms.items())), files


def last_run(repo: Path) -> list[dict]:
    """The lines of kind "test" of records/ whose "date" is the latest (ACU-34, step 3)."""
    lines = []
    records = repo / "records"
    for path in sorted(records.glob("*.jsonl")) if records.is_dir() else []:
        for text in path.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                line = json.loads(text)
            except ValueError:
                continue
            if isinstance(line, dict) and line.get("kind") == "test" and isinstance(line.get("date"), str):
                lines.append(line)
    if not lines:
        return []
    latest = max(line["date"] for line in lines)
    return [line for line in lines if line["date"] == latest]


def unchanged(repo: Path, commits: dict) -> bool:
    """ACU-34, step 3: whether the last recorded run tested these reference commits and these files."""
    last = last_run(repo)
    if not last:
        return False
    for line in last:
        for_ = line.get("for")
        if not isinstance(for_, dict) or for_.get("reference_commits") != commits:
            return False
    tested = {line.get("acceptance_commit") for line in last}
    if len(tested) != 1:
        return False
    commit = tested.pop()
    if not isinstance(commit, str) or not re.fullmatch(r"[0-9a-f]{7,64}", commit):
        return False
    diff = run(["git", "-C", str(repo), "diff", "--quiet", commit, "HEAD", "--", ".", ":(exclude)records"])
    return diff.returncode == 0


def id_order(name: str) -> tuple[str, int]:
    """The order of the IDs of ACU-34: by prefix, then by number."""
    prefix, number = name.split("-")
    return prefix, int(number)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--work", required=True, type=Path)
    parser.add_argument("--produced-by", required=True)
    parser.add_argument("--token-file", type=Path, default=None,
                        help="file that holds CODE_READ_TOKEN; it is deleted as soon as it is read")
    parser.add_argument("--git-url", default=GIT_URL,
                        help="template of the URL of a code repository, with {owner} and {name}")
    parser.add_argument("--date", default=None)
    args = parser.parse_args(argv)
    # ACU-34: the token never reaches the run through its environment, which
    # every process of the same user can read in /proc/<pid>/environ.
    token = ""
    if args.token_file is not None:
        try:
            token = args.token_file.read_text(encoding="utf-8").strip()
        finally:
            args.token_file.unlink(missing_ok=True)
    if "CODE_READ_TOKEN" in os.environ:
        print("error: CODE_READ_TOKEN is in the environment, where a build could read it; "
              "pass it with --token-file (ACU-34)", file=sys.stderr)
        return 1
    repo, work = args.repo.resolve(), args.work.resolve()
    if work.is_relative_to(repo):
        print(f"error: --work {work} is inside --repo {repo}; it must be outside the acceptance repository (ACU-34)",
              file=sys.stderr)
        return 1

    config = json.loads((repo / "acceptance.json").read_text(encoding="utf-8"))
    command = config.get("test_command", "")
    if not command:
        print("test_command is empty in acceptance.json: no code to test yet; nothing recorded")
        return 0
    product = config.get("product", {})
    if not isinstance(product, dict):
        print("error: product of acceptance.json must be an object (ACU-6)", file=sys.stderr)
        return 1
    if args.date is not None and not DATE.match(args.date):
        print("error: --date must have the form YYYY-MM-DDTHH:MM:SS+00:00 (ACU-35)", file=sys.stderr)
        return 1
    date = args.date or datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()
    try:
        codes = {f"{r['owner']}/{r['name']}": r for r in code_repositories(repo)}
        unknown = sorted(set(product) - set(codes))
        if unknown:
            raise Failure("product names a repository that is not of layer 4 in project.json: " + ", ".join(unknown))
        for name, entry in product.items():
            if (not isinstance(entry, dict) or not isinstance(entry.get("build"), str) or not entry["build"]
                    or not isinstance(entry.get("env"), str) or not ENV_NAME.match(entry["env"])
                    or ("published" in entry and (not isinstance(entry["published"], str) or not entry["published"]))
                    or set(entry) - {"build", "env", "published"}):
                raise Failure(f"product of {name} must hold \"build\" and \"env\" (an environment variable name), "
                              "\"published\" only as a command, and no other field (ACU-6)")
        urls = {name: args.git_url.format(owner=r["owner"], name=r["name"]) for name, r in codes.items()}
        commits = {name: reference_commit(url, name, token) for name, url in urls.items()}
        if unchanged(repo, commits):
            print("no reference commit and no file outside records/ changed since the last recorded run; nothing recorded")
            return 0
        # Every clone is made before any code of layer 4 runs, so no "build"
        # can leave a process behind that reads the token of a later git call.
        folders = {name: clone(urls[name], name, commits[name], work, token) for name in product}
        token = ""
        clean = dict(os.environ)
        env = dict(clean)
        for name, entry in product.items():
            env[entry["env"]] = build(folders[name], name, entry, clean)
    except Failure as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    head = run(["git", "-C", str(repo), "rev-parse", "HEAD"])
    acceptance_commit = head.stdout.strip() if not head.returncode else None
    tests = repo / "tests"
    targets = sorted((p.name for p in tests.iterdir() if p.is_dir() and TARGET.match(p.name)),
                     key=id_order) if tests.is_dir() else []
    (work / "reports").mkdir(parents=True, exist_ok=True)
    (repo / "records").mkdir(exist_ok=True)
    for target in targets:
        report = work / "reports" / f"{target}.xml"
        report.unlink(missing_ok=True)
        out = subprocess.run(command, shell=True, cwd=repo,
                             env=env | {"ACCEPTANCE_TARGET": f"tests/{target}", "ACCEPTANCE_REPORT": str(report)})
        norms, files = produced_for(repo, target)
        found = results(report, f"tests/{target}", out.returncode)
        lines = []
        for name, result in found:
            lines.append(json.dumps({
                "kind": "test", "test": name, "result": result,
                "for": {"norm_hashes": norms, "files": files, "reference_commits": commits},
                "acceptance_commit": acceptance_commit, "date": date, "produced_by": args.produced_by,
            }))
        with open(repo / "records" / f"{target}.jsonl", "a", encoding="utf-8") as f:
            f.write("".join(line + "\n" for line in lines))
        print(f"{target}: " + ", ".join(f"{n} {r}" for n, r in found))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
