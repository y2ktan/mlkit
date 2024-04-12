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
from BusAttendance import BusAttendance
from model.Bus import *
from model.Passenger import *

app = Flask(__name__)
UPLOAD_FOLDER = 'database'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'json'}
IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg'}
VIDEO_EXTENSION = {'mp4'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

PRIVATE_GPT_COMPLETION_URL = "http://0.0.0.0:8001/v1/chat/completions"
PRIVATE_GPT_INGESTION_URL = "http://0.0.0.0:8001/v1/ingest/file"
PRIVATE_GPT_INGESTION_LIST_URL = "http://0.0.0.0:8001/v1/ingest/list"
PRIVATE_GPT_DEL_INGESTION_URL = "http://0.0.0.0:8001/v1/ingest"
BUS_ATTENDANCE_FILE_NAME = "bus_attendance.json"
BUS_ATTENDANCE_FILE = os.path.join(UPLOAD_FOLDER, BUS_ATTENDANCE_FILE_NAME)


def init_or_reset():
    bus = Bus(plate_number='', bus_activities=[])
    passengers: list[Passenger] = []
    return BusAttendance(bus, passengers)


_bus_attendance = init_or_reset()


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


def describe_image(id="User",
                   prompt="Describe these images",
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
            return (True, response)
    return (False, None)


# @curl -X POST -F "images=@/path/to/image1.png" -F "images=@/path/to/image2.png" http://0.0.0.:5044/upload-images
@app.route('/upload-images', methods=['POST'])
def upload_images():
    import pprint
    pprint.pprint(request.files)
    prompt = None
    if 'prompt' in request.form:
        prompt = request.form['prompt']
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
    if prompt:
        llava_result, answer = describe_image(prompt=prompt, images=local_image_file_list)
    else:
        llava_result, answer = describe_image(images=local_image_file_list)

    if not llava_result:
        return jsonify({'message': 'File failed to upload'}), 500

    if shutil.os.path.exists(image_folder):
        shutil.rmtree(image_folder)
    if llava_result:
        return jsonify({'message': answer})
    else:
        return jsonify(result)


@app.route('/upload', methods=['POST'])
def upload_file():
    source = None
    if "source" in request.form:
        source = request.form["source"]
    if 'file' not in request.files:
        return 'No file part'

    file = request.files['file']

    if file.filename == '':
        return 'No selected file'

    if file and allowed_file(file.filename):
        headers = {'Context-Type': 'v1/ingest/file'}
        filename = secure_filename(file.filename)
        local_file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(local_file_path)

        with open(local_file_path, "rb") as local_file:
            file_content = local_file.read()
            print(file_content)
            if source == "bus_activity":
                _bus_attendance.update_bus_info_from_json(file_content)
            else:
                _bus_attendance.update_attendance_from_json(file_content)

        with open(BUS_ATTENDANCE_FILE, "w+") as json_file:
            formatted_json = json.loads(_bus_attendance.to_json())
            json.dump(formatted_json, json_file, indent=4)

        with open(BUS_ATTENDANCE_FILE, "rb") as local_bus_attendance_file:
            response = requests.post(PRIVATE_GPT_INGESTION_URL, headers=headers,
                                     files={'file': (BUS_ATTENDANCE_FILE_NAME, local_bus_attendance_file)})

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
            _bus_attendance = init_or_reset()
            return "deleted files size: " + str(len(doc_ids))
        else:
            return "no data in reponse"
    else:
        return "status code: " + str(response.status_code)


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


@app.route('/missing_stop', methods=['GET'])
def predict_missing_stop():
    prediction = None
    with open(BUS_ATTENDANCE_FILE, "rb") as local_bus_attendance_file:
        _bus_attendance.from_json(local_bus_attendance_file.read())
    passengers = _bus_attendance.get_passenger_list_who_missed_the_stop()
    if passengers:
        passenger_names = [passenger.name for passenger in passengers]
        name_list = ', '.join(passenger_names)
        place = passengers[0].final_destination
        prediction = make_prediction("{} missed the disembarkation location at {}, "
                                     "please generate a warning message to them".format(name_list, place),
                                     use_context = False)
    if prediction:
        answer = jsonify({'answer': prediction})
    else:
        answer = jsonify({'answer': "None"})
    return answer


def make_prediction(question: str, radio_id="user", use_context=True):
    headers = {"Content-Type": "application/json"}
    short_summary = ("By referring to the last activity by time, provide a short and straight to-the-point answer."
                     "Please respond NONE if no answer fits the question. "
                     "Do not provide any explanation, source of context, reasoning, or justification for your answer!")
    # now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    query = "{} {}".format(short_summary, question)

    data = {
        "messages": [
            {
                "role": "system",
                "content": "As a bus driver assistant proficient in analyzing JSON data, "
                           "your primary goal is to ensure that all passengers reach their designated stops safely."
                           "You will be provided with real-time JSON data containing information about the passengers, "
                           "their intended stops, and the current location of the bus. "
                           "You need to Parse and analyze JSON data in real-time."
                           "The last index of the bus activities and passenger activities always "
                           "is the latest and current activity."
                           "Determine which passengers need to disembark at the bus current location."
                           "Alert passengers who may miss their stop. Provide detail information of every passenger"
            },
            {
                "role": radio_id,
                "content": query
            }
        ],
        "stream": False,
        "use_context": use_context
    }

    response = requests.post(PRIVATE_GPT_COMPLETION_URL, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        prediction = response.json()
        return prediction["choices"][0]["message"]["content"]
    else:
        return response.status_code


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5044)
