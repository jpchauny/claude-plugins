"""The pending-work tree on GitHub issues and sub-issues.

Usage:
    python3 -I issue_tree.py link <parent issue URL> <child issue URL>
    python3 -I issue_tree.py tree <owner/repo> [--tema <name>] [--html <file>]

`link` makes the child a sub-issue of the parent (across repositories too;
a child that already has a parent moves).

`tree` finds the open issue labelled `baseline` in <owner/repo> (the
current baseline), walks its sub-issues down to 8 levels, and prints the
summary and the tree. With --tema it keeps only the branches holding an
issue labelled `tema:<name>`. With --html it also writes the page. Only
what the caller's GitHub account can see is read; issues of repositories
it cannot see do not appear.

State of a node, from its labels: `question` ⏳ waits for the user,
`blocked` ⛔ blocked, `breaks-ci` 🔴 breaks CI, anything else ▶ Claude can
advance. Uses `gh` (logged in); no other dependency.
"""
from __future__ import annotations

import html
import json
import subprocess
import sys
from datetime import date

FIELDS = """
  number title url state
  repository { nameWithOwner }
  labels(first: 20) { nodes { name } }
  subIssues(first: 100) { totalCount nodes { id } }
"""


def gh_graphql(query: str, **variables) -> dict:
    args = ["gh", "api", "graphql", "-H", "GraphQL-Features: sub_issues", "-f", f"query={query}"]
    for key, value in variables.items():
        args += ["-F" if isinstance(value, int) else "-f", f"{key}={value}"]
    out = subprocess.run(args, capture_output=True, text=True)
    if out.returncode != 0:
        sys.exit(f"gh api graphql failed: {out.stderr.strip()}")
    data = json.loads(out.stdout)
    if data.get("errors"):
        sys.exit("GraphQL error: " + "; ".join(e.get("message", "") for e in data["errors"]))
    return data["data"]


def node_id(url: str) -> str:
    owner, repo, _, number = url.rstrip("/").split("/")[-4:]
    q = "query($o:String!,$r:String!,$n:Int!){repository(owner:$o,name:$r){issue(number:$n){id}}}"
    return gh_graphql(q, o=owner, r=repo, n=int(number))["repository"]["issue"]["id"]


def link(parent_url: str, child_url: str) -> None:
    q = """mutation($p:ID!,$c:String!){addSubIssue(input:{issueId:$p,subIssueUrl:$c,replaceParent:true}){
      issue{number repository{nameWithOwner}} subIssue{number repository{nameWithOwner}}}}"""
    d = gh_graphql(q, p=node_id(parent_url), c=child_url)["addSubIssue"]
    print(f"{d['subIssue']['repository']['nameWithOwner']}#{d['subIssue']['number']} → "
          f"child of {d['issue']['repository']['nameWithOwner']}#{d['issue']['number']}")


def fetch(ids: list[str]) -> list[dict]:
    # gh cannot pass a list variable with -f, so the ids are inlined.
    q ="{nodes(ids:[" + ",".join(json.dumps(i) for i in ids) + "]){... on Issue{id " + FIELDS + "}}}"
    nodes = gh_graphql(q)["nodes"]
    return [n for n in nodes if n]  # an issue the caller cannot see comes back null


def build(node: dict, depth: int = 0) -> dict:
    labels = [l["name"] for l in node["labels"]["nodes"]]
    item = {
        "ref": f"{node['repository']['nameWithOwner']}#{node['number']}",
        "title": node["title"], "url": node["url"], "open": node["state"] == "OPEN",
        "labels": labels, "children": [],
    }
    kids = [k["id"] for k in node["subIssues"]["nodes"]]
    if kids and depth < 8:
        item["children"] = [build(k, depth + 1) for k in fetch(kids)]
    return item


def state(item: dict) -> str:
    labels = item["labels"]
    if not item["open"]:
        return "✓"
    if "breaks-ci" in labels:
        return "🔴"
    if "question" in labels:
        return "⏳"
    if "blocked" in labels:
        return "⛔"
    return "▶"


