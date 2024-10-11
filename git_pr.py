"""
git_pr.py

This module provides a class for managing GitHub Pull Requests (PRs).
The `GitPR` class includes methods for creating branches, getting commit 
details, creating revert commits, and creating pull requests for reverting 
previous merges.

Dependencies:
- requests: For making HTTP requests to the GitHub API.
- os: For accessing environment variables.

Usage Example:
    from git_pr import GitPR

    # Create an instance of GitPR
    git_pr = GitPR()

    # Create a new branch based on an existing branch
    git_pr.create_branch(base_branch='main', new_branch_name='feature-branch')

    # Get details of a specific commit
    commit_details = git_pr.get_commit(commit_sha='abcd1234')

    # Create a revert commit for a given merge commit
    revert_sha = git_pr.create_revert_commit(merge_commit=commit_details)

    # Create a pull request for the revert commit
    git_pr.create_pull_request(new_branch_name='revert-branch', 
                                base_branch='main', 
                                revert_message='Revert previous merge commit.')

"""

import os
import requests

class GitPR:
    token = ''
    repo_owner = ''
    repo_name = ''
    commit_sha = ''
    headers = {}

    def __init__(self) -> None:
        self.token = os.getenv("GH_TOKEN")
        self.repo_owner = os.getenv("REPO_OWNER")
        self.repo_name = os.getenv("REPO_NAME")
        self.commit_sha = os.getenv("COMMIT_SHA")
        
        # Set headers for authentication
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }


    def create_branch(self, base_branch, new_branch_name):
        # Get the latest commit on the base branch
        url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/git/ref/heads/{base_branch}"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            sha = response.json()["object"]["sha"]
        else:
            raise Exception(f"Failed to get branch details: {response.text}")

        # Create the new branch
        url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/git/refs"
        data = {
            "ref": f"refs/heads/{new_branch_name}",
            "sha": sha
        }
        response = requests.post(url, json=data, headers=self.headers)
        if response.status_code != 201:
            raise Exception(f"Failed to create branch: {response.text}")

    def get_commit(self, commit_sha):

        url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/commits/{commit_sha}"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to get commit details: {response.text}")

    def create_revert_commit(self, merge_commit):
        # Prepare the revert commit
        revert_commit_message = f"Revert: {merge_commit['commit']['message']}"
        data = {
            "message": revert_commit_message,
            "parents": [merge_commit['sha']],
            "tree": merge_commit['commit']['tree']['sha']
        }

        # Create the revert commit
        url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/git/commits"
        response = requests.post(url, json=data, headers=self.headers)
        if response.status_code == 201:
            return response.json()["sha"]
        else:
            raise Exception(f"Failed to create revert commit: {response.text}")

    def create_pull_request(self, new_branch_name, base_branch, revert_message):
        url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/pulls"
        data = {
            "title": revert_message,
            "head": new_branch_name,
            "base": base_branch,
            "body": "This pull request reverts a previous merge."
        }
        response = requests.post(url, json=data, headers=self.headers)
        if response.status_code == 201:
            print(f"Revert PR created: {response.json()['html_url']}")
        else:
            raise Exception(f"Failed to create pull request: {response.text}")

    def revert(self):
        merge_commit = self.get_commit(self.commit_sha)

        # Create a new branch for the revert
        new_branch_name = f"revert-{self.commit_sha[:7]}"
        base_branch = "main"  # Assuming you want to revert on the main branch
        self.create_branch(base_branch, new_branch_name)

        # Create the revert commit
        revert_commit_sha = self.create_revert_commit(merge_commit)

        # Create the pull request for the revert
        revert_message = f"Revert merge: {merge_commit['commit']['message']}"
        self.create_pull_request(new_branch_name, base_branch, revert_message)

