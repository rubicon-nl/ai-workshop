# LLama3 agents met Groq en CrewAI
We gaan Python gebruiken om een agent-based nieuwsbureau te emuleren met AI. De volgende youtube video is de leidraad: https://www.youtube.com/watch?v=9fcQDJw2lcE
Onderstaand vind je een beknopt uitgeschreven versie daarvan:

## voorbereiding
1. Installeer Conda [(download hier)](https://docs.anaconda.com/free/miniconda/)
   * **Belangrijk:** kies tijdens installatie voor toevoegen aan PATH!!
2. Maak een folder aan waar je in gaat werken
3. Ga naar [Groq Cloud](https://console.groq.com/login), maak hier een account of log in met Github/Google
4. Maak een API key aan en bewaar deze even, je hebt hem straks nodig!

## Het maken van de API
1. Maak een "environment": `conda create -n crewai python=3.11 -y`
2. Open je environment: `conda activate crewai`
3. Installeer een aantal packages: `pip install 'crewai[tools]' flask requests`
4. Maak een nieuwe file genaamd `scores_api.py`  
5. Gebruik onderstaande code:

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

def get_game_score(team_name):
    if "ajax" in team_name:
        return {"game_id": "2342340", "status": 'final', "home_team": "Ajax", "home_team_score": 3, "away_team": "PSV", "away_team_score": 1}
    elif "psv" in team_name:
        return {"game_id": "2342342", "status": 'final', "home_team": "PSV", "home_team_score": 2, "away_team": "Feyenoord", "away_team_score": 2}
    elif "feyenoord" in team_name:
        return {"game_id": "2342343", "status": 'final', "home_team": "Feyenoord", "home_team_score": 1, "away_team": "Ajax", "away_team_score": 0}
    elif "az" in team_name:
        return {"game_id": "2342344", "status": 'final', "home_team": "AZ", "home_team_score": 2, "away_team": "PSV", "away_team_score": 1}
    else:
        return {"team_name": team_name, "status": 'not found'}
    
@app.route('/')
def home():
    return jsonify({'message': 'Welcome to the Eredivisie scores API. Use /score?team=<team_name> to get the score of the game.'}), 200

@app.route('/score', methods=['GET'])
def score():
    team_name = request.args.get('team', '')
    if not team_name:
        return jsonify({"error": "Please provide a team name in the query parameter"}), 400
    score = get_game_score(team_name)
    return jsonify(score)


if __name__ == '__main__': 
    app.run(debug=True)
```
6. Start de api, en laat deze draaien: `python scores_api.py`

## Het maken van de agent crew
1. splits je terminal, zodat je naast de nog draaiende api een nieuwe console hebt. 
2. Open je environment: `conda activate crewai`
3. Maak deze omgevingsvariabelen aan:

```pwsh
$env:OPENAI_API_BASE='https://api.groq.com/openai/v1'
$env:OPENAI_MODEL_NAME='llama3-70b-8192'
$env:OPENAI_API_KEY='' # vul je eigen api key in
```

4. Gebruik de volgende code:

```python
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
```

5. Start de crew: `python.exe .\crewai_agents.py` en zie hoe je een nieuwsartikeltje krijgt over een Ajax-wedstrijd.
6. Verander de task door in `description='Investigate the scores for the Ajax game',` 'Ajax' te veranderen in bijv. 'Feyenoord'.
7. Start de crew nogmaals.

