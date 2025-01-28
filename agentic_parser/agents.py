from bs4 import BeautifulSoup
from typing import Dict, Type
import requests
from dataclasses import Field
from crewai import Agent, Task, Crew
from dotenv import load_dotenv
from urllib.parse import urljoin
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import os

load_dotenv()

gapi_key = os.getenv('GEMINI_API_KEY')

class EnhancedDocumentationToolInput(BaseModel):
    """Input schema for EnhancedDocumentationTool."""
    url: str = Field(..., description="The starting URL to crawl for documentation content.")

class EnhancedDocumentationTool(BaseTool):
    name: str = "enhanced_documentation_tool"
    description: str = "A tool to crawl and extract content from documentation pages."
    args_schema: Type[BaseModel] = EnhancedDocumentationToolInput

    def __init__(self, base_url: str):
        # Explicitly set the name and description for BaseTool constructor
        super().__init__(name=self.name, description=self.description)
        self.base_url = base_url
        self.visited_urls = set()
        self.content_store = {}

    def _run(self, input_data: EnhancedDocumentationToolInput) -> Dict:
        """Implements the tool's primary logic."""
        url = input_data.url  # Extract URL from the input schema
        if not url:
            return {"error": "No URL provided"}
        return self.crawl(url)

    def crawl(self, url: str) -> Dict:
        """Recursively crawl documentation pages."""
        if url in self.visited_urls:
            return {}

        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            self.visited_urls.add(url)

            # Extract content
            content = self._extract_content(soup)
            # Find documentation links
            links = self._find_doc_links(soup, url)

            # Store current page content
            self.content_store[url] = {
                'title': content['title'],
                'content': content['content'],
                'links': links,
                'metadata': content['metadata']
            }

            # Recursively crawl linked pages
            for link in links:
                if link not in self.visited_urls:
                    self.crawl(link)

            return self.content_store

        except Exception as e:
            return {'error': f'Failed to crawl {url}: {str(e)}'}

    def _extract_content(self, soup: BeautifulSoup) -> Dict:
        """Extract content from page."""
        main_content = (
            soup.find('article') or
            soup.find('main') or
            soup.find('div', class_='content') or
            soup.find('div', class_='document')
        )

        sections = []
        if main_content:
            for header in main_content.find_all(['h1', 'h2', 'h3']):
                sections.append({
                    'level': int(header.name[1]),
                    'text': header.get_text(strip=True)
                })

        return {
            'title': soup.title.string if soup.title else '',
            'content': main_content.get_text('\n', strip=True) if main_content else '',
            'metadata': {
                'sections': sections
            }
        }

    def _find_doc_links(self, soup: BeautifulSoup, current_url: str) -> list[str]:
        """Find documentation-related links."""
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            full_url = urljoin(current_url, href)
            if (
                full_url.startswith(self.base_url) and
                not href.startswith('#') and
                full_url not in self.visited_urls
            ):
                links.append(full_url)
        return links
    

# Initialize tools
doc_tool = EnhancedDocumentationTool('https://documentation-using-ai-agent.readthedocs.io/en/latest/')



# Define Agents - remove the llm parameter since it's already an LLM object
crawler_agent = Agent(
    role="Documentation Crawler",
    goal="Thoroughly crawl and extract content from documentation pages",
    backstory="""You are an expert web crawler specialized in technical documentation.
    Your mission is to systematically explore and extract content from documentation
    pages while maintaining the proper structure and hierarchy.""",
    tools=[doc_tool],
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

# Define Tasks with expected_output field
crawl_task = Task(
    description="""
    1. Crawl the documentation starting from the provided URL
    2. Extract content from each page
    3. Maintain documentation hierarchy
    4. Collect all relevant links and content
    5. Store the extracted information
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
    tools=[doc_tool],
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
    1. Understand user {query} about the documentation and the {user_context}
    2. Search the processed knowledge base
    3. Provide step-by-step solutions
    4. Explain concepts clearly
    5. Guide users through implementation
    """,
    expected_output="""
    Clear and actionable responses including:
    - Direct answers to user {query}
    - Step-by-step implementation of the answer
    - Relevant documentation references
    - Troubleshooting suggestions if needed
    """,
    agent=user_assistant,
    verbose=True
)

# Updated embedder configuration with correct model name format
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
        "query": "How do I setup and run the project?",
        "user_context": "experience_level : intermediate, specific_focus : implementation details"
                  
    }
    
    result = crew.kickoff(inputs=inputs)
    print(result)