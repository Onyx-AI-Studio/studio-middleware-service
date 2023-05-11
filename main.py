from flask import Flask, jsonify, request
import json
import requests

# Creating a Flask app
app = Flask(__name__)


# To check the if the API is up
@app.route('/healthcheck', methods=['GET'])
def healthcheck():
    if request.method == 'GET':
        data = "API is up!"
        return jsonify({'status': data})


# This route handles all studio traffic and request patterns
@app.route('/studio_handler', methods=['POST'])
def studio_handler():
    if request.method == "POST":
        utterance = request.json["utterance"]
        llm_selected = request.json["llm_selected"]
        # do a post request to llm_service to fetch the required data and pass to the studio
        url = "http://localhost:6999/llm_predict"

        payload = json.dumps({
            "utterance": utterance,
            "llm_selected": llm_selected,
        })
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload).json()
        return response


# driver function
if __name__ == '__main__':
    app.run(port=5999, debug=True)

# from app.adapter.inmemory_vote_repository import InMemoryVoteRepository
# from app.domain.vote import Vote
#
# from fastapi import FastAPI
#
# app = FastAPI()
#
# vote_repository = InMemoryVoteRepository()
#
#
# @app.post("/vote", response_model=Vote)
# def vote() -> Vote:
#     return Vote().save(vote_repository)
#
#
# @app.get("/votes", response_model=int)
# def votes() -> int:
#     return vote_repository.total()
