import pprint

from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
import datetime
import json
import requests
import ollama
import uuid
import shutil
import speechToText

app = Flask(__name__)
UPLOAD_FOLDER = 'database'
ALLOWED_EXTENSIONS = {'txt', 'pdf'}
IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg'}
VIDEO_EXTENSION = {'mp4'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

PRIVATE_GPT_COMPLETION_URL = "http://0.0.0.0:8001/v1/chat/completions"
PRIVATE_GPT_INGESTION_URL = "http://0.0.0.0:8001/v1/ingest/file"
PRIVATE_GPT_INGESTION_LIST_URL = "http://0.0.0.0:8001/v1/ingest/list"
PRIVATE_GPT_DEL_INGESTION_URL = "http://0.0.0.0:8001/v1/ingest"


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def is_image(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in IMAGE_EXTENSIONS


def list_files(dir="../database"):
    path = dir
    files = os.listdir(path)
    return files


def describe_image(id = "User",
                   prompt = "Describe these images",
                   images: list = []):
    # res = ollama.chat(
    #     model="llava:latest",
    #     messages=[
    #         {
    #             "role": "system",
    #             "content": "You are an a police officer.",
    #         },
    #         {
    #             'role': id,
    #             'content': prompt,
    #             'images': images
    #         }
    #     ]
    # )

    if not images:
        messages = [{'role': id, 'content': prompt}]
    else:
        messages = [{'role': 'user', 'content': prompt, 'images': images}]

    res = ollama.chat(
        model="llava:latest",
        messages=messages
    )

    response = res['message']['content']
    pprint.pprint(res)

    unique_filename = os.path.join(UPLOAD_FOLDER, str(uuid.uuid4()) + ".txt")
    with open(unique_filename, "w+") as file:
        file.write(response)
    with open(unique_filename, "rb") as file:
        filename = secure_filename(unique_filename)
        headers = {'Context-Type': 'v1/ingest/file'}
        http_response = requests.post(PRIVATE_GPT_INGESTION_URL, headers=headers, files={'file': (filename, file)})
        if http_response.status_code == 200:
            os.remove(unique_filename)
            return True
    return False


#@curl -X POST -F "images=@/path/to/image1.png" -F "images=@/path/to/image2.png" http://0.0.0.:5044/upload-images
@app.route('/upload-images', methods=['POST'])
def upload_images():
    import pprint
    pprint.pprint(request.files)
    if len(request.files.getlist('images')) <= 0:
        return jsonify({'message': 'No file part'}), 400
    files = request.files.getlist('images')
    result = []
    current_time = datetime.datetime.now()
    image_folder = os.path.join(UPLOAD_FOLDER, current_time.strftime("%d%m%Y%H%M%S"))
    os.makedirs(image_folder, exist_ok=True)
    local_image_file_list = []

    for file in files:
        if file and is_image(file.filename):
            filename = secure_filename(file.filename)
            image_path = os.path.join(image_folder, filename)
            local_image_file_list.append(image_path)
            file.save(os.path.join(image_folder, filename))
            result.append({'filename': filename})
        else:
            return jsonify({'message': 'File type not allowed'}), 400
    if not describe_image(images=local_image_file_list):
        return jsonify({'message': 'File failed to upload'}), 500
    if shutil.os.path.exists(image_folder):
        shutil.rmtree(image_folder)
    return jsonify(result)


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'

    file = request.files['file']

    if file.filename == '':
        return 'No selected file'

    if file and allowed_file(file.filename):
        headers = {'Context-Type': 'v1/ingest/file'}
        filename = secure_filename(file.filename)
        response = requests.post(PRIVATE_GPT_INGESTION_URL, headers=headers, files={'file': (filename, file)})
        if response.status_code == 200:
            return 'File uploaded successfully'
    return 'Invalid file type'


@app.route('/clean', methods=['POST'])
def clean_files():
    doc_ids = []
    response = requests.get(PRIVATE_GPT_INGESTION_LIST_URL)
    if response.status_code == 200:
        document_response = response.json()
        if "data" in document_response:
            for document in document_response["data"]:
                doc_ids.append(document["doc_id"])
            for doc_id in doc_ids:
                delete_url = "{}/{}".format(PRIVATE_GPT_DEL_INGESTION_URL, str(doc_id))
                print(delete_url)
                requests.delete(delete_url)
            return "deleted files size: " + str(len(doc_ids))
        else:
            return "no data in reponse"
    else:
        return "status code: "+str(response.status_code)


@app.route('/predict', methods=['POST'])
def predict():
    if 'file' in request.files:
        file = request.files['file']
        text = speechToText.speech_to_text(file)
    else:
        data = request.get_json()
        text = data['question']

    prediction = make_prediction(text)
    answer = jsonify({'answer': prediction})

    return answer

def make_prediction(question: str, radio_id="user"):
    headers = {"Content-Type": "application/json"}
    short_summary = ("Provide a short and straight to-the-point answer to the question according to the information provided without "
                     "providing any unrelated information and suggestion in the answer. Question is: ")
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    query = "{}: {},{}".format(short_summary, now, question)

    data = {
        "messages": [
            {
                "role": radio_id,
                "content": query
            }
        ],
        "stream": False,
        "use_context": True
    }

    response = requests.post(PRIVATE_GPT_COMPLETION_URL, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        prediction = response.json()
        return prediction["choices"][0]["message"]["content"]
    else:
        return response.status_code


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5044)
