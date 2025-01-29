import os
import requests
import json

# GitLab Project ID (replace with your project ID)
GITLAB_PROJECT_ID = 66617663  # Your GitLab project ID

# GitLab repository API URL (using the Project ID)
GITLAB_REPO_URL = f"https://gitlab.com/api/v4/projects/{GITLAB_PROJECT_ID}/repository/tree"

# Custom Tool to Fetch Markdown Files from GitLab Repository
def fetch_markdown_files_from_gitlab(repo_url: str, folder_path=""):
    """
    Fetches markdown files from a GitLab repository and returns structured content.
    
    Args:
        repo_url (str): GitLab API URL to fetch the list of files.
        folder_path (str): Current directory path to fetch the files from (used for recursion).
        
    Returns:
        dict: A dictionary with filenames as keys and their content as values.
    """
    docs_content = {}

    # Construct the GitLab API URL to list files in the current folder
    current_repo_url = f"{repo_url}?path={folder_path}" if folder_path else f"{repo_url}"
    print(f"Fetching contents from: {current_repo_url}")
    
    response = requests.get(current_repo_url)
    
    # Handle rate limiting if reached
    if response.status_code == 403:  # Rate limit error
        reset_time = response.headers.get('X-RateLimit-Reset')
        print(f"Rate limit reached, try again after: {reset_time}")
        return docs_content
    
    # Check for successful response
    if response.status_code != 200:
        raise Exception(f"Failed to fetch files from GitLab: {response.status_code} - {response.text}")
    
    files = response.json()
    
    for file_info in files:
        # If it's a directory, recursively call the function to process that folder
        if file_info['type'] == 'tree':  # If it's a directory in GitLab
            new_folder_path = os.path.join(folder_path, file_info['name']) if folder_path else file_info['name']
            docs_content.update(fetch_markdown_files_from_gitlab(repo_url, new_folder_path))
        
        # If it's a markdown file, download it
        elif file_info['name'].endswith(".md"):  # If it's a markdown file
            file_name = file_info['name']
            print(f"Downloading markdown file: {file_name}")
            file_raw_url = f"https://gitlab.com/{file_info['path']}/raw"  # GitLab raw file URL
            
            try:
                file_response = requests.get(file_raw_url)
                if file_response.status_code == 200:
                    docs_content[file_name] = file_response.text
                else:
                    docs_content[file_name] = f"Error downloading file: {file_response.status_code}"
            except Exception as e:
                docs_content[file_name] = f"Error reading file: {e}"
    
    return docs_content

# Fetch markdown content from the GitLab repository
documentation_content = fetch_markdown_files_from_gitlab(GITLAB_REPO_URL)

# Save the documentation content to a JSON file
json_file_path = "documentation_content.json"
with open(json_file_path, "w", encoding="utf-8") as json_file:
    json.dump(documentation_content, json_file, ensure_ascii=False, indent=4)

print(f"\nData has been saved to {json_file_path}")

# Optionally, display extracted content for verification
print("\nExtracted Documentation Content:")
for file, content in documentation_content.items():
    print(f"\nFile: {file}\n{'-'*40}\n{content}\n")  # Print all chars of each file
