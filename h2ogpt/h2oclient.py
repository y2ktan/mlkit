# The grclient.py file can be copied from h2ogpt repo and used with local gradio_client for example use
from gradio_utils.grclient import GradioClient
from gradio_client import Client
import ast
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'resources'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'mp4'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
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
    prediction = make_prediction(text) # This function should implement your machine learning model
    return jsonify({'answer': prediction})


def make_prediction(question: str, local_server=True):
    if local_server:
        client = GradioClient("http://localhost:7860")
    else:
        h2ogpt_key = os.getenv('H2OGPT_KEY') or os.getenv('H2OGPT_H2OGPT_KEY')
        if h2ogpt_key is None:
            return
        # if you have API key for public instance:
        client = GradioClient("https://gpt.h2o.ai", h2ogpt_key=h2ogpt_key)

    db_file_path = ["http://0.0.0.0:8000/PAQ2277.txt", "http://0.0.0.0:8000/PAQ2278.txt"]

    # Q/A
    result = client.query("{}".format(question), url=db_file_path)
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
