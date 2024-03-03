import cv2
import glob
import subprocess
from pathlib import Path

# Set paths
LLAVA_EXEC_PATH = "/home/st-stationhigh1/mlkit/h2ogpt/llama.cpp/build/bin/llava-cli"
MODEL_PATH = "ggml-model-q5_k.gguf"
MMPROJ_PATH = "mmproj-model-f16.gguf"
VIDEO_PATH = "database/bus.mp4"
IMAGE_DIR = Path("data", "image")
TXT_DIR = Path("data", "txt")

final_summary_path = TXT_DIR.joinpath("video_summary.txt")

# Create directories if they don't exist
IMAGE_DIR.mkdir(parents=True, exist_ok=True)
TXT_DIR.mkdir(parents=True, exist_ok=True)

# Define prompt
# PROMPT = "Please analyze all of the provided images from a video recorded by the bus security camera and identify whether a road accident has occurred. " \
#     "If an accident is detected, please describe the situation inside the bus. For example, the plate number, " \
#     "types of vehicles involved, the location and the time of the accident, and any visible damage to the vehicles. " \
#     "Please describe the behavior of the people involved including any injuries and casualties in the accident. " \
#     "Please summarize the events depicted on the bus. The summary must be clear, concise, and factual like a police report. " \

PROMPT = "These images are captured from a security camera inside a bus. Please analyze every images and determine if " \
"there is a road accident. If so, describe the situation in a police report format, which shall include " \
"Vehicles involved, Location, Time, Damage, number of injuries and casualties. " \
"The information must be clear, concise, and factual."

# Define bash command
TEMP = 0.2
bash_command = f"{LLAVA_EXEC_PATH} -m {MODEL_PATH} --mmproj {MMPROJ_PATH} --temp {TEMP} -p '{PROMPT}'"

# Open video
video = cv2.VideoCapture(VIDEO_PATH)

# Get video info
fps = video.get(cv2.CAP_PROP_FPS)
frame_count = video.get(cv2.CAP_PROP_FRAME_COUNT)
# image_list_parameter = ""
# Loop over frames
for i in range(int(frame_count)):
    # Read frame
    ret, frame = video.read()

    # Break loop if frame not read correctly
    if not ret:
        break

    # Write frame to disk
    image_path = IMAGE_DIR.joinpath(f"frame_{i}.jpg")
    cv2.imwrite(str(image_path), frame)
    temp = TXT_DIR.joinpath("temp.txt")
    bash_command_cur = f"{bash_command} --image '{image_path}' > '{temp}'"
    process = subprocess.Popen(
        bash_command_cur, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    output, error = process.communicate()
    with open(temp, 'r') as f:
        image_text = f.read()
        content = f"frame_{i}.jpg: " + image_text.split("\n")[-2]
        with open(final_summary_path, 'a') as summary:
            summary.write(content + "\n")
        print("content: " + content)

    #image_list_parameter = image_list_parameter + f"--image '{image_path}' "

# Release video
video.release()

# bash_command_cur = f"{bash_command} {image_list_parameter} > '{final_summary_path}'"
# print(bash_command_cur)
# process = subprocess.Popen(
#     bash_command_cur, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
# )
# output, error = process.communicate()
# with open(final_summary_path, 'r') as f:
#     image_text = f.read()
#     content = image_text.split("\n")[-2]
#     print("content: "+content)

#
# image_paths = sorted(glob.glob(str(IMAGE_DIR.joinpath("*.jpg"))))
#
# for image_path in image_paths:
#     image_name = Path(image_path).stem
#     image_summary_path = TXT_DIR.joinpath(image_name + ".txt")
#     image_list_parameter = image_list_parameter + f"--image '{image_path}' "


# bash_command_cur = f"{bash_command} '{image_list_parameter}' > '{final_summary_path}'"
# process = subprocess.Popen(
#     bash_command_cur, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
# )
# output, error = process.communicate()

# summarize