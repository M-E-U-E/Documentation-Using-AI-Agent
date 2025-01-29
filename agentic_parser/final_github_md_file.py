import os
import requests
from dotenv import load_dotenv
import json
from crewai import Agent, Task, Crew

# Load environment variables
load_dotenv()

gapi_key = os.getenv("GEMINI_API_KEY")

# GitHub repository base URL loaded from .env file
GITHUB_REPO_BASE = os.getenv("GITHUB_REPO_BASE")  # Root repository URL

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
    print(f"Fetching contents from: {current_repo_url}")
    
    response = requests.get(current_repo_url)
    
    # Handle rate limiting if reached
    if response.status_code == 403:  # Rate limit error
        reset_time = response.headers.get('X-RateLimit-Reset')
        print(f"Rate limit reached, try again after: {reset_time}")
        return docs_content
    
    # Check for successful response
    if response.status_code != 200:
        raise Exception(f"Failed to fetch files from GitHub: {response.status_code} - {response.text}")
    
    files = response.json()
    
    for file_info in files:
        # If it's a directory, recursively call the function to process that folder
        if file_info['type'] == 'dir':
            new_folder_path = os.path.join(folder_path, file_info['name']) if folder_path else file_info['name']
            docs_content.update(fetch_markdown_files(repo_url, new_folder_path))
        
        # If it's a markdown file, download it
        elif file_info['name'].endswith(".md"):
            file_name = file_info['name']
            print(f"Downloading markdown file: {file_name}")
            file_url = file_info['download_url']
            
            try:
                file_response = requests.get(file_url)
                if file_response.status_code == 200:
                    docs_content[file_name] = file_response.text
                    # # Save to file locally
                    # with open(f"{file_name}", "w", encoding="utf-8") as f:
                    #     f.write(file_response.text)
                else:
                    docs_content[file_name] = f"Error downloading file: {file_response.status_code}"
            except Exception as e:
                docs_content[file_name] = f"Error reading file: {e}"
    
    return docs_content

# Fetch markdown content from the GitHub repository
documentation_content = fetch_markdown_files(GITHUB_REPO_BASE)
# Define Agents
crawler_agent = Agent(
    role="Documentation Crawler",
    goal="Extract and structure content from Markdown documentation files.",
    backstory="""You are an expert in reading and processing documentation files.
    Your task is to systematically scan all Markdown files and extract structured information.""",
    tools=[],
    verbose=True,
    memory=True,
    llm="gemini/gemini-1.5-flash-latest"
)

analyzer_agent = Agent(
    role="Content Analyzer",
    goal="Process and organize documentation content for efficient retrieval.",
    backstory="""You are an expert in analyzing technical documentation and creating structured knowledge bases.
    Your role is to process raw content, create summaries, and organize information in an easily searchable format.""",
    verbose=True,
    memory=True,
    llm="gemini/gemini-1.5-flash-latest"
)

user_assistant = Agent(
    role="Documentation Guide",
    goal="Help users understand and apply documentation effectively.",
    backstory="""You are an expert technical assistant who helps users navigate and understand documentation.
    You can break down complex problems into step-by-step solutions and provide clear, actionable guidance.""",
    verbose=True,
    memory=True,
    llm="gemini/gemini-1.5-flash-latest"
)

# Define Tasks
crawl_task = Task(
    description="""
    Read all markdown files from the documentation directory and extract structured information.
    Ensure that all files are read properly and store them in a structured format.
    """,
    expected_output="""
    A structured dictionary containing:
    - Extracted content from all markdown files.
    - Filenames mapped to their respective content.
    - Metadata for each file.
    - Error logs if any files failed to read.
    """,
    agent=crawler_agent,
    tools=[],  # No external tools needed
    verbose=True
)

analyze_task = Task(
    description="""
    1. Process the extracted documentation content.
    2. Generate summaries for each section.
    3. Create a searchable knowledge base.
    4. Identify key concepts and their relationships.
    5. Prepare content for user queries.
    """,
    expected_output="""
    A processed knowledge base containing:
    - Section summaries.
    - Key concepts and their definitions.
    - Relationship mappings between concepts.
    - Indexed content for quick search.
    - Metadata for content organization.
    """,
    agent=analyzer_agent,
    verbose=True
)

assist_task = Task(
    description="""
    1. Understand user {query} about the documentation and {user_context}.
    2. Search the processed knowledge base.
    3. Provide step-by-step solutions.
    4. Explain concepts clearly.
    5. Guide users through implementation.
    """,
    expected_output="""
    Clear and actionable responses including:
    - Direct answers to user {query}.
    - Step-by-step implementation of the answer.
    - Relevant documentation references.
    - Troubleshooting suggestions if needed.
    """,
    agent=user_assistant,
    verbose=True
)

# Updated embedder configuration
embedder_config = {
    "provider": "google",
    "config": {
        "api_key": gapi_key,
        "model": "models/embedding-001"
    }
}

# Create and configure the crew
crew = Crew(
    agents=[crawler_agent, analyzer_agent, user_assistant],
    tasks=[crawl_task, analyze_task, assist_task],
    verbose=True,
    memory=True,
    embedder=embedder_config
)

if __name__ == "__main__":
    inputs = {
        "query": "How to setup this project?",
        "user_context": "experience_level: advanced, specific_focus: high-level understanding"
    }

    # Kick off the Crew
    result = crew.kickoff(inputs=inputs)
# # Save the documentation content to a JSON file
# json_file_path = "documentation_content.json"
# with open(json_file_path, "w", encoding="utf-8") as json_file:
#     json.dump(documentation_content, json_file, ensure_ascii=False, indent=4)

# Display extracted documentation content for verification
print("\nExtracted Documentation Content:")
for file, content in documentation_content.items():
    print(f"\nFile: {file}\n{'-'*40}\n{content}\n")  # Print all chars of each file
