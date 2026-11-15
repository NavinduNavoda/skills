#!/usr/bin/env python3
"""Plan state, snapshots and WHY-comment handling for the relay skills.

Uses only the Python standard library and git. Every command prints one JSON
object. On failure it prints {"error": ...} and exits 1, and the calling agent
does that step by hand.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

WHY_RE = re.compile(r"^[ \t]*(?://|#|--|;|%|/\*|<!--|\{/\*)[ \t]*WHY:")
WHY_TEXT_RE = re.compile(r"WHY:\s*(.*?)\s*(?:\*/\}?|-->)?\s*$")
NO_COMMENT_EXT = {".json", ".md", ".markdown", ".txt", ".lock", ".csv"}
DEP_DIRS = ["node_modules", ".venv", "venv"]
LOCK_STALE_SECONDS = 30 * 60
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
# /to-adr commits ADRs on their own, so they never count as part of a feature commit.
FEATURE_PATHS = ["--", ".", ":(exclude)docs/adr"]

PLAN_TEMPLATE = """# {id}: {title}

Branch: `{branch}`. Status: active.

## Goal

## Commits

## Decisions

## Open questions

## Session log

## WHY notes
"""


class RelayError(Exception):
    pass


def run(args, cwd=None, env=None, data=None, check=True):
    result = subprocess.run(args, cwd=cwd, env=env, input=data, capture_output=True)
    if check and result.returncode != 0:
        raise RelayError(f"{' '.join(args)}: {result.stderr.decode(errors='replace').strip()}")
    return result


def git(*args, cwd=None, env=None, data=None, check=True):
    return run(["git", *args], cwd=cwd, env=env, data=data, check=check).stdout.decode()


class Repo:
    def __init__(self, cwd="."):
        self.top = Path(git("rev-parse", "--show-toplevel", cwd=cwd).strip())
        common = git("rev-parse", "--path-format=absolute", "--git-common-dir", cwd=self.top)
        self.common = Path(common.strip())
        self.plans = self.common / "agent-plans"
        self.states = self.common / "agent-state"
        self.worktrees = self.common / "agent-worktrees"

    def g(self, *args, **kwargs):
        return git(*args, cwd=self.top, **kwargs)

    def head(self):
        return self.g("rev-parse", "HEAD").strip()

    def branch(self):
        name = self.g("symbolic-ref", "--quiet", "--short", "HEAD", check=False).strip()
        if not name:
            raise RelayError("HEAD is detached; check out a branch first")
        return name

    def state_dir(self, plan_id):
        return self.states / plan_id

    def plan_file(self, plan_id):
        return self.plans / f"{plan_id}.md"

    def worktree(self, plan_id):
        return self.worktrees / plan_id


# ---------- state ----------

def load_state(repo, plan_id=None):
    if plan_id:
        path = repo.state_dir(plan_id) / "state.json"
        if not path.exists():
            raise RelayError(f"no plan {plan_id}")
        return json.loads(path.read_text())
    branch = repo.branch()
    for path in sorted(repo.states.glob("*/state.json")):
        state = json.loads(path.read_text())
        if state["branch"] == branch and state["status"] == "active":
            return state
    raise RelayError(f"no active plan for branch {branch}; run /start-relay")


def save_state(repo, state):
    path = repo.state_dir(state["id"]) / "state.json"
    path.write_text(json.dumps(state, indent=2) + "\n")
    render_commits(repo, state)


def commit_entry(state, n):
    for entry in state["commits"]:
        if entry["n"] == n:
            return entry
    raise RelayError(f"plan {state['id']} has no commit {n}")


def find_entry(state, n):
    return next((c for c in state["commits"] if c["n"] == n), None)


# ---------- plan file ----------

def replace_section(text, heading, body_lines, append=False):
    lines = text.splitlines()
    try:
        start = lines.index(f"## {heading}")
    except ValueError:
        lines += ["", f"## {heading}"]
        start = len(lines) - 1
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    current = [l for l in lines[start + 1:end] if l.strip()]
    body = current + body_lines if append else body_lines
    block = [""] + body + [""] if body else [""]
    return "\n".join(lines[:start + 1] + block + lines[end:]).rstrip() + "\n"


def render_commits(repo, state):
    plan = repo.plan_file(state["id"])
    if not plan.exists():
        return
    lines = [f"{c['n']}. {c['title']} ({c['status']})" for c in state["commits"]]
    plan.write_text(replace_section(plan.read_text(), "Commits", lines))


def append_why_notes(repo, state, n, title, notes):
    plan = repo.plan_file(state["id"])
    if not notes or not plan.exists():
        return
    lines = [f"- commit {n} ({title}), `{path}:{line}`: {text}" for path, line, text in notes]
    plan.write_text(replace_section(plan.read_text(), "WHY notes", lines, append=True))


# ---------- WHY comments ----------

def can_hold_why(path):
    return Path(path).suffix.lower() not in NO_COMMENT_EXT


def why_text(line):
    match = WHY_TEXT_RE.search(line)
    return match.group(1) if match else line.strip()


def strip_text(text):
    """Remove WHY lines. Returns the new text and (line, why) pairs, where line
    is the 1-based line, in the new text, of the code the comment sat above."""
    out, notes, pending = [], [], []
    for line in text.splitlines(keepends=True):
        if WHY_RE.match(line):
            pending.append(why_text(line))
            continue
        if pending:
            notes += [(len(out) + 1, why) for why in pending]
            pending = []
        out.append(line)
    notes += [(max(len(out), 1), why) for why in pending]
    return "".join(out), notes


def decode(data):
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return None


def strip_working_files(repo, since):
    """Strip WHY lines from files changed since `since` or untracked. Edits in place."""
    names = set(filter(None, repo.g("diff", "--name-only", "-z", since).split("\0")))
    names |= set(filter(None, repo.g("ls-files", "--others", "--exclude-standard", "-z").split("\0")))
    notes = []
    for name in sorted(names):
        path = repo.top / name
        if not path.is_file() or path.is_symlink() or not can_hold_why(name):
            continue
        text = decode(path.read_bytes())
        if text is None:
            continue
        new_text, found = strip_text(text)
        if found:
            path.write_bytes(new_text.encode("utf-8"))
            notes += [(name, line, why) for line, why in found]
    return notes


def strip_commit(repo, commit, parent, message):
    """Return a commit like `commit` with WHY lines removed from the files it changed."""
    names = filter(None, repo.g("diff", "--name-only", "-z", "--diff-filter=AMR", parent, commit).split("\0"))
    with tempfile.TemporaryDirectory() as tmp:
        env = {**os.environ, "GIT_INDEX_FILE": str(Path(tmp) / "index")}
        repo.g("read-tree", commit, env=env)
        for name in names:
            if not can_hold_why(name):
                continue
            entry = repo.g("ls-tree", commit, "--", name).split()
            if not entry or entry[1] != "blob":
                continue
            text = decode(run(["git", "show", f"{commit}:{name}"], cwd=repo.top).stdout)
            if text is None:
                continue
            new_text, found = strip_text(text)
            if not found:
                continue
            blob = repo.g("hash-object", "-w", "--stdin", data=new_text.encode("utf-8")).strip()
            repo.g("update-index", "--cacheinfo", f"{entry[0]},{blob},{name}", env=env)
        tree = repo.g("write-tree", env=env).strip()
    if tree == repo.g("rev-parse", f"{commit}^{{tree}}").strip():
        return commit
    return repo.g("commit-tree", tree, "-p", parent, "-m", message).strip()


# ---------- snapshots ----------

def working_tree(repo):
    """Tree id of the working folder as `git add -A` would see it, without touching the index."""
    with tempfile.TemporaryDirectory() as tmp:
        env = {**os.environ, "GIT_INDEX_FILE": str(Path(tmp) / "index")}
        repo.g("read-tree", "HEAD", env=env)
        repo.g("add", "-A", env=env)
        return repo.g("write-tree", env=env).strip()


def set_ref(repo, state, name, sha):
    repo.g("update-ref", f"refs/relay/{state['id']}/{name}", sha)


def reset_worktree(repo, state, commit):
    wt = repo.worktree(state["id"])
    git("reset", "-q", "--hard", commit, cwd=wt)
    git("clean", "-fdq", cwd=wt)


# ---------- worktree setup ----------

def exclude(repo, names):
    path = repo.common / "info" / "exclude"
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = path.read_text().splitlines() if path.exists() else []
    new = [f"/{n}" for n in names if f"/{n}" not in existing]
    if new:
        with path.open("a") as handle:
            handle.write("\n".join(["# relay: dependency links in agent worktrees", *new]) + "\n")


def setup_worktree(repo, wt):
    copied, linked = [], []
    ignored = repo.g("ls-files", "--others", "--ignored", "--exclude-standard", "--directory", "-z")
    for name in filter(None, ignored.split("\0")):
        src = repo.top / name
        if Path(name.rstrip("/")).name.startswith(".env") and src.is_file():
            (wt / name).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, wt / name)
            copied.append(name)
    for name in DEP_DIRS:
        src = repo.top / name
        if src.is_dir() and not (wt / name).exists():
            (wt / name).symlink_to(src, target_is_directory=True)
            linked.append(name)
    exclude(repo, [n for n in linked if run(["git", "check-ignore", "-q", n], cwd=wt, check=False).returncode != 0])
    return copied, linked


# ---------- commands ----------

def cmd_init(repo, args):
    if not SLUG_RE.match(args.slug):
        raise RelayError("slug must be lowercase kebab-case, like auth or order-export")
    branch = repo.branch()
    if repo.g("status", "--porcelain").strip():
        raise RelayError("working tree has uncommitted changes; commit or stash them first")
    for path in repo.states.glob("*/state.json"):
        state = json.loads(path.read_text())
        if state["branch"] == branch and state["status"] == "active":
            raise RelayError(f"branch {branch} already has active plan {state['id']}")
    numbers = [int(p.name[:3]) for p in repo.plans.glob("[0-9][0-9][0-9]-*.md")] if repo.plans.exists() else []
    plan_id = f"{max(numbers, default=-1) + 1:03d}-{args.slug}"
    for folder in (repo.plans, repo.state_dir(plan_id), repo.worktrees):
        folder.mkdir(parents=True, exist_ok=True)
    wt = repo.worktree(plan_id)
    repo.g("worktree", "add", "-q", "-b", f"relay/{plan_id}", str(wt), "HEAD")
    copied, linked = setup_worktree(repo, wt)
    repo.plan_file(plan_id).write_text(PLAN_TEMPLATE.format(id=plan_id, title=args.title, branch=branch))
    state = {
        "id": plan_id, "title": args.title, "branch": branch, "status": "active",
        "base": repo.head(), "review": None, "commits": [],
        "worktree": str(wt), "linked": linked,
    }
    save_state(repo, state)
    return {"id": plan_id, "plan": str(repo.plan_file(plan_id)), "worktree": str(wt),
            "state": str(repo.state_dir(plan_id)), "copied": copied, "linked": linked}


def cmd_set_commits(repo, args):
    state = load_state(repo, args.plan)
    kept = [c for c in state["commits"] if c["status"] != "planned"]
    start = max((c["n"] for c in kept), default=0) + 1
    state["commits"] = kept + [{"n": start + i, "title": t, "status": "planned"} for i, t in enumerate(args.titles)]
    save_state(repo, state)
    return {"commits": state["commits"]}


def cmd_snapshot(repo, args):
    """Record the working folder as commit N, the version handed to the user for review."""
    state = load_state(repo, args.plan)
    entry = commit_entry(state, args.n)
    head = repo.head()
    orig = repo.g("commit-tree", working_tree(repo), "-p", head, "-m", f"relay {state['id']}: commit {args.n} as handed over").strip()
    base = strip_commit(repo, orig, head, f"relay {state['id']}: commit {args.n} without WHY comments")
    set_ref(repo, state, f"orig-{args.n}", orig)
    set_ref(repo, state, f"base-{args.n}", base)
    entry.update(status="review", orig=orig, base=base, handoff_head=head)
    entry.pop("built", None)
    state["review"] = args.n
    reset_worktree(repo, state, base)
    save_state(repo, state)
    return {"n": args.n, "orig": orig, "base": base, "worktree_at": base}


def cmd_building(repo, args):
    state = load_state(repo, args.plan)
    entry = commit_entry(state, args.n)
    entry.update(status="building", started_at=int(time.time()))
    entry.pop("built", None)
    save_state(repo, state)
    return {"n": args.n, "status": "building"}


def cmd_wt_commit(repo, args):
    """Commit the background build in the agent worktree as commit N."""
    state = load_state(repo, args.plan)
    entry = commit_entry(state, args.n)
    wt = Path(state["worktree"])
    git("add", "-A", cwd=wt)
    if not git("diff", "--cached", "--name-only", cwd=wt).strip():
        raise RelayError("the worktree has no changes to commit")
    git("commit", "-q", "--no-verify", "-m", entry["title"], cwd=wt)
    built = git("rev-parse", "HEAD", cwd=wt).strip()
    set_ref(repo, state, f"built-{args.n}", built)
    entry.update(status="built", built=built)
    save_state(repo, state)
    return {"n": args.n, "built": built}


def cmd_finalize(repo, args):
    """Strip WHY lines from the reviewed commit, detect user changes, commit it."""
    state = load_state(repo, args.plan)
    n = state["review"]
    if n is None:
        raise RelayError("no commit is in review")
    entry = commit_entry(state, n)
    moved = bool(repo.g("log", "--format=%H", f"{entry['handoff_head']}..HEAD", *FEATURE_PATHS).strip())
    notes = strip_working_files(repo, state["base"])
    append_why_notes(repo, state, n, entry["title"], notes)
    user = repo.g("commit-tree", working_tree(repo), "-p", repo.head(), "-m", "relay: user version").strip()
    changed = run(["git", "diff", "--quiet", entry["base"], user, *FEATURE_PATHS], cwd=repo.top, check=False).returncode != 0
    out_dir = repo.state_dir(state["id"])
    user_diff = None
    if changed:
        user_diff = out_dir / f"user-edits-{n}.diff"
        user_diff.write_text(repo.g("diff", entry["base"], user, *FEATURE_PATHS))
    message = None
    if repo.g("status", "--porcelain").strip():
        message = "chore: remove WHY comments" if moved else entry["title"]
        repo.g("add", "-A")
        repo.g("commit", "-q", "-m", message)
    entry.update(status="done", final=repo.head())
    state["review"] = None
    result = {"n": n, "user_committed": moved, "changed": changed, "user_diff": str(user_diff) if user_diff else None,
              "why_notes": len(notes), "commit_message": message}
    nxt = find_entry(state, n + 1)
    if nxt:
        result["next"] = {"n": nxt["n"], "title": nxt["title"], "status": nxt["status"]}
        if nxt["status"] == "built":
            patch = out_dir / f"next-{nxt['n']}.diff"
            patch.write_text(repo.g("diff", "--binary", entry["base"], nxt["built"], *FEATURE_PATHS))
            result["next"]["patch"] = str(patch)
    save_state(repo, state)
    return result


def cmd_bring(repo, args):
    """Apply the built commit N to the working folder, uncommitted."""
    state = load_state(repo, args.plan)
    entry = commit_entry(state, args.n)
    if entry["status"] != "built":
        raise RelayError(f"commit {args.n} is {entry['status']}, not built")
    patch = repo.state_dir(state["id"]) / f"next-{args.n}.diff"
    if not patch.exists():
        raise RelayError(f"no patch for commit {args.n}; run finalize first")
    if run(["git", "apply", "--whitespace=nowarn", str(patch)], cwd=repo.top, check=False).returncode == 0:
        return {"n": args.n, "applied": "clean", "conflicts": []}
    run(["git", "apply", "--3way", "--whitespace=nowarn", str(patch)], cwd=repo.top, check=False)
    conflicts = [c for c in repo.g("diff", "--name-only", "--diff-filter=U").splitlines() if c]
    repo.g("reset", "-q")
    return {"n": args.n, "applied": "3way" if not conflicts else "conflicts", "conflicts": conflicts}


def cmd_status(repo, args):
    try:
        state = load_state(repo, args.plan)
    except RelayError as err:
        return {"plan": None, "message": str(err)}
    folder = repo.state_dir(state["id"])
    questions = sorted(str(p) for p in folder.glob("questions-*.md"))
    review = state["review"]
    nxt = find_entry(state, review + 1) if review else None
    open_commits = [c for c in state["commits"] if c["status"] != "done"]
    if review:
        hint = "review" if not nxt or nxt["status"] in ("built", "planned") else "review-while-building"
    elif open_commits:
        hint = "resume"
    else:
        hint = "finish"
    return {"plan": state["id"], "title": state["title"], "plan_file": str(repo.plan_file(state["id"])),
            "worktree": state["worktree"], "review": review, "hint": hint, "questions": questions,
            "locked": lock_info(folder), "commits": [{k: c.get(k) for k in ("n", "title", "status")} for c in state["commits"]]}


def lock_info(folder):
    path = folder / "lock"
    if not path.exists():
        return None
    age = time.time() - path.stat().st_mtime
    return None if age > LOCK_STALE_SECONDS else {"age_seconds": int(age), "note": path.read_text().strip()}


def cmd_lock(repo, args):
    state = load_state(repo, args.plan)
    folder = repo.state_dir(state["id"])
    held = lock_info(folder)
    if held and not args.force:
        raise RelayError(f"plan {state['id']} is in use by another session ({held['age_seconds']}s ago)")
    (folder / "lock").write_text(f"pid {os.getppid()} at {time.ctime()}\n")
    return {"locked": state["id"]}


def cmd_unlock(repo, args):
    state = load_state(repo, args.plan)
    (repo.state_dir(state["id"]) / "lock").unlink(missing_ok=True)
    return {"unlocked": state["id"]}


def cmd_checks(repo, args):
    top, found = repo.top, []
    pkg = top / "package.json"
    if pkg.exists():
        scripts = json.loads(pkg.read_text()).get("scripts", {})
        if "typecheck" in scripts:
            found.append("npm run typecheck")
        elif (top / "tsconfig.json").exists():
            found.append("npx tsc --noEmit")
        if "test" in scripts and "no test specified" not in scripts["test"]:
            found.append("npm test")
    pyproject = top / "pyproject.toml"
    if pyproject.exists() or (top / "pytest.ini").exists() or (top / "setup.cfg").exists():
        if pyproject.exists() and "[tool.mypy]" in pyproject.read_text():
            found.append("python -m mypy .")
        if (top / "tests").is_dir() or (top / "test").is_dir():
            found.append("python -m pytest -q")
    if (top / "go.mod").exists():
        found += ["go vet ./...", "go test ./..."]
    if (top / "Cargo.toml").exists():
        found += ["cargo check", "cargo test"]
    return {"commands": found}


def cmd_finish(repo, args):
    state = load_state(repo, args.plan)
    wt = Path(state["worktree"])
    if wt.exists():
        repo.g("worktree", "remove", "--force", str(wt))
    repo.g("worktree", "prune")
    repo.g("branch", "-D", f"relay/{state['id']}", check=False)
    refs = repo.g("for-each-ref", "--format=%(refname)", f"refs/relay/{state['id']}/").split()
    for ref in refs:
        repo.g("update-ref", "-d", ref)
    folder = repo.state_dir(state["id"])
    for path in folder.glob("*.diff"):
        path.unlink()
    (folder / "lock").unlink(missing_ok=True)
    state["status"] = "done"
    save_state(repo, state)
    plan = repo.plan_file(state["id"])
    plan.write_text(plan.read_text().replace("Status: active.", "Status: done.", 1))
    return {"finished": state["id"], "removed_refs": len(refs)}


def cmd_strip(repo, args):
    """Strip WHY lines from the given files in place. For manual use and fallbacks."""
    notes = []
    for name in args.files:
        path = Path(name)
        new_text, found = strip_text(path.read_text())
        if found:
            path.write_text(new_text)
            notes += [{"file": name, "line": line, "why": why} for line, why in found]
    return {"notes": notes}


def main(argv=None):
    parser = argparse.ArgumentParser(prog="relay.py")
    parser.add_argument("--plan", help="plan id; defaults to the active plan for the current branch")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("init"); p.add_argument("slug"); p.add_argument("title")
    p = sub.add_parser("set-commits"); p.add_argument("titles", nargs="+")
    for name in ("snapshot", "building", "wt-commit", "bring"):
        p = sub.add_parser(name); p.add_argument("n", type=int)
    for name in ("finalize", "status", "unlock", "checks", "finish"):
        sub.add_parser(name)
    p = sub.add_parser("lock"); p.add_argument("--force", action="store_true")
    p = sub.add_parser("strip"); p.add_argument("files", nargs="+")
    args = parser.parse_args(argv)
    handler = globals()["cmd_" + args.cmd.replace("-", "_")]
    try:
        result = handler(Repo(), args)
    except RelayError as err:
        print(json.dumps({"error": str(err)}))
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
