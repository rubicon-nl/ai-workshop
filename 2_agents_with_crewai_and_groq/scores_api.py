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