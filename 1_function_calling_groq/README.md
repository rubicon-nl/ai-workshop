# Function calling met Groq en Llama3
We gaan Python gebruiken om via Groq het Llama3 model te gebruiken voor function calling. Dit doen we aan de hand van de volgende youtube video of onderstaande uitleg:
https://www.youtube.com/watch?v=7OAmeq-vwNc

## Voorbereiding
1. Installeer Conda [(download hier)](https://docs.anaconda.com/free/miniconda/)
   * **Belangrijk:** kies tijdens installatie voor toevoegen aan PATH!!
2. Maak een folder aan waar je in gaat werken
3. Ga naar [Groq Cloud](https://console.groq.com/login), maak hier een account of log in met Github/Google
4. Maak een API key aan en bewaar deze even, je hebt hem straks nodig!

## Het maken van de API
1. Maak een "environment": `conda create -n groq python=3.11 -y`
2. Open je environment: `conda activate groq`
3. Installeer een aantal packages: `pip install groq gradio requests flask`
4. Maak een nieuwe file genaamd `api.py`
5. code:
   ```python
    from flask import Flask, request, jsonify
    import json

    app = Flask(__name__)

    def get_game_score(team_name):
        """Get the current score for a given football game"""
        team_name = team_name.lower()
        if "ajax" in team_name:
            return {"game_id": "2342340", "status": 'final', "home_team": "Ajax", "home_team_score": 3, "away_team": "PSV", "away_team_score": 1}
        elif "psv" in team_name:
            return {"game_id": "2342342", "status": 'final', "home_team": "PSV", "home_team_score": 2, "away_team": "Feyenoord", "away_team_score": 2}
        elif "feyenoord" in team_name:
            return {"game_id": "2342343", "status": 'final', "home_team": "Feyenoord", "home_team_score": 1, "away_team": "Ajax", "away_team_score": 0}
        elif "az" in team_name:
            return {"game_id": "2342344", "status": 'final', "home_team": "AZ", "home_team_score": 2, "away_team": "PSV", "away_team_score": 1}
        else:
            return {"team_name": team_name, "score": "unknown"}
        
    @app.route('/score', methods=['GET'])
    def score():
        team_name = request.args.get('team', '')
        if not team_name:
            return jsonify({'error': 'Missing team name'}), 400
        score = get_game_score(team_name)
        return jsonify(score)

    if __name__ == '__main__':
    app.run(debug=True)
   ```
6. Draai de API: `python api.py`

## het maken van de UI
1. open een nieuwe terminal, laat die met de API draaien
2. Open je environment: `conda activate groq`
3. Export je API key: `$env:GROQ_API_KEY="xxxxxx"`
4. Gebruik code:
   ```python
    from groq import Groq
    import os
    import json
    import requests

    client = Groq(api_key = os.getenv('GROQ_API_KEY'))
    MODEL = 'llama3-70b-8192'

    def get_game_score(team_name):
        """Get the current score for a given football game by querying the Flask API."""
        url = f'http://127.0.0.1:5000/score?team={team_name}'
        response = requests.get(url)
        if response.status_code == 200:
            return json.dumps(response.json())
        else:
            return json.dumps({"error": "API request failed", "status_code": response.status_code})

    def run_conversation(user_prompt):
        # Step 1: send the conversation and available functions to the model
        messages=[
            {
                "role": "system",
                "content": "You are a function calling LLM that uses the data extracted from the get_game_score function to answer questions around football game scores. Include the team and their opponent in your response."
            },
            {
                "role": "user",
                "content": user_prompt,
            }
        ]
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_game_score",
                    "description": "Get the score for a given football game",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "team_name": {
                                "type": "string",
                                "description": "The name of the football team (e.g. 'Ajax')",
                            }
                        },
                        "required": ["team_name"],
                    },
                },
            }
        ]
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=tools,
            tool_choice="auto",  
            max_tokens=4096
        )

        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls
        # Step 2: check if the model wanted to call a function
        if tool_calls:
            # Step 3: call the function
            # Note: the JSON response may not always be valid; be sure to handle errors
            available_functions = {
                "get_game_score": get_game_score,
            }  # only one function in this example, but you can have multiple
            messages.append(response_message)  # extend conversation with assistant's reply
            # Step 4: send the info for each function call and function response to the model
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_to_call = available_functions[function_name]
                function_args = json.loads(tool_call.function.arguments)
                function_response = function_to_call(
                    team_name=function_args.get("team_name")
                )
                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": function_response,
                    }
                )  # extend conversation with function response
            second_response = client.chat.completions.create(
                model=MODEL,
                messages=messages
            )  # get a new response from the model where it can see the function response
            return second_response.choices[0].message.content
        
    user_prompt = "What was the score of the Ajax game?"
    print(run_conversation(user_prompt))
   ```
   5. draai het script: `python app.py` en je zult het resultaat zien
   6. Verwijder de laatste 2 regels code en vervang door:
   ```python
    def gradio_interface(user_prompt):
    return run_conversation(user_prompt)

    interface = gr.Interface(fn=gradio_interface, inputs="text", outputs="text")
    interface.launch()
   ```
   7. Draai de code nogmaals en gebruik de UI om je vraag nogmaals te stellen.