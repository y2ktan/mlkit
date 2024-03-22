# The grclient.py file can be copied from h2ogpt repo and used with local gradio_client for example use
from gradio_utils.grclient import GradioClient
from gradio_client import Client
import ast
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
import datetime

app = Flask(__name__)
UPLOAD_FOLDER = '../database'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'mp4'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def list_files(dir="../database"):
    path = dir
    files = os.listdir(path)
    return files


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'

    file = request.files['file']

    if file.filename == '':
        return 'No selected file'

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return 'File uploaded successfully'

    return 'Invalid file type'


@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    text = data['question']


    ip_address = data.get("ip_address", None)
    radio_id = data.get("radio_id", None)

    print("IP address: " + ip_address)
    print("Radio ID: " + radio_id)
    prediction = make_prediction(text)  # This function should implement your machine learning model
    answer = jsonify({'answer1': prediction, 'ip_address': ip_address, 'radio_id': radio_id})

    #web socket to notify the drive of the message

    return answer


def make_prediction(question: str, local_server=True):
    if local_server:
        client = GradioClient("http://localhost:7860")
    else:
        h2ogpt_key = os.getenv('H2OGPT_KEY') or os.getenv('H2OGPT_H2OGPT_KEY')
        if h2ogpt_key is None:
            return
        # if you have API key for public instance:
        client = GradioClient("https://gpt.h2o.ai", h2ogpt_key=h2ogpt_key)

    files = list_files()
    db_file_path = []
    for file in files:
        db_file_path.append("http://0.0.0.0:8000/{fname}".format(fname=file))

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    short_summary = "Provide a short and straight to-the-point answer to the question according to the information provided by URLs without providing the source of information and suggestion in the answer"

    # Q/A
    result = client.query("{}: {},{}".format(short_summary, now, question), url=db_file_path)
    return result


@app.route('/predictText', methods=['POST'])
def predictText():
    data = request.get_json()
    text = data['question']
    prediction = make_predictionText(text)  # This function should implement your machine learning model
    return jsonify({'answer': prediction})


@app.route('/textTest', methods=['POST'])
def textQuery():
    data = request.get_json()
    text = data['question']
    prediction = make_predictionText(text)  # This function should implement your machine learning model
    return jsonify({'answer: test'})


def make_predictionText(question: str, local_server=True):
    if local_server:
        client = GradioClient("http://localhost:7860")
    else:
        h2ogpt_key = os.getenv('H2OGPT_KEY') or os.getenv('H2OGPT_H2OGPT_KEY')
        if h2ogpt_key is None:
            return
        # if you have API key for public instance:
        client = GradioClient("https://gpt.h2o.ai", h2ogpt_key=h2ogpt_key)

    files = list_files()
    db_file_path = []
    for file in files:
        db_file_path.append("http://0.0.0.0:8000/{fname}".format(fname=file))

    # Q/A
    result = client.query(
        "{}, the latest information from the text file, with a short response of no more than ten words".format(
            question), url=db_file_path)
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