def keep_tema(item: dict, tema: str) -> dict | None:
    kids = [k for k in (keep_tema(c, tema) for c in item["children"]) if k]
    if f"tema:{tema}" in item["labels"] or kids:
        return {**item, "children": kids}
    return None


def walk(item: dict):
    yield item
    for c in item["children"]:
        yield from walk(c)


def short_ref(ref: str, home: str) -> str:
    repo, num = ref.split("#")
    name = repo.split("/")[-1].replace("clean-language-", "")
    return f"#{num}" if repo == home else f"{name}#{num}"


def render_text(root: dict, home: str) -> str:
    nodes = [n for n in walk(root) if n is not root and n["open"]]
    waiting = sum(1 for n in nodes if state(n) == "⏳")
    red = [short_ref(n["ref"], home) for n in nodes if state(n) == "🔴"]
    lines = [f"{root['title']} · {len(nodes)} abiertos · ⏳ {waiting} esperan de ti"
             + (f" · 🔴 {', '.join(red)}" if red else "")]

    def rec(item, prefix):
        kids = [k for k in item["children"] if k["open"]]
        for i, k in enumerate(kids):
            last = i == len(kids) - 1
            tema = next((l[5:] for l in k["labels"] if l.startswith("tema:")), "")
            lines.append(f"{prefix}{'└─' if last else '├─'} {state(k)} {short_ref(k['ref'], home):<14} "
                         f"{k['title']}" + (f"  [{tema}]" if tema else ""))
            rec(k, prefix + ("   " if last else "│  "))

    rec(root, "")
    lines.append("⏳ espera de ti   ▶ Claude puede avanzar   ⛔ bloqueado   🔴 rompe CI")
    return "\n".join(lines)


CSS = """
:root{--bg:#f6f7f6;--surface:#fff;--fg:#1d2523;--muted:#5d6b67;--line:#d9dfdc;--accent:#1f6f63;
--you:#b4620b;--you-bg:#fbeedd;--claude:#2a5fa8;--claude-bg:#e3ecf8;--blocked:#6a6f75;--blocked-bg:#e9ebed;--red:#b3261e;--red-bg:#f9e2df}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#141917;--surface:#1c2321;--fg:#e4ebe8;--muted:#9aa8a3;--line:#2f3a37;--accent:#5fbfae;
--you:#f0a95a;--you-bg:#3a2a15;--claude:#8cb4ef;--claude-bg:#1d2a3d;--blocked:#a6acb2;--blocked-bg:#2a2f33;--red:#f2928a;--red-bg:#3d1e1b;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#141917;--surface:#1c2321;--fg:#e4ebe8;--muted:#9aa8a3;--line:#2f3a37;--accent:#5fbfae;
--you:#f0a95a;--you-bg:#3a2a15;--claude:#8cb4ef;--claude-bg:#1d2a3d;--blocked:#a6acb2;--blocked-bg:#2a2f33;--red:#f2928a;--red-bg:#3d1e1b;color-scheme:dark}
*{box-sizing:border-box}
body{background:var(--bg);color:var(--fg);font-family:"Atkinson Hyperlegible","Segoe UI",system-ui,sans-serif;font-size:15px;line-height:1.5;
padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));padding-block:24px 48px}
.wrap{max-width:860px;margin:0 auto;display:flex;flex-direction:column;gap:24px}
h1{font-size:1.5rem;margin:0}h2{font-size:1.02rem;margin:0 0 8px}.sub{color:var(--muted);margin:4px 0 0}
.box{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:12px 16px}
.inbox{border-left:4px solid var(--you)}.inbox ul{margin:0;padding-left:1.1rem;display:grid;gap:4px}
details>summary{list-style:none;cursor:pointer;padding:6px 4px;border-radius:6px;display:flex;gap:10px;align-items:baseline;flex-wrap:wrap}
details>summary::-webkit-details-marker{display:none}details>summary::before{content:"▸";color:var(--muted);width:1ch}
details[open]>summary::before{content:"▾"}details>summary:hover{background:var(--bg)}
.leaf{display:flex;gap:10px;align-items:baseline;flex-wrap:wrap;padding:6px 4px 6px calc(1ch + 14px)}
.kids{margin-left:14px;padding-left:12px;border-left:1px dashed var(--line)}
.t{font-weight:700;min-width:0}.ref{font-family:"JetBrains Mono",ui-monospace,Menlo,monospace;font-size:.78rem;color:var(--accent);text-decoration:none}
.tema{font-size:.78rem;color:var(--muted)}
.chip{display:inline-flex;gap:6px;align-items:center;border-radius:999px;padding:1px 9px;font-size:.76rem;font-weight:700;white-space:nowrap}
.s-you{color:var(--you);background:var(--you-bg)}.s-claude{color:var(--claude);background:var(--claude-bg)}
.s-blocked{color:var(--blocked);background:var(--blocked-bg)}.s-red{color:var(--red);background:var(--red-bg)}
a:focus-visible,summary:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
"""
CHIP = {"⏳": ("s-you", "Espera de ti"), "▶": ("s-claude", "Claude puede"),
        "⛔": ("s-blocked", "Bloqueado"), "🔴": ("s-red", "Rompe CI")}


