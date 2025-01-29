import os
from dotenv import load_dotenv
import requests
import json
import time
from urllib.parse import quote

# Load environment variables
load_dotenv()

class GitLabDownloader:
    def __init__(self):
        # Get configuration from environment variables
        self.token = os.getenv('GITLAB_TOKEN')
        self.project_id = os.getenv('GITLAB_PROJECT_ID')
        self.branch = os.getenv('GITLAB_BRANCH', 'main')
        
        if not all([self.token, self.project_id]):
            raise ValueError("Missing required environment variables. Please check your .env file")
            
        self.headers = {'PRIVATE-TOKEN': self.token}
        self.base_url = f"https://gitlab.com/api/v4/projects/{self.project_id}"
    
    def fetch_markdown_files(self, folder_path=""):
        """
        Fetches markdown files from a GitLab repository recursively.
        """
        docs_content = {}
        
        # URL encode the folder path for API request
        encoded_path = quote(folder_path, safe='')
        tree_url = f"{self.base_url}/repository/tree?path={encoded_path}&ref={self.branch}"
        
        try:
            response = requests.get(tree_url, headers=self.headers)
            response.raise_for_status()  # Raise exception for non-200 status codes
            
            files = response.json()
            
            for file_info in files:
                file_path = os.path.join(folder_path, file_info['name']) if folder_path else file_info['name']
                
                if file_info['type'] == 'tree':
                    # Recursively process subdirectories
                    docs_content.update(self.fetch_markdown_files(file_path))
                    
                elif file_info['name'].lower().endswith('.md'):
                    # Fetch markdown file content
                    content = self.fetch_file_content(file_path)
                    if content:
                        docs_content[file_path] = content
        
        except requests.exceptions.RequestException as e:
            print(f"Error fetching repository contents: {str(e)}")
            if hasattr(e.response, 'headers'):
                # Handle rate limiting
                if e.response.status_code == 429:  # Rate limit exceeded
                    reset_time = int(e.response.headers.get('RateLimit-Reset', 0))
                    wait_time = max(reset_time - int(time.time()), 0)
                    if wait_time > 0:
                        print(f"Rate limit reached. Waiting {wait_time} seconds...")
                        time.sleep(wait_time)
                        return self.fetch_markdown_files(folder_path)  # Retry after waiting
        
        return docs_content
    
    def fetch_file_content(self, file_path):
        """
        Fetches content of a specific file using GitLab API.
        """
        encoded_path = quote(file_path, safe='')
        file_url = f"{self.base_url}/repository/files/{encoded_path}/raw?ref={self.branch}"
        
        try:
            response = requests.get(file_url, headers=self.headers)
            response.raise_for_status()
            return response.text
        
        except requests.exceptions.RequestException as e:
            print(f"Error downloading file {file_path}: {str(e)}")
            return None

def save_documentation(content, output_file="documentation_content.json"):
    """
    Saves the documentation content to a JSON file.
    """
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(content, f, ensure_ascii=False, indent=4)
        print(f"\nSuccessfully saved data to {output_file}")
        return True
    except Exception as e:
        print(f"Error saving documentation: {str(e)}")
        return False

def main():
    try:
        # Initialize downloader
        downloader = GitLabDownloader()
        
        # Fetch markdown files
        print("Fetching markdown files from GitLab...")
        content = downloader.fetch_markdown_files()
        
        if content:
            # Save content
            if save_documentation(content):
                # Display preview of downloaded content
                print("\nPreview of downloaded content:")
                for file_path, file_content in content.items():
                    preview = file_content[:200] + "..." if len(file_content) > 200 else file_content
                    print(f"\nFile: {file_path}\n{'-'*40}\n{preview}\n")
        else:
            print("No content was downloaded. Please check your configuration and permissions.")
            
    except ValueError as e:
        print(f"Configuration error: {str(e)}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main()
