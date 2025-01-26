
from crewai import Agent, Task, Crew, Process, LLM
import os
from dotenv import load_dotenv
from crewai_tools import (
    FileReadTool,
)

llm=LLM(model="ollama/llama3.2", base_url="http://localhost:11434")

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

# Define the tasks
extract_information_task = Task(
    description="Read the given file and summerise what is in it",
    agent=extractor,
    expected_output="Read the given file and summerise what is in it"

)


notecrew = Crew(
    agents=[extractor],
    tasks=[extract_information_task],
    verbose=True,
    process=Process.sequential
)



# Kickoff the crew process 
result = notecrew.kickoff()