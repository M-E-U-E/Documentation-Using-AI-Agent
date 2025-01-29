import requests
import urllib.parse
from typing import Dict, List, Optional
import json
from datetime import datetime
import os

class GitLabRAGProcessor:
    def __init__(self, repo_url: str, output_dir: str = "rag_data"):
        """
        Initialize the RAG processor with a public GitLab repository URL.
        
        Args:
            repo_url (str): Full URL to the GitLab repository
            output_dir (str): Directory to store the processed RAG data
        """
        self.repo_url = repo_url.rstrip('/')
        self.output_dir = output_dir
        
        # Extract repository information
        parts = self.repo_url.split('gitlab.com/')[-1].split('/')
        if len(parts) < 2:
            raise ValueError("Invalid GitLab repository URL")
            
        self.namespace = '/'.join(parts[:-1])
        self.project_name = parts[-1]
        self.api_url = f"https://gitlab.com/api/v4/projects/{urllib.parse.quote(f'{self.namespace}/{self.project_name}', safe='')}"
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

    def fetch_project_info(self) -> Optional[dict]:
        """Fetch basic project information."""
        try:
            response = requests.get(self.api_url)
            if response.status_code == 200:
                return response.json()
            print(f"Warning: Could not fetch project info. Status code: {response.status_code}")
            return {
                'name': self.project_name,
                'description': None,
                'web_url': self.repo_url,
                'default_branch': 'main'
            }
        except Exception as e:
            print(f"Warning: Error fetching project info: {e}")
            return {
                'name': self.project_name,
                'description': None,
                'web_url': self.repo_url,
                'default_branch': 'main'
            }

    def fetch_markdown_files(self, project_id: int, path: str = "") -> List[Dict[str, str]]:
        """
        Recursively fetch all markdown files.
        
        Returns:
            List[Dict]: List of dictionaries containing file info and content
        """
        files_data = []
        tree_url = f"https://gitlab.com/api/v4/projects/{project_id}/repository/tree"
        params = {"path": path} if path else {}
        
        try:
            response = requests.get(tree_url, params=params)
            response.raise_for_status()
            items = response.json()
            
            for item in items:
                item_path = f"{path}/{item['name']}" if path else item['name']
                
                if item['type'] == 'tree':
                    # Recursively process directories
                    files_data.extend(self.fetch_markdown_files(project_id, item_path))
                    
                elif item['type'] == 'blob' and item['name'].endswith('.md'):
                    # Fetch file content
                    content = self.fetch_file_content(project_id, item_path)
                    if content:
                        files_data.append({
                            'path': item_path,
                            'content': content,
                            'title': self.extract_title(content) or item['name']
                        })
            
            return files_data
            
        except Exception as e:
            print(f"Error fetching files: {e}")
            return files_data

    def fetch_file_content(self, project_id: int, file_path: str) -> Optional[str]:
        """Fetch content of a specific file."""
        encoded_path = urllib.parse.quote(file_path, safe='')
        url = f"https://gitlab.com/api/v4/projects/{project_id}/repository/files/{encoded_path}/raw"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Error downloading {file_path}: {e}")
            return None

    def extract_title(self, content: str) -> Optional[str]:
        """Extract title from markdown content."""
        lines = content.split('\n')
        for line in lines:
            # Look for # or ## headers
            if line.startswith('# '):
                return line.replace('# ', '').strip()
            if line.startswith('## '):
                return line.replace('## ', '').strip()
        return None

    def process_for_rag(self) -> bool:
        """
        Process repository content into RAG-friendly format.
        
        Returns:
            bool: True if processing was successful
        """
        try:
            # Fetch project information
            project_info = self.fetch_project_info()
            project_id = project_info.get('id')
            
            if not project_id:
                print("Warning: Could not get project ID, trying with URL path...")
                project_id = urllib.parse.quote(f'{self.namespace}/{self.project_name}', safe='')
            
            # Fetch all markdown files
            print("Fetching markdown files...")
            markdown_files = self.fetch_markdown_files(project_id)
            
            if not markdown_files:
                print("No markdown files found in the repository")
                return False
            
            # Prepare RAG document
            rag_document = {
                'project_info': {
                    'name': project_info['name'],
                    'url': project_info['web_url'],
                    'processed_date': datetime.now().isoformat()
                },
                'documents': []
            }
            
            # Process each markdown file
            for file_data in markdown_files:
                document = {
                    'title': file_data['title'],
                    'content': file_data['content'],
                    'source_file': file_data['path'],
                    'repository': self.repo_url
                }
                rag_document['documents'].append(document)
            
            # Save processed data
            output_path = os.path.join(self.output_dir, 'rag_processed.json')
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(rag_document, f, ensure_ascii=False, indent=2)
            
            print(f"\nSuccessfully processed {len(markdown_files)} markdown files")
            print(f"RAG document saved to: {output_path}")
            
            # Print found documents
            print("\nProcessed files:")
            for doc in rag_document['documents']:
                print(f"- {doc['source_file']}")
            
            return True
            
        except Exception as e:
            print(f"Error processing repository: {e}")
            return False

def main():
    repo_url = "https://gitlab.com/Shino-01/testrepocrawler"  # Replace with actual repository URL
    
    try:
        processor = GitLabRAGProcessor(repo_url)
        success = processor.process_for_rag()
        
        if success:
            print("\nRepository successfully processed for RAG")
        else:
            print("\nFailed to process repository")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()