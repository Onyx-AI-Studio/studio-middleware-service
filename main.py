from flask import Flask, jsonify, request
import json
import os
import requests
from pathlib import Path

import app.adapter.deepgram as deepgram
import boto3

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


@app.route('/stt', methods=['POST'])
def stt():
    conv_id = request.json["conversation_id"]
    s3_audio_file_path = str(request.json["s3_audio_file_path"])
    stt_model = str(request.json["stt_model"])

    save_folder = '/Users/snehalyelmati/Documents/studio-middleware-service/audio_files'
    save_path = Path(save_folder, conv_id)
    print(f'save_path: {save_path}')
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    filename = '_'.join(s3_audio_file_path.split('/')[-1].split('_')[1:])
    print(f'filename: {filename}')

    s3 = boto3.client("s3")
    s3.download_file('onyx-test-001', s3_audio_file_path, Path(save_path, filename))
    print(f'File downloaded from S3!')

    stt_engine = deepgram
    deepgram_response = stt_engine.speech_to_text(conv_id, str(Path(save_path, filename)), stt_model)
    return deepgram_response


@app.route('/deepgram_healthcheck', methods=['GET'])
def deepgram_healthcheck():
    # response = await deepgram.projects.list()
    # return True if response.status_code == 200 else False
    return jsonify({'status': "True" if deepgram.healthcheck() else "False"})


# driver function
if __name__ == '__main__':
    app.run(port=5999, debug=True)
