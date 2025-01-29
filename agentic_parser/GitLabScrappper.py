import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

gapi_key = os.getenv("GEMINI_API_KEY")

# GitHub repository base URL loaded from .env file
GITLAB_REPO_BASE = os.getenv("GITLAB_REPO_BASE")  # Root repository URL

# Custom Tool to Fetch Markdown Files from GitHub Repository
def fetch_markdown_files(repo_url: str, folder_path=""):
    """
    Fetches markdown files from a GitHub repository and returns structured content.
    
    Args:
        repo_url (str): GitHub API URL to fetch the list of files.
        folder_path (str): Current directory path to fetch the files from (used for recursion).
        
    Returns:
        dict: A dictionary with filenames as keys and their content as values.
    """
    docs_content = {}
    
    # Construct the GitHub API URL to list files in the current folder
    current_repo_url = f"{repo_url}/contents/{folder_path}" if folder_path else f"{repo_url}/contents"
    
    response = requests.get(current_repo_url)
    
    # Check for successful response
    if response.status_code != 200:
        raise Exception(f"Failed to fetch files from GitLab: {response.status_code} - {response.text}")
    
    files = response.json()
    
    for file_info in files:
        # If it's a directory, recursively call the function to process that folder
        if file_info['type'] == 'dir':
            new_folder_path = os.path.join(folder_path, file_info['name']) if folder_path else file_info['name']
            docs_content.update(fetch_markdown_files(repo_url, new_folder_path))
        
        # If it's a markdown file, download it
        elif file_info['name'].endswith(".md"):
            file_name = file_info['name']
            file_url = file_info['download_url']
            
            try:
                file_response = requests.get(file_url)
                if file_response.status_code == 200:
                    docs_content[file_name] = file_response.text
                else:
                    docs_content[file_name] = f"Error downloading file: {file_response.status_code}"
            except Exception as e:
                docs_content[file_name] = f"Error reading file: {e}"
    
    return docs_content

# Fetch markdown content from the GitHub repository
documentation_content = fetch_markdown_files(GITLAB_REPO_BASE)

# Display extracted documentation content for verification
print("\nExtracted Documentation Content:")
for file, content in documentation_content.items():
    print(f"\nFile: {file}\n{'-'*40}\n{content[:1000]}...\n")  # Print first 1000 chars of each file
