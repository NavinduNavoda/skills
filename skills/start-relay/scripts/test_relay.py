"""Tests for relay.py. Run: python3 -m unittest test_relay.py (from this folder).

StripTextTests
- test_strips_each_comment_syntax: removes WHY lines in //, #, --, /* */, <!-- --> and {/* */} forms
- test_reports_line_of_code_below: notes point at the code line in the stripped text
- test_keeps_non_why_comments: ordinary comments and WHY inside strings stay

FlowTests
- test_init_refuses_dirty_tree: init stops when the working folder has changes
- test_unchanged_review_applies_next_cleanly: no user edits, next commit applies with no conflicts
- test_why_only_edits_count_as_unchanged: editing or deleting WHY lines is not a change
- test_code_edit_is_detected_and_diffed: a code edit sets changed and writes a diff without WHY lines
- test_user_commit_gets_why_cleanup_commit: a manual commit with WHY lines gets a chore follow-up commit
- test_adr_commit_during_review_is_not_a_change: an ADR committed on its own leaves detection and the next patch alone
- test_two_branches_have_separate_plans: plans on two worktrees of one repo stay apart
- test_finish_removes_worktree_branch_and_refs: finish cleans up and marks the plan done
- test_lock_blocks_second_session: a fresh lock refuses a second lock without --force
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import relay  # noqa: E402

RELAY = str(Path(__file__).parent / "relay.py")


def sh(cwd, *args):
    return subprocess.run(args, cwd=cwd, check=True, capture_output=True, text=True).stdout


def relay_cmd(cwd, *args, ok=True):
    result = subprocess.run([sys.executable, RELAY, *args], cwd=cwd, capture_output=True, text=True)
    data = json.loads(result.stdout)
    if ok:
        assert result.returncode == 0, data
    return data


class StripTextTests(unittest.TestCase):
    def test_strips_each_comment_syntax(self):
        text = "\n".join([
            "  // WHY: a", "x", "# WHY: b", "y", "-- WHY: c", "z",
            "/* WHY: d */", "w", "<!-- WHY: e -->", "v", "{/* WHY: f */}", "u", "",
        ])
        out, notes = relay.strip_text(text)
        self.assertEqual(out, "x\ny\nz\nw\nv\nu\n")
        self.assertEqual([w for _, w in notes], ["a", "b", "c", "d", "e", "f"])

    def test_reports_line_of_code_below(self):
        out, notes = relay.strip_text("a\n// WHY: one\n// WHY: two\nb\nc\n# WHY: three\nd\n")
        self.assertEqual(out, "a\nb\nc\nd\n")
        self.assertEqual(notes, [(2, "one"), (2, "two"), (4, "three")])

    def test_keeps_non_why_comments(self):
        text = '// normal\nconst s = "// WHY: in a string";\n# why lowercase\n'
        self.assertEqual(relay.strip_text(text), (text, []))


class FlowTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name) / "app"
        self.repo.mkdir()
        sh(self.repo, "git", "init", "-q", "-b", "main")
        sh(self.repo, "git", "config", "user.email", "t@example.com")
        sh(self.repo, "git", "config", "user.name", "Test")
        self.write("src/a.ts", "export const a = 1;\n")
        self.write(".gitignore", ".env\n")
        self.write(".env", "SECRET=1\n")
        sh(self.repo, "git", "add", "-A")
        sh(self.repo, "git", "commit", "-qm", "init")
        sh(self.repo, "git", "switch", "-qc", "feat/x")

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, name, text, root=None):
        path = (root or self.repo) / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def start(self):
        info = relay_cmd(self.repo, "init", "x", "Feature X")
        relay_cmd(self.repo, "set-commits", "feat: add b", "feat: add c")
        self.write("src/b.ts", "// WHY: chose const over let because b never changes\nexport const b = 2;\n")
        relay_cmd(self.repo, "snapshot", "1")
        wt = Path(info["worktree"])
        relay_cmd(self.repo, "building", "2")
        self.write("src/c.ts", "// WHY: c reuses b, chose import over copy\nimport { b } from './b';\nexport const c = b + 1;\n", root=wt)
        relay_cmd(self.repo, "--plan", info["id"], "wt-commit", "2")
        return info, wt

    def test_init_refuses_dirty_tree(self):
        self.write("src/a.ts", "export const a = 3;\n")
        self.assertIn("uncommitted", relay_cmd(self.repo, "init", "x", "X", ok=False)["error"])

    def test_unchanged_review_applies_next_cleanly(self):
        info, wt = self.start()
        self.assertEqual((wt / ".env").read_text(), "SECRET=1\n")
        self.assertFalse((wt / "src/b.ts").read_text().startswith("// WHY"))
        result = relay_cmd(self.repo, "finalize")
        self.assertFalse(result["changed"])
        self.assertEqual(result["commit_message"], "feat: add b")
        self.assertEqual(result["next"]["status"], "built")
        self.assertEqual(relay_cmd(self.repo, "bring", "2")["applied"], "clean")
        self.assertIn("// WHY: c reuses b", (self.repo / "src/c.ts").read_text())
        self.assertNotIn("WHY", (self.repo / "src/b.ts").read_text())
        plan = Path(info["plan"]).read_text()
        self.assertIn("`src/b.ts:1`: chose const over let", plan)
        self.assertIn("1. feat: add b (done)", plan)

    def test_why_only_edits_count_as_unchanged(self):
        self.start()
        self.write("src/b.ts", "// WHY: reworded by the user\nexport const b = 2;\n")
        self.assertFalse(relay_cmd(self.repo, "finalize")["changed"])

    def test_code_edit_is_detected_and_diffed(self):
        self.start()
        self.write("src/b.ts", "// WHY: chose const over let because b never changes\nexport const bee = 2;\n")
        result = relay_cmd(self.repo, "finalize")
        self.assertTrue(result["changed"])
        diff = Path(result["user_diff"]).read_text()
        self.assertIn("+export const bee = 2;", diff)
        self.assertNotIn("WHY", diff)

    def test_user_commit_gets_why_cleanup_commit(self):
        self.start()
        sh(self.repo, "git", "add", "-A")
        sh(self.repo, "git", "commit", "-qm", "my own commit")
        result = relay_cmd(self.repo, "finalize")
        self.assertTrue(result["user_committed"])
        self.assertFalse(result["changed"])
        self.assertEqual(result["commit_message"], "chore: remove WHY comments")

    def test_adr_commit_during_review_is_not_a_change(self):
        self.start()
        self.write("docs/adr/0001-use-const.md", "# 1. Use const\n")
        sh(self.repo, "git", "add", "docs/adr")
        sh(self.repo, "git", "commit", "-qm", "docs: add ADR 0001", "--", "docs/adr")
        result = relay_cmd(self.repo, "finalize")
        self.assertFalse(result["changed"])
        self.assertFalse(result["user_committed"])
        self.assertEqual(result["commit_message"], "feat: add b")
        self.assertEqual(relay_cmd(self.repo, "bring", "2")["applied"], "clean")
        self.assertTrue((self.repo / "docs/adr/0001-use-const.md").exists())

    def test_two_branches_have_separate_plans(self):
        self.start()
        other = Path(self.tmp.name) / "app-y"
        sh(self.repo, "git", "worktree", "add", "-q", "-b", "feat/y", str(other), "main")
        info_y = relay_cmd(other, "init", "y", "Feature Y")
        self.assertEqual(info_y["id"], "001-y")
        self.assertEqual(relay_cmd(other, "status")["plan"], "001-y")
        self.assertEqual(relay_cmd(self.repo, "status")["plan"], "000-x")

    def test_finish_removes_worktree_branch_and_refs(self):
        info, wt = self.start()
        relay_cmd(self.repo, "finalize")
        relay_cmd(self.repo, "finish")
        self.assertFalse(wt.exists())
        self.assertEqual(sh(self.repo, "git", "branch", "--list", "relay/*"), "")
        self.assertEqual(sh(self.repo, "git", "for-each-ref", "refs/relay/"), "")
        self.assertIn("Status: done.", Path(info["plan"]).read_text())

    def test_lock_blocks_second_session(self):
        self.start()
        relay_cmd(self.repo, "lock")
        self.assertIn("in use", relay_cmd(self.repo, "lock", ok=False)["error"])
        relay_cmd(self.repo, "lock", "--force")
        relay_cmd(self.repo, "unlock")
        self.assertIsNone(relay_cmd(self.repo, "status")["locked"])


if __name__ == "__main__":
    unittest.main()
