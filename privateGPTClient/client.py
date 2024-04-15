import asyncio
import pprint
import websockets

from flask import Flask, request, jsonify
from requests import Response
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
from enum import Enum

from model.WebSocketMessageAttribute import Role

app = Flask(__name__)
UPLOAD_FOLDER = 'database'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'json'}
IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg'}
VIDEO_EXTENSIONS = {'mp4'}
AUDIO_EXTENSIONS = {'wav'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

PRIVATE_GPT_COMPLETION_URL = "http://0.0.0.0:8001/v1/chat/completions"
PRIVATE_GPT_INGESTION_URL = "http://0.0.0.0:8001/v1/ingest/file"
PRIVATE_GPT_INGESTION_LIST_URL = "http://0.0.0.0:8001/v1/ingest/list"
PRIVATE_GPT_DEL_INGESTION_URL = "http://0.0.0.0:8001/v1/ingest"
BUS_ATTENDANCE_FILE_NAME = "bus_attendance.json"
BUS_ATTENDANCE_FILE = os.path.join(UPLOAD_FOLDER, BUS_ATTENDANCE_FILE_NAME)

WS_URI = "ws://{}:{}".format("0.0.0.0", 2277)


class FileSourceType(Enum):
    BUS_ACTIVITY = "bus_activity"
    OBJECT_DETECTION_EVENTS = "object_detection_events"
    PASSENGER_ACTIVITY = "pessenger_activity"


def init_bus_attendance():
    bus = Bus(plate_number='', bus_activities=[])
    passengers: list[Passenger] = []
    bus_attendance = BusAttendance(bus, passengers, [])
    if os.path.exists(BUS_ATTENDANCE_FILE):
        with open(BUS_ATTENDANCE_FILE, "rb") as f:
            bus_attendance.from_json(f.read())
    return bus_attendance


def reset_bus_attendance():
    if os.path.exists(BUS_ATTENDANCE_FILE):
        os.remove(BUS_ATTENDANCE_FILE)
    return init_bus_attendance()


_bus_attendance = init_bus_attendance()


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def is_image(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in IMAGE_EXTENSIONS
        
def is_audio(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in AUDIO_EXTENSIONS   


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
        filename = secure_filename(file.filename)
        local_file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(local_file_path)

        with open(local_file_path, "rb") as local_file:
            file_content = local_file.read()
            print(file_content)
            print("FileSourceType source: {}".format(str(source)))
            if source and source == FileSourceType.BUS_ACTIVITY.value:
                _bus_attendance.update_bus_info_from_json(file_content)
            elif source and source == FileSourceType.OBJECT_DETECTION_EVENTS.value:
                _bus_attendance.update_object_detection_events_from_json(file_content)
            else:
                _bus_attendance.update_attendance_from_json(file_content)

        delete_privategpt_storage()
        response = ingest_context_to_llm(BUS_ATTENDANCE_FILE_NAME,
                                         BUS_ATTENDANCE_FILE,
                                         json.loads(_bus_attendance.to_json()))

        if response.status_code == 200:
            if source == FileSourceType.BUS_ACTIVITY.value:
                print("ws")
                asyncio.run(send_message_to_passenger_with_missing_stop())
                asyncio.run(send_message_to_video_assistance())
                asyncio.run(send_message_to_alert_vehicle_nearby())
            if source == FileSourceType.OBJECT_DETECTION_EVENTS.value:
                asyncio.run(send_message_to_alert_vehicle_nearby())
            return 'File uploaded successfully'
    return 'Invalid file type'


async def send_message_to_passenger_with_missing_stop():
    try:
        print("send_message_to_passenger_with_missing_stop")
        async with websockets.connect(WS_URI) as websocket:
            bus_activity = _bus_attendance.bus.bus_activities[-1] if _bus_attendance.bus.bus_activities else None
            is_bus_ready_to_go = bus_activity and bus_activity.activity == BusStatus.DOOR_CLOSE
            if not is_bus_ready_to_go:
                print("send_message_to_passenger_with_missing_stop halt!!!!")
                return

            response = predict_missing_stop()
            if response.status_code != 200:
                return

            message = response.json
            answer = message.get("answer", "none")
            if answer.lower() == "none":
                return

            formatted_message = f"{Role.SYSTEM.value};{Role.BUS_DRIVER.value};{answer}"
            await websocket.send(formatted_message)
    except ConnectionRefusedError:
        print("web socket server not running")


async def send_message_to_video_assistance():
    try:
        async with websockets.connect(WS_URI) as websocket:
            bus_activity = _bus_attendance.bus.bus_activities[-1] if _bus_attendance.bus.bus_activities else None
            is_bus_stop_sign_on = bus_activity and (bus_activity.activity == BusStatus.STOP or bus_activity.activity == BusStatus.WAITING)
            message = "stop sign showed" if is_bus_stop_sign_on else "stop sign hidden"

            formatted_message = f"{Role.SYSTEM.value};{Role.VIDEO_ASSISTANCE.value};{message}"
            await websocket.send(formatted_message)
    except ConnectionRefusedError:
        print("web socket server not running")
    pass


async def send_message_to_alert_vehicle_nearby():
    print("send_message_to_alert_vehicle_nearby!!!!")
    try:
        async with websockets.connect(WS_URI) as websocket:
            bus_activity = _bus_attendance.bus.bus_activities[-1] if _bus_attendance.bus.bus_activities else None
            is_bus_stop_sign_on = bus_activity and (bus_activity.activity == BusStatus.STOP or bus_activity.activity == BusStatus.WAITING)
            if bus_activity and bus_activity.activity == BusStatus.DOOR_CLOSE: return
            if not is_bus_stop_sign_on: return
            response = check_safe_to_exit()
            if response.status_code != 200:
                print("send_message_to_alert_vehicle_nearby halt!!!!")
                return

            message = response.json
            answer = message.get("answer", "none")
            if answer.lower() == "none":
                answer = "\"No vehicles detected nearby, passengers are safe to board and alight the bus.\""

            formatted_message = f"{Role.SYSTEM.value};{Role.BUS_DRIVER.value};{answer}"
            await websocket.send(formatted_message)
    except ConnectionRefusedError:
        print("web socket server not running")
    pass

def ingest_context_to_llm(filename: str, local_file_path: str, formatted_json: str) -> Response:
    headers = {'Context-Type': 'v1/ingest/file'}
    with open(local_file_path, "w+") as json_file:
        #json.dump(formatted_json, json_file, separators=(',', ':'))
        json.dump(formatted_json, json_file, indent=4)

    with open(local_file_path, "rb") as local_bus_attendance_file:
        response = requests.post(PRIVATE_GPT_INGESTION_URL, headers=headers,
                                 files={'file': (filename, local_bus_attendance_file)})
        return response


@app.route('/clean', methods=['POST'])
def clean_files():
    _bus_attendance = reset_bus_attendance()
    return delete_privategpt_storage()


def delete_privategpt_storage():
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
        return "status code: " + str(response.status_code)

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' in request.files and is_audio(request.files['file'].filename):
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
    passenger_name_list, destination= missing_stop()
    if passenger_name_list and destination:
        prediction = "Warning! {}, bus has reached {}, please disembark NOW!".format(passenger_name_list, destination)
    if prediction:
        answer = jsonify({'answer': prediction})
    else:
        answer = jsonify({'answer': "All the passengers had disembarked. Good to go now!"})
    return answer


def missing_stop() -> (str, str):
    if not os.path.exists(BUS_ATTENDANCE_FILE): return None, None
    with open(BUS_ATTENDANCE_FILE, "rb") as local_bus_attendance_file:
        _bus_attendance.from_json(local_bus_attendance_file.read())
    passengers = _bus_attendance.get_passenger_list_who_missed_the_stop()
    if passengers:
        passenger_names = [passenger.name for passenger in passengers]
        name_list = ', '.join(passenger_names)
        place = passengers[0].final_destination
        return name_list, place
    return None, None


@app.route('/check_safe_to_alight', methods=['POST'])
def check_safe_to_exit():
    is_dangerous, count_of_vehicle_nearby = _bus_attendance.get_list_of_last_vehicle_movement_on_bus_last_stop()
    if is_dangerous:
        prediction = make_prediction("There {} vehicle detected moving near the bus, "
                                     "please generate a warning message to the bus driver "
                                     "and passengers who alighting the bus".format(count_of_vehicle_nearby),
                                     use_context=False)
        return jsonify({"answer":prediction})
    return jsonify({'answer': "None"})


def format_traffic_violation_query() -> str:
    vehicle_list =_bus_attendance.vehicles_violate_stop_sign()
    if len(vehicle_list) > 0:
        violation_info = "following vehicle was recorded violating the stop sign. \n"
        for vehicle in vehicle_list:
            violation_info += "At {}, {} violating the stop sign at {} " \
                              "because the status was recorded as \"Nearby\""\
                .format(vehicle.time, vehicle.plate_number, vehicle.location)
    else:
        violation_info = "No violation detected."
    print("violation_info: {}".format(violation_info))
    return violation_info


def format_who_on_the_bus() -> str:
    passengers = _bus_attendance.who_on_the_bus()
    message = ""
    for passenger in passengers:
        message += "{},".format(passenger.name)
    message = "{} are the passengers on the bus".format(message) if len(message) > 0 else "nobody on the bus"
    print("who are on the bus: "+message)
    return message


def format_who_not_on_the_bus() -> str:
    passengers = _bus_attendance.who_not_on_bus()
    message = ""
    for passenger in passengers:
        message += "{} disembarked at {} around {},".format(passenger.name,
                                                            passenger.passenger_activities[-1].location,
                                                            passenger.passenger_activities[-1].time)
    message = "{}".format(message) if len(message) > 0 else "nobody disembarked the bus"
    print("who are not on the bus: "+message)
    return message


def make_prediction(question: str, radio_id="user", use_context=True):
    headers = {"Content-Type": "application/json"}
    short_summary = ("By referring to the last activity by time, provide a short and straight to-the-point answer."
                     "Please respond NONE if no answer fits the question. "
                     "Do not provide any explanation, source of context, reasoning, or justification for your answer! Question:")
    # now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    question = "{} {}".format(short_summary, question)
    print("question: {}".format(question))

    passenger_list, place = missing_stop()
    if passenger_list and len(passenger_list) > 0:
        missing_bus_stop = "passengers who may miss: {}".format(passenger_list)
    else:
        missing_bus_stop = "Nobody"
    print(missing_bus_stop)
    is_dangerous, count_of_vehicle_nearby = _bus_attendance.get_list_of_last_vehicle_movement_on_bus_last_stop()
    is_dangerous_message = "Dangerous!!!! {} vehicles detected nearby.".format(count_of_vehicle_nearby) \
        if is_dangerous else "safe to disembark"

    print("is_dangerous_message: {}".format(is_dangerous_message))

    data = {
        "messages": [
            {
                "role": "system",
                "content": "As a bus driver assistant proficient in analyzing JSON data, "
                           "your primary goal is to ensure that all passengers reach their designated stops safely. "
                           "You will be provided with real-time JSON data containing information about the passengers, "
                           "current bus event and traffic around the bus. "
                           "You need to Parse and analyze JSON data in real-time. "
                           "The last index of the bus activities and passenger activities always is the latest and current activity. "
                           "Determine which passengers need to disembark at the bus current location. "
                           "Alert passengers who may miss their stop. Provide detail information of every passenger. "
                           "Alert the passengers and driver when there is traffic nearby the bus to avoid any unexpected traffic accident."
            },
            {
                "role": "user",
                "content": "<s>[INST]Who violate the stop sign?[/INST]{}</s>".format(format_traffic_violation_query())
            },
            {
                "role": "user",
                "content": "<s>[INST]Who are on the bus?[/INST]{}</s>".format(format_who_on_the_bus())
            },
            {
                "role": "user",
                "content": "<s>[INST]Who disembarked from the bus?[/INST]{}</s>".format(format_who_not_on_the_bus())
            },
            {
                "role": "user",
                "content": "<s>[INST]Who may miss their stop?[/INST]{}</s>".format(missing_bus_stop)
            },
            {
                "role": "user",
                "content": "<s>[INST]Is it dangerous to disembark or boarding the bus now?[/INST]{}</s>".format(is_dangerous_message)
            },
            {
                "role": "user",
                "content": "<s>[INST]Please answer \"Sorry, I do not have any answer.\" when no answer can be determined.[/INST]{}</s>".format(
                    "Sorry, I do not have any answer.")
            },
            {
                "role": radio_id,
                "content": question
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
