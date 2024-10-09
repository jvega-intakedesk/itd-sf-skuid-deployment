"""
deploy_skuid_pages.py

This module contains the SkuidPagesDeployer class, which is responsible for
deploying Skuid pages to a GitHub repository. It handles operations such as 
creating branches, commits, and pull requests for reverting changes.

Usage:
    deployer = SkuidPagesDeployer(token="your_token", repo_owner="owner", repo_name="repo")
    deployer.deploy_page(page="your_page")
"""

import os
import subprocess
import queue
import time
import requests

from skuid_pages_deployer import SkuidPagesDeployer
from git_pr import GitPR

# Main entry point
def main():
    try:
        (SkuidPagesDeployer()).deploy()
    except Exception as e:
        print(f"Error occurred: {e}. Creating a revert PR...")
        (GitPR()).revert()

if __name__ == "__main__":
    main()
