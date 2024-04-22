import json
import requests
from crewai import Agent, Task, Crew
from crewai_tools import tool

# Define a tool for an agent to use, to get the game score
@tool("Game score tool")
def game_score_tool(team_name: str) -> str:
    """Get the current score of a given Eredivisie game by querying the Flask API. It accepts a team name and returns the score of the game."""
    url = f'http://localhost:5000/score?team={team_name.lower()}'
    response = requests.get(url)
    if response.status_code == 200:
        return json.dumps(response.json(), indent=2)
    else:
        return json.dumps({"error": "An error occurred while fetching the game score.", "status": response.status}, indent=2)
    
# Create agents
researcher = Agent(
    role='Researcher',
    goal='Gather and analyze information on Eredivisie games scores',
    verbose=True,
    backstory=(
        "As a seasoned researcher, you have a keen eye for detail and a deep understanding of sports analytics. You're adept at sifting through scores to find the most relevant and accurate data."
    ),
    tools=[game_score_tool],
    allow_delegation=False
)

writer = Agent(
    role='Sports journalist',
    goal='Compose an engaging news article based on Eredivisie game scores',
    verbose=True,
    backstory=(
        "With a talent for storytelling, you convert statistical data and game outcomes into engaging sports narratives. Your articles are insightful, capturing the excitement of the games and providing a deep analysis for sports enthusiasts."
    ),
    allow_delegation=False
)

# Create tasks
research_task = Task(
    description='Investigate the scores for the Ajax game',
    expected_output='A detailed report summarizing the data',
    tools=[game_score_tool],
    agent=researcher,
)

writing_task = Task(
    description='Write an article on the latest Eredivisie games',
    expected_output='A well-crafted article that captures the excitement of the games',
    context=[research_task],
    agent=writer,
)

# Compose the crew
crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, writing_task],
)   

# Start the crew conversation
result = crew.kickoff()
print(result)