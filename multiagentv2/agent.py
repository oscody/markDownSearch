
from crewai import Agent, Task, Crew, Process, LLM
import os
from crewai_tools import (
    FileReadTool,
)

# llm=LLM(model="ollama/llama3.2", base_url="http://localhost:11434")
OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")

llm=LLM(model="gpt-4")


file_tool = FileReadTool('/Users/bogle/Dev/obsidian/Bogle/2. Areas/multi device tester.md')
file_tool = FileReadTool('/Users/bogle/Dev/obsidian/Bogle/2. Areas/multi device tester.md')


extractor = Agent(
    role='Extractor',
    goal='Extract information from the note provided.',
    backstory='You are skilled at analyzing text and pulling out relevant information',
    tools=[file_tool],
    verbose=True,
    llm=llm,
    max_iter=1
)

summarizer = Agent(
    role='Summarizer',
    goal='Summarize the information from the provided links.',
    backstory='You are an expert at distilling key points from lengthy information.',
    verbose=True,
    llm=llm
)

hashtag_creator = Agent(
    role='Hashtag Creator',
    goal='Create relevant hashtags based on the content and links.',
    backstory='You are skilled at identifying keywords and creating impactful hashtags.',
    verbose=True,
    llm=llm
)

reviewer = Agent(
    role='Reviewer',
    goal='Review all generated hashtags and create a final list of the most relevant ones.',
    backstory='You are experienced at evaluating the quality and relevance of hashtags.',
    verbose=True,
    llm=llm
)


# Define the tasks
extract_information_task = Task(
    description="Read the given file and summerise what is in it",
    agent=extractor,
    expected_output="Read the given file and summerise what is in it"
)


# summarize_links_task = Task(
#     description="Summarize the information from the provided link.",
#     agent=summarizer,
#     expected_output="A concise summary of the information from each link."
# )

create_note_hashtags_task = Task(
    description="Create relevant hashtags based on the content of the note.",
    agent=hashtag_creator,
    expected_output="A list of hashtags based on the note content."
)

create_links_hashtags_task = Task(
    description="Create relevant hashtags based on the content of the summarized links.",
    agent=hashtag_creator,
    expected_output="A list of hashtags based on the summarized link content."
)

review_hashtags_task = Task(
    description="Review all the generated hashtags and create a final list of the most relevant ones.",
    agent=reviewer,
    expected_output="A final list of curated hashtags.",
    output_file="multiagentv2/agent_report.md"
)


notecrew = Crew(
    agents=[extractor, hashtag_creator, reviewer],
    tasks=[extract_information_task, create_note_hashtags_task, review_hashtags_task],
    verbose=True,
    process=Process.sequential
)




# Kickoff the crew process 
result = notecrew.kickoff()