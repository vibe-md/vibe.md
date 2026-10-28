"""Guards for the security properties of the GitHub Actions workflows.

These read the workflow files; they do not run GitHub Actions. They keep the
publishing credentials away from pull requests and away from repository code.
"""

import unittest
from pathlib import Path

import yaml

WORKFLOWS = Path(__file__).resolve().parents[1] / ".github" / "workflows"


def load(name):
    data = yaml.safe_load((WORKFLOWS / name).read_text())
    data["on"] = data.pop(True, data.get("on"))  # YAML reads a bare `on:` as the boolean True
    return data


class PublishWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.workflow = load("publish.yml")
        self.job = self.workflow["jobs"]["publish"]
        self.steps = self.job["steps"]

    def test_it_never_runs_for_pull_requests(self):
        self.assertEqual(set(self.workflow["on"]), {"push", "workflow_dispatch"})
        self.assertEqual(self.workflow["on"]["push"]["branches"], ["main"])

    def test_it_only_runs_on_the_trusted_branch_of_the_real_repository(self):
        condition = self.job["if"]
        self.assertIn("github.ref == 'refs/heads/main'", condition)
        self.assertIn("github.repository == 'vibe-md/vibe.md'", condition)

    def test_write_access_is_limited_to_the_publish_job(self):
        self.assertEqual(self.workflow["permissions"], {"contents": "read"})
        self.assertEqual(self.job["permissions"], {"contents": "write"})

    def test_the_token_is_not_available_to_the_whole_job(self):
        self.assertNotIn("GH_TOKEN", self.job.get("env", {}))
        self.assertNotIn("GITHUB_TOKEN", self.job.get("env", {}))

    def test_steps_that_run_repository_code_never_receive_the_token(self):
        for step in self.steps:
            run = step.get("run", "")
            runs_repo_code = any(word in run for word in ("python ", "unittest", "scripts/"))
            if runs_repo_code:
                with self.subTest(step=step.get("name")):
                    self.assertNotIn("GH_TOKEN", step.get("env", {}))
                    self.assertNotIn("secrets.", str(step.get("env", {})))

    def test_only_steps_that_call_the_github_api_receive_the_token(self):
        for step in self.steps:
            if "GH_TOKEN" in step.get("env", {}):
                with self.subTest(step=step.get("name")):
                    self.assertIn("gh ", step["run"])

    def test_the_deploy_hook_secret_is_only_given_to_the_step_that_uses_it(self):
        holders = [step.get("name") for step in self.steps if "secrets." in str(step.get("env", {}))]
        self.assertEqual(holders, ["Rebuild the website"])

    def test_every_action_is_pinned_to_a_full_commit_sha(self):
        for step in self.steps:
            if "uses" in step:
                with self.subTest(action=step["uses"]):
                    self.assertRegex(step["uses"], r"@[0-9a-f]{40}$")

    def test_checkout_does_not_persist_credentials(self):
        checkout = next(step for step in self.steps if step.get("uses", "").startswith("actions/checkout"))
        self.assertIs(checkout["with"]["persist-credentials"], False)

    def test_releases_are_published_only_after_every_check_and_build_step(self):
        names = [step.get("name") for step in self.steps]
        publish = names.index("Publish the release")
        for before in ("Validate and test the merged commit", "Build every package and the catalog",
                       "Verify the catalog against the source"):
            self.assertLess(names.index(before), publish)


class ValidationWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.workflow = load("validate-skills.yml")

    def test_it_uses_pull_request_not_pull_request_target(self):
        self.assertIn("pull_request", self.workflow["on"])
        self.assertNotIn("pull_request_target", self.workflow["on"])

    def test_it_is_read_only_and_uses_no_secrets(self):
        self.assertEqual(self.workflow["permissions"], {"contents": "read"})
        for job in self.workflow["jobs"].values():
            self.assertNotIn("permissions", job)
        self.assertNotIn("secrets.", (WORKFLOWS / "validate-skills.yml").read_text())


if __name__ == "__main__":
    unittest.main()
