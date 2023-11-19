# self-contained example used for readme, to be copied to README_CLIENT.md if changed, setting local_server = True at first
import os
# The grclient.py file can be copied from h2ogpt repo and used with local gradio_client for example use
from gradio_utils.grclient import GradioClient
from gradio_client import Client
import ast
from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    text = data['question']
    prediction = make_prediction(text) # This function should implement your machine learning model
    return jsonify({'answer': prediction})


def make_prediction(question: str, local_server=True):
    if local_server:
        client = GradioClient("http://0.0.0.0:7860")
    else:
        h2ogpt_key = os.getenv('H2OGPT_KEY') or os.getenv('H2OGPT_H2OGPT_KEY')
        if h2ogpt_key is None:
            return
        # if you have API key for public instance:
        client = GradioClient("https://gpt.h2o.ai", h2ogpt_key=h2ogpt_key)

    url = "https://cdn.openai.com/papers/whisper.pdf"

    # Q/A
    result = client.query("{}. Limit the answer to maximum 100 words".format(question), url=url)
    return result


def simple_question_answer():
    HOST_URL = "http://localhost:7860"
    client = Client(HOST_URL)

    # string of dict for input
    kwargs = dict(instruction_nochat='Who are you?')
    res = client.predict(str(dict(kwargs)), api_name='/submit_nochat_api')

    # string of dict for output
    response = ast.literal_eval(res)['response']
    print(response)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=2277)
