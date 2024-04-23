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