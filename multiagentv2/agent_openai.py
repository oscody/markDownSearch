
from crewai import Agent, Task, Crew, Process, LLM
import os
from openai import OpenAI
from dotenv import load_dotenv
from crewai_tools import (
    FileReadTool,
)


OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")

llm=LLM(model="gpt-4")


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

hashtag_creator = Agent(
    role='Hashtag Creator',
    goal='Create relevant hashtags based on the content and links.',
    backstory='You are skilled at identifying keywords and creating impactful hashtags.',
    verbose=True,
    llm=llm,
    max_iter=1
)

create_note_hashtags_task = Task(
    description="Create relevant hashtags based on the content of the note.",
    agent=hashtag_creator,
    expected_output="A list of hashtags based on the note content."
)



# Define the tasks
extract_information_task = Task(
    description="Read the given file and summerise what is in it",
    agent=extractor,
    expected_output="Read the given file and summerise what is in it"

)


notecrew = Crew(
    agents=[extractor, hashtag_creator],
    tasks=[extract_information_task, create_note_hashtags_task],
    verbose=True,
    process=Process.sequential
)



# Kickoff the crew process 
result = notecrew.kickoff({"path_to_the_file": "/Users/bogle/Dev/obsidian/Bogle/2. Areas/multi device tester.md"})
print(result)