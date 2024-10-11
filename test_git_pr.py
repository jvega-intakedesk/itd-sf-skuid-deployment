import os
import unittest
from unittest.mock import patch, MagicMock
import requests

from git_pr import GitPR

class TestGitPR(unittest.TestCase):
    def setUp(self):
        # Set up environment variables
        os.environ["GITHUB_TOKEN"] = "fake_token"
        os.environ["REPO_OWNER"] = "fake_owner"
        os.environ["REPO_NAME"] = "fake_repo"
        os.environ["COMMIT_SHA"] = "fake_commit_sha"

        self.git_pr = GitPR()

    @patch('requests.get')
    def test_create_branch_success(self, mock_get):
        # Mock the response for the base branch
        mock_get.return_value = MagicMock(status_code=200)
        mock_get.return_value.json.return_value = {"object": {"sha": "fake_sha"}}

        with patch('requests.post') as mock_post:
            mock_post.return_value = MagicMock(status_code=201)

            self.git_pr.create_branch("main", "new_branch")

            # Assert that the correct post request was made
            mock_post.assert_called_once_with(
                "https://api.github.com/repos/fake_owner/fake_repo/git/refs",
                json={"ref": "refs/heads/new_branch", "sha": "fake_sha"},
                headers=self.git_pr.headers
            )

    @patch('requests.get')
    def test_create_branch_failure(self, mock_get):
        # Mock a failure response for the base branch
        mock_get.return_value = MagicMock(status_code=404, text='Not Found')

        with self.assertRaises(Exception) as context:
            self.git_pr.create_branch("main", "new_branch")
        
        self.assertIn("Failed to get branch details:", str(context.exception))

    @patch('requests.get')
    def test_get_commit_success(self, mock_get):
        mock_get.return_value = MagicMock(status_code=200)
        mock_get.return_value.json.return_value = {"sha": "fake_sha", "commit": {"message": "Commit message"}}

        commit = self.git_pr.get_commit("fake_commit_sha")
        self.assertEqual(commit["sha"], "fake_sha")

    @patch('requests.get')
    def test_get_commit_failure(self, mock_get):
        mock_get.return_value = MagicMock(status_code=404, text='Not Found')

        with self.assertRaises(Exception) as context:
            self.git_pr.get_commit("fake_commit_sha")

        self.assertIn("Failed to get commit details:", str(context.exception))

    @patch('requests.post')
    def test_create_revert_commit_success(self, mock_post):
        mock_post.return_value = MagicMock(status_code=201)
        mock_post.return_value.json.return_value = {"sha": "new_revert_sha"}

        merge_commit = {"commit": {"message": "Commit message", "tree": {"sha": "tree_sha"}}, "sha": "merge_sha"}
        revert_sha = self.git_pr.create_revert_commit(merge_commit)

        self.assertEqual(revert_sha, "new_revert_sha")

    @patch('requests.post')
    def test_create_revert_commit_failure(self, mock_post):
        mock_post.return_value = MagicMock(status_code=400, text='Bad Request')

        merge_commit = {"commit": {"message": "Commit message", "tree": {"sha": "tree_sha"}}, "sha": "merge_sha"}

        with self.assertRaises(Exception) as context:
            self.git_pr.create_revert_commit(merge_commit)

        self.assertIn("Failed to create revert commit:", str(context.exception))

    @patch('requests.post')
    def test_create_pull_request_success(self, mock_post):
        mock_post.return_value = MagicMock(status_code=201)
        mock_post.return_value.json.return_value = {"html_url": "https://github.com/fake_repo/pulls/1"}

        self.git_pr.create_pull_request("new_branch", "main", "Revert message")

        mock_post.assert_called_once_with(
            "https://api.github.com/repos/fake_owner/fake_repo/pulls",
            json={
                "title": "Revert message",
                "head": "new_branch",
                "base": "main",
                "body": "This pull request reverts a previous merge."
            },
            headers=self.git_pr.headers
        )

    @patch('requests.post')
    def test_create_pull_request_failure(self, mock_post):
        mock_post.return_value = MagicMock(status_code=400, text='Bad Request')

        with self.assertRaises(Exception) as context:
            self.git_pr.create_pull_request("new_branch", "main", "Revert message")

        self.assertIn("Failed to create pull request:", str(context.exception))


if __name__ == '__main__':
    unittest.main()
