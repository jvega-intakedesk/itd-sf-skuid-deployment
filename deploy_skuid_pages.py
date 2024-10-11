"""
deploy_skuid_pages.py

This module contains the SkuidPagesDeployer and the GitPR classes. The first is responsible for deploying pages to a 
Salesforce environment using the Saleforce Skuid Plugin. The latter is responsible for creating a PR of the 
current commit being merged into the main branch  in cases where a failure occurred.

Dependencies:
- requests: For making HTTP requests to the Salesforce API.
- os: For accessing environment variables.
- subprocess: For executing the sales force skuid plugin
- time: For implementing delays during deployment retries.

Usage:
    try:
        (SkuidPagesDeployer()).deploy()
    except Exception as e:
        print(f"Error occurred: {e}. Creating a revert PR...")
        (GitPR()).revert()
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
