from crewai_tools import CodeDocsSearchTool
from crewai import Agent, Task, Crew
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin, urlparse

load_dotenv()

gapi_key = os.getenv('GEMINI_API_KEY')
documentation_url = 'https://documentation-using-ai-agent.readthedocs.io/en/latest/'

def find_all_subpages(base_url, visited=None):
    """Find all subpages of a documentation website."""
    if visited is None:
        visited = set()

    if base_url in visited:
        return visited

    print(f"Finding links on: {base_url}")
    visited.add(base_url)

    try:
        response = requests.get(base_url, timeout=10)
        if response.status_code != 200:
            return visited

        soup = BeautifulSoup(response.text, "html.parser")

        # Find all internal links
        for link in soup.find_all("a", href=True):
            href = link["href"]
            next_url = urljoin(base_url, href)

            # Ensure it's within the same documentation domain
            if urlparse(next_url).netloc == urlparse(base_url).netloc:
                if next_url not in visited:
                    visited.update(find_all_subpages(next_url, visited))

    except Exception as e:
        print(f"Error finding links on {base_url}: {e}")

    return visited


# Step 1: Find all subpages
all_documentation_pages = find_all_subpages(documentation_url)
print(f"Discovered {len(all_documentation_pages)} pages.")

# Step 2: Initialize CodeDocsSearchTool for each page
scrape_tools = [
    CodeDocsSearchTool(
        config=dict(
            llm=dict(
                provider="google",
                config=dict(
                    model="gemini/gemini-1.5-flash-latest",
                ),
            ),
            embedder=dict(
                provider="google",
                config=dict(
                    model="models/embedding-001",
                    task_type="retrieval_document",
                ),
            ),
        ),
        docs_url=page_url
    )
    for page_url in all_documentation_pages
]

# Define Agents
crawler_agent = Agent(
    role="Documentation Crawler",
    goal="Thoroughly crawl and extract content from documentation pages",
    backstory="""You are an expert web crawler specialized in technical documentation.
    Your mission is to systematically explore and extract content from documentation
    pages while maintaining the proper structure and hierarchy.""",
    tools=scrape_tools,
    verbose=True,
    memory=True,
    llm="gemini/gemini-1.5-flash-latest"
)

analyzer_agent = Agent(
    role="Content Analyzer",
    goal="Process and organize documentation content for efficient retrieval",
    backstory="""You are an expert in analyzing technical documentation and creating
    structured knowledge bases. Your role is to process raw content, create summaries,
    and organize information in an easily searchable format.""",
    verbose=True,
    memory=True,
    llm="gemini/gemini-1.5-flash-latest"
)

user_assistant = Agent(
    role="Documentation Guide",
    goal="Help users understand and apply documentation effectively",
    backstory="""You are an expert technical assistant who helps users navigate
    and understand documentation. You can break down complex problems into
    step-by-step solutions and provide clear, actionable guidance.""",
    verbose=True,
    memory=True,
    llm="gemini/gemini-1.5-flash-latest"
)

# Define Tasks
crawl_task = Task(
    description="""
    1. Crawl the documentation starting from the provided URL
    2. Find all subpages and collect their URLs
    3. Run CodeDocsSearchTool on each subpage
    4. Store the extracted information
    """,
    expected_output="""
    A structured dictionary containing:
    - Extracted content from all documentation pages
    - Hierarchical structure of the documentation
    - All relevant links and their relationships
    - Metadata for each page
    - Error logs if any pages failed to crawl
    """,
    agent=crawler_agent,
    tools=scrape_tools,
    verbose=True
)

analyze_task = Task(
    description="""
    1. Process the crawled documentation content
    2. Generate summaries for each section
    3. Create a searchable knowledge base
    4. Identify key concepts and their relationships
    5. Prepare content for user queries
    """,
    expected_output="""
    A processed knowledge base containing:
    - Section summaries
    - Key concepts and their definitions
    - Relationship mappings between concepts
    - Indexed content for quick search
    - Metadata for content organization
    """,
    agent=analyzer_agent,
    verbose=True
)

assist_task = Task(
    description="""
    1. Understand user queries about the documentation
    2. Search the processed knowledge base
    3. Provide step-by-step solutions
    4. Explain concepts clearly
    5. Guide users through implementation
    """,
    expected_output="""
    Clear and actionable responses including:
    - Direct answers to user queries
    - Step-by-step implementation guides
    - Relevant documentation references
    - Examples and explanations
    - Troubleshooting suggestions if needed
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
        "query": "How do I setup the project?",
        "user_context": {
            "experience_level": "intermediate",
            "specific_focus": "implementation details"
        }
    }
    
    result = crew.kickoff(inputs=inputs)
    print(result)
