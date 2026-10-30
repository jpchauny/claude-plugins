"""Write the record of the types of derived norms of the step of layer 2 (NRM-16).

Usage:
    python3 -I write_types_of_derived_norms.py --norms-repository <root of the norms repository>

Reads the project.json of the working tree of the norms repository, the one
by which the step ran the derived-norms generators (NRM-1, NRM-2), and
writes specs-derived/types-of-derived-norms.json: one JSON object, with the
field types_of_derived_norms, the type of each entry of derived_norms in
its order ([] when there is none), followed by one line feed. The outputs,
byte for byte, are those of NRM-16: the path written on standard output,
exit 0; or, leaving the record of the working tree as it was, one line on
standard error, exit 1.

Runs with Python 3.9 or later and its standard library only (MTH-5).
"""

from __future__ import annotations

import argparse
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from compare_derived_norms import (  # noqa: E402
    RECORD_OF_THE_TYPES_OF_DERIVED_NORMS_PATH,
    TypesOfDerivedNormsError,
    text_of_record_of_the_types_of_derived_norms,
    types_of_derived_norms_of_project_json,
)

THE_FILE_CANNOT_BE_WRITTEN = "the file cannot be written"  # NRM-16


def fail(reason: str) -> int:
    """NRM-16, outcome 2."""
    sys.stderr.buffer.write(
        f"norms-management: the record of the types of derived norms is not written (NRM-16): {reason}\n".encode("utf-8"))
    return 1


def write_record(record: Path, text: str) -> None:
    """Writes the whole record or nothing: a temporary file beside it, then renamed over it."""
    record.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(dir=str(record.parent), prefix=".types-of-derived-norms.")
    try:
        with os.fdopen(descriptor, "wb") as file:
            file.write(text.encode("utf-8"))
        umask = os.umask(0)
        os.umask(umask)
        os.chmod(temporary, 0o666 & ~umask)  # mkstemp makes it readable only by its owner; a file is not.
        os.replace(temporary, str(record))
    except BaseException:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise


def main(argv: list[str]) -> int:
    # NRM-16, outcome 3: no abbreviated option and no --help, so any other argument exits with status 2.
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0], allow_abbrev=False, add_help=False)
    parser.add_argument("--norms-repository", required=True, type=Path)
    arguments = parser.parse_args(argv)
    norms_repository = arguments.norms_repository.resolve()
    project_json = norms_repository / "project.json"
    try:
        project_json_bytes = project_json.read_bytes() if project_json.is_file() else None
    except OSError:
        project_json_bytes = None
    try:
        types_of_derived_norms = types_of_derived_norms_of_project_json(project_json_bytes)
    except TypesOfDerivedNormsError as error:
        return fail(str(error))
    try:
        write_record(norms_repository / RECORD_OF_THE_TYPES_OF_DERIVED_NORMS_PATH,
                     text_of_record_of_the_types_of_derived_norms(types_of_derived_norms))
    except OSError:
        return fail(THE_FILE_CANNOT_BE_WRITTEN)
    sys.stdout.buffer.write((RECORD_OF_THE_TYPES_OF_DERIVED_NORMS_PATH + "\n").encode("utf-8"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
