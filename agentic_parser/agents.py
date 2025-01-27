from crewai import Agent, Task, Crew, LLM
from crewai_tools import CodeDocsSearchTool

doc_reader = Agent(
    role="Technical Documentation Expert",
    goal=(
        "Be the ultimate source of clarity and precision in "
        "helping users understand technical concepts and documentation. "
        "Ensure users have a seamless experience navigating and applying "
        "the documentation to solve their problems effectively."
    ),
    backstory=(
        "You are a seasoned Technical Documentation Expert with years of "
        "experience in simplifying complex technical concepts and making them "
        "accessible to a diverse audience. Your passion lies in bridging the gap "
        "between technical content and user understanding, ensuring every piece "
        "of documentation is both practical and actionable. "
        "\n\n"
        "Your mission is to assist {person} in navigating CrewAI's technical documentation, "
        "answering their questions with thoroughness and empathy, and ensuring they "
        "feel confident and empowered to utilize the platform effectively. You are known "
        "for providing full, complete answers without making assumptions and always "
        "going the extra mile to ensure clarity."
    ),
    allow_delegation=False,
    verbose=True,
    llm=LLM(
        model="ollama/deepseek-r1:1.5b",
        base_url="http://localhost:11434"
    ) 
)

CDS_Tool = CodeDocsSearchTool(docs_url='https://documentation-using-ai-agent.readthedocs.io/en/latest/')

TD_Assistance= Task(
    description=(
        "{person} has submitted a technical query related to the documentation:\n"
        "{inquiry}\n\n"
        "{person} is seeking clarification. "
        "Your task is to thoroughly analyze the query, reference the relevant sections "
        "of the technical documentation, and provide a clear and concise explanation. "
        "Ensure the response is tailored to the customer's context and technical expertise."
    ),
    expected_output=(
        "A comprehensive and user-friendly explanation addressing the customer's inquiry. "
        "The response should include:\n"
        "- Detailed references to specific sections of the documentation.\n"
        "- Explanations that simplify complex terms or concepts, where necessary.\n"
        "- Additional context or examples to enhance understanding, if applicable.\n"
        "The tone must remain professional, friendly, and supportive, ensuring the customer "
        "feels confident and empowered to proceed."
    ),
    tools=[CDS_Tool],
    agent=doc_reader,
)

crew = Crew(
  agents=[doc_reader],
  tasks=[TD_Assistance],
  verbose=True,
  memory=True
)



if __name__ == "__main__":
    inputs = {
    "person": "Andrew Ng",
    "inquiry": "I need help with setting up the django project"
               "and kicking it off, specifically "
               "how can I run the CRON script?"
               "Can you provide guidance?"
    }
    result = crew.kickoff(inputs=inputs)