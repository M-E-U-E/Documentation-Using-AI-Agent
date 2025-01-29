import os
import requests
from crewai import Agent, Task, Crew
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

gapi_key = os.getenv("GEMINI_API_KEY")

# Dynamically get the correct absolute path of the `docs/` directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))  # Get the script's directory
DOCS_DIR = os.path.join(SCRIPT_DIR, "docs")  # Construct the absolute path to 'docs'

# Check if the directory exists before proceeding
if not os.path.exists(DOCS_DIR):
    raise FileNotFoundError(f"Error: The 'docs/' directory does not exist at {DOCS_DIR}. Please create it.")

# Custom Tool to Read Markdown Files
def read_markdown_files(directory: str):
    """
    Reads all markdown (.md) files from the specified directory and returns structured content.
    
    Args:
        directory (str): Path to the documentation directory.
        
    Returns:
        dict: A dictionary with filenames as keys and their content as values.
    """
    docs_content = {}
    
    for filename in os.listdir(directory):
        if filename.endswith(".md"):  # Only process markdown files
            file_path = os.path.join(directory, filename)
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    docs_content[filename] = file.read()
            except Exception as e:
                docs_content[filename] = f"Error reading file: {e}"
    
    return docs_content


# Initialize the custom tool for reading Markdown files
documentation_content = read_markdown_files(DOCS_DIR)

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
        "query": "Can you summarize the project goal?",
        "user_context": "experience_level: advanced, specific_focus: high-level understanding"
    }

    # Kick off the Crew
    result = crew.kickoff(inputs=inputs)

    # Output the extracted documentation content for verification
    print("\nExtracted Documentation Content:")
    for file, content in documentation_content.items():
        print(f"\nFile: {file}\n{'-'*40}\n{content[:1000]}...\n")  # Print first 500 chars of each file
