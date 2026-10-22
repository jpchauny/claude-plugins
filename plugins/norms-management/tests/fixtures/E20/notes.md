# E20: folder

The spec has no snippet for E20: a folder is not annotated and has no
ID (R14); it is identified by its path. The annotated files of layer 2
keep the folder tree of foundation (R62: `specs-repo-annotated/` mirrors it).

The test builds a small foundation git repository in a temporary
directory, runs `norms-gen build` on it, and checks that every `.md`
file appears under the output at the same relative path, and no folder
gets a marker.