def render_html(root: dict, home: str) -> str:
    e = html.escape
    nodes = [n for n in walk(root) if n is not root and n["open"]]
    waiting = [n for n in nodes if state(n) == "⏳"]

    def row(k):
        cls, label = CHIP[state(k)]
        tema = next((l[5:] for l in k["labels"] if l.startswith("tema:")), "")
        return (f'<span class="t">{e(k["title"])}</span><a class="ref" href="{e(k["url"])}">'
                f'{e(short_ref(k["ref"], home))}</a><span class="chip {cls}">{label}</span>'
                + (f'<span class="tema">{e(tema)}</span>' if tema else ""))

    def rec(item):
        out = []
        for k in [c for c in item["children"] if c["open"]]:
            if any(c["open"] for c in k["children"]):
                out.append(f'<details open><summary>{row(k)}</summary><div class="kids">{rec(k)}</div></details>')
            else:
                out.append(f'<div class="leaf">{row(k)}</div>')
        return "".join(out)

    inbox = "".join(f'<li><a class="ref" href="{e(n["url"])}">{e(short_ref(n["ref"], home))}</a> '
                    f'{e(n["title"])}</li>' for n in waiting) or "<li>Nada espera de ti.</li>"
    return f"""<title>Árbol de pendientes</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700&family=JetBrains+Mono:wght@400&display=swap">
<style>{CSS}</style>
<div class="wrap">
<header><h1>{e(root["title"])}</h1>
<p class="sub">{len(nodes)} abiertos · {len(waiting)} esperan de ti · generado el {date.today().isoformat()} desde
<a class="ref" href="{e(root["url"])}">{e(root["ref"])}</a></p></header>
<section class="box inbox"><h2>Espera tu decisión ({len(waiting)})</h2><ul>{inbox}</ul></section>
<section class="box">{rec(root)}</section>
</div>
"""


def tree(home: str, tema: str | None, html_out: str | None) -> None:
    owner, repo = home.split("/")
    q = """query($o:String!,$r:String!){repository(owner:$o,name:$r){
      issues(first:5,states:OPEN,labels:["baseline"],orderBy:{field:CREATED_AT,direction:DESC}){nodes{id}}}}"""
    found = gh_graphql(q, o=owner, r=repo)["repository"]["issues"]["nodes"]
    if not found:
        sys.exit(f"no open issue labelled `baseline` in {home}")
    root = build(fetch([found[0]["id"]])[0])
    if tema:
        root = keep_tema(root, tema) or {**root, "children": []}
    print(render_text(root, home))
    if html_out:
        with open(html_out, "w", encoding="utf-8") as f:
            f.write(render_html(root, home))
        print(f"\npage written: {html_out}")


def main(argv: list[str]) -> int:
    if len(argv) >= 3 and argv[0] == "link":
        link(argv[1], argv[2])
        return 0
    if len(argv) >= 2 and argv[0] == "tree":
        opts = dict(zip(argv[2::2], argv[3::2]))
        tree(argv[1], opts.get("--tema"), opts.get("--html"))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
