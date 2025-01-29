import os
import requests
from crewai import Agent, Task, Crew
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

gapi_key = os.getenv("GEMINI_API_KEY")

# GitHub repository and path setup loaded from .env file
GITHUB_REPO = os.getenv("GITHUB_REPO")  # Fetching from .env
GITHUB_RAW_URL = os.getenv("GITHUB_RAW_URL")  # Fetching from .env

# Custom Tool to Read Markdown Files from GitHub Repository
def read_markdown_files_from_github(repo_url: str, raw_url: str):
    """
    Fetches markdown files from a GitHub repository and returns structured content.
    
    Args:
        repo_url (str): GitHub API URL to fetch the list of files.
        raw_url (str): Base URL for accessing raw file content.
        
    Returns:
        dict: A dictionary with filenames as keys and their content as values.
    """
    docs_content = {}
    
    # Fetch list of files from the GitHub repository
    response = requests.get(repo_url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch files from GitHub: {response.status_code}")
    
    files = response.json()
    
    for file_info in files:
        if file_info['name'].endswith(".md"):  # Only process markdown files
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
documentation_content = read_markdown_files_from_github(GITHUB_REPO, GITHUB_RAW_URL)

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

# Display extracted documentation content for verification
print("\nExtracted Documentation Content:")
for file, content in documentation_content.items():
    print(f"\nFile: {file}\n{'-'*40}\n{content[:1000]}...\n")  # Print first 1000 chars of each file
