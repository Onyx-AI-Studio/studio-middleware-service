import json
import os
import sys
import asyncio

from flask import Flask, jsonify, request
from deepgram import Deepgram


def speech_to_text(conv_id: str, audio_file):
    if request.method == 'POST':
        data = "This is a place holder for output from Deepgram"

        try:
            # Transcribe to text using Deepgram
            response = asyncio.run(deepgram_stt(audio_file))
            verbatim, summaries = response["results"]["channels"][0]["alternatives"][0]["transcript"], \
                response["results"]["channels"][0]["alternatives"][0]["summaries"]

            return jsonify(
                {
                    'verbatim': verbatim,
                    'summaries': summaries
                }
            )

        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            line_number = exception_traceback.tb_lineno
            print(f'line {line_number}: {exception_type} - {e}')

        return jsonify({'result': 'Something wrong with Deepgram API'})


async def deepgram_stt(FILE: str):
    # FILE = './audio_files/6min.mp3'

    MIMETYPE = 'audio/mp3'

    # Initialize the Deepgram SDK
    deepgram = Deepgram(os.environ["DEEPGRAM_API_KEY"])

    # Check whether requested file is local or remote, and prepare source
    if FILE.startswith('http'):
        source = {'url': FILE}
    else:
        audio = open(FILE, 'rb')
        source = {'buffer': audio, 'mimetype': MIMETYPE}

    # Send the audio to Deepgram and get the response
    response = await asyncio.create_task(
        deepgram.transcription.prerecorded(
            source,
            {
                'punctuate': True,
                'model': 'nova',
                'diarize': True,
                'summarize': True,
            }
        )
    )

    print(f'Speech to text based on audio input: {json.dumps(response, indent=4)}')
    # return response["results"]["channels"][0]["alternatives"][0]["transcript"]
    # return response["results"]["channels"][0]["alternatives"][0]["transcript"], \
    #     response["results"]["channels"][0]["alternatives"][0]["summaries"]
    return response


# NOT USED!
def process_response(conversation_id: str):
    dirname = "./audio_files/"
    save_path = os.path.join(dirname, conversation_id + ".mp3")
    request.files['audio_file'].save(save_path)

    try:
        # Transcribe to text using Deepgram
        response = asyncio.run(deepgram_stt(save_path))
        print(f'Speech to text based on audio input: {json.dumps(response, indent=2)}')

        # Build transcript object using the speech to text response
        idx = 0
        transcript = []
        temp = {'speaker': 0, 'utterance': "", 'fraudulent': False}
        transcript.append(temp)

        # TODO: isolate the following logic to build transcript based on conversation
        words = response["results"]["channels"][0]["alternatives"][0]["words"]
        for i in range(len(words)):
            if i == 0:
                continue

            if words[i - 1]["speaker"] == words[i]["speaker"]:
                # print(transcript)
                transcript[idx]["utterance"] += words[i]["punctuated_word"] + " "
            else:
                idx += 1
                temp = {
                    'speaker': words[i]["speaker"],
                    'utterance': words[i]["punctuated_word"] + " ",
                    'fraudulent': False
                }
                transcript.append(temp)

        return jsonify({
            'response': response,
            'transcript': transcript,
        })
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        line_number = exception_traceback.tb_lineno
        print(f'line {line_number}: {exception_type} - {e}')

    return jsonify({'result': 'Something wrong with Deepgram API'})
