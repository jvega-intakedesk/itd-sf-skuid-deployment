"""
skuid_pages_deployer.py

This module provides a class for deploying Skuid pages to a Salesforce 
environment. The `SkuidPagesDeployer` class includes methods for handling 
the deployment process, managing API interactions with Salesforce, and 
logging the results of deployments.

Dependencies:
- requests: For making HTTP requests to the Salesforce API.
- os: For accessing environment variables.
- json: For handling JSON data.
- time: For implementing delays during deployment retries.

Usage Example:
    from skuid_pages_deployer import SkuidPagesDeployer

    # Create an instance of SkuidPagesDeployer
    deployer = SkuidPagesDeployer()

    # Deploy a specific Skuid page
    deployer.deploy_page(page='example_page')

    # Check the status of a deployment
    deployer.check_deployment_status(deployment_id='12345')

    # Handle potential errors during deployment
    try:
        deployer.deploy_page(page='error_page')
    except Exception as e:
        print(f"Deployment failed: {e}")

"""

import os
import subprocess
import queue
import time

class SkuidPagesDeployer:

    # Initialize a queue for files to be deployed
    file_queue = queue.Queue()
    sync_files = []
    all_changed_files = ''
    target_username_alias = ''

    # Max number of attempts to deploy a page
    MAX_RETRIES = 3
    
    def __init__(self) -> None:
        self.all_changed_files = os.getenv('ALL_CHANGED_FILES', '')  # Get the changed files
        self.target_username_alias = os.getenv('TARGET_USERNAME_ALIAS', '')  # Get the target username

        self.sync_flags = []
        if self.target_username_alias:
            self.sync_flags.append(f'--targetusername={self.target_username_alias}')

    # Function to push a page and retry if necessary
    def deploy_page(self, page):
        retries = 0
        while retries < self.MAX_RETRIES:
            try:
                print(f"Deploying page: {page}")
                # Command construction similar to: sf skuid page push "${syncFlags[@]}" "./skuidpages/$page"
                command = ["sf", "skuid", "page", "push"] + self.sync_flags + [f"./skuidpages/{page}"] # similar to array merge
                
                # The subprocess.run will split the command array in pieces as first the command and then arguments
                result = subprocess.run(command, check=True, capture_output=True)
                print(result.stdout.decode())  # Print command output

                return True
            except subprocess.CalledProcessError as e:
                retries += 1
                print(f"Error deploying {page}: {e.stderr.decode()}")
                print(f"Retrying... ({retries}/{self.MAX_RETRIES})")
                time.sleep(1)  # Optional delay before retrying
            except Exception as e:
                retries += 1

                # Attempt to decode stderr if it exists; otherwise, use a generic message
                error_message = e.stderr.decode() if hasattr(e, 'stderr') else str(e)
                print(f"Error deploying {page}: {error_message}")
                print(f"Retrying... ({retries}/{self.MAX_RETRIES})")

                # Optional delay before retrying
                time.sleep(1)

        print(f"Failed to deploy {page} after {self.MAX_RETRIES} retries")
        return False

    # Function to process all pages in the queue
    def process_queue(self):
        while not self.file_queue.empty():
            page = self.file_queue.get()
            success = self.deploy_page(page)
            if not success:
                self.file_queue.task_done()
                raise Exception(f"Page {page} could not be deployed after retries.")
            else:
                self.file_queue.task_done()

    # Main logic to handle changed files
    def deploy(self):
        # Process files from ALL_CHANGED_FILES
        if self.all_changed_files:
            files_array = self.all_changed_files.split()
            deploy = False
            pages = []

            # Iterate over each changed file
            for file in files_array:
                print(f"Processing file: {file}")
                if "skuidpages/" in file:
                    filename = os.path.basename(file)  # Extract file name
                    pages.append(filename)  # Add to pages list
                    deploy = True

            if deploy:
                print(f"Deploying {len(pages)} pages.")
                for page in pages:
                    self.file_queue.put(page)  # Add pages to the queue
                self.process_queue()  # Process the queue
            else:
                print("No pages found to be deployed.")
                raise Exception("No pages found to be deployed.")
        else:
            print("No changed files detected.")
            raise Exception("No changed files detected.")