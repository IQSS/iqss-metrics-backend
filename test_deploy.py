from pathlib import Path
import subprocess
import tempfile
import unittest


class DeployTests(unittest.TestCase):
    def test_new_file_is_pushed_and_unchanged_rerun_succeeds(self):
        makefile = Path(__file__).resolve().parent / "Makefile"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            remote = root / "remote.git"
            dashboard = root / "dashboard"

            def run(*command, cwd=root):
                return subprocess.run(command, cwd=cwd, check=True, capture_output=True, text=True).stdout

            run("git", "init", "--bare", "--initial-branch=master", str(remote))
            run("git", "init", "--initial-branch=master", str(dashboard))
            run("git", "config", "user.name", "Test", cwd=dashboard)
            run("git", "config", "user.email", "test@example.org", cwd=dashboard)
            run("git", "config", "commit.gpgsign", "false", cwd=dashboard)
            (dashboard / "README").write_text("Test dashboard\n")
            run("git", "add", "README", cwd=dashboard)
            run("git", "commit", "-m", "Initial", cwd=dashboard)
            run("git", "remote", "add", "origin", str(remote), cwd=dashboard)
            data = dashboard / "assets" / "data"
            data.mkdir(parents=True)
            (root / "out").symlink_to(data, target_is_directory=True)
            (data / "dataverse-pm-metrics.tsv").write_text("date\trt_new\n2026-10-14\t1\n")
            run("make", "-f", str(makefile), "deploy")
            published = run("git", "--git-dir", str(remote), "show", "master:assets/data/dataverse-pm-metrics.tsv")
            self.assertIn("2026-10-14\t1", published)
            before = run("git", "rev-parse", "HEAD", cwd=dashboard)
            result = run("make", "-f", str(makefile), "deploy")
            self.assertIn("No changes to data.", result)
            self.assertEqual(run("git", "rev-parse", "HEAD", cwd=dashboard), before)


if __name__ == "__main__":
    unittest.main()
