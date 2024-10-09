import os
import subprocess
import queue
import time

# Initialize a queue for files to be deployed
file_queue = queue.Queue()

# Function to push a page and retry if necessary
def deploy_page(page, sync_flags, max_retries=3):
    retries = 0
    while retries < max_retries:
        try:
            print(f"Deploying page: {page}")
            # Command construction similar to: sf skuid page push "${syncFlags[@]}" "./skuidpages/$page"
            command = ["sf", "skuid", "page", "push"] + sync_flags + [f"./skuidpages/{page}"]
            result = subprocess.run(command, check=True, capture_output=True)
            print(result.stdout.decode())  # Print command output
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error deploying {page}: {e.stderr.decode()}")
            retries += 1
            print(f"Retrying... ({retries}/{max_retries})")
            time.sleep(1)  # Optional delay before retrying

    print(f"Failed to deploy {page} after {max_retries} retries")
    return False

# Function to process all pages in the queue
def process_queue(sync_flags):
    while not file_queue.empty():
        page = file_queue.get()
        success = deploy_page(page, sync_flags)
        if not success:
            print(f"Page {page} could not be deployed after retries.")
        file_queue.task_done()

# Main logic to handle changed files
def main():
    # Get environment variables
    all_changed_files = os.getenv('ALL_CHANGED_FILES', '')  # Get the changed files
    target_username_alias = os.getenv('TARGET_USERNAME_ALIAS', '')  # Get the target username

    sync_flags = []
    if target_username_alias:
        sync_flags.append(f'--targetusername={target_username_alias}')

    # Process files from ALL_CHANGED_FILES
    if all_changed_files:
        files_array = all_changed_files.split()
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
                file_queue.put(page)  # Add pages to the queue
            process_queue(sync_flags)  # Process the queue
        else:
            print("No pages to deploy.")
    else:
        print("No changed files detected.")

if __name__ == "__main__":
    main()