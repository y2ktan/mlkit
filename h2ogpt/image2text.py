import glob
import subprocess
from pathlib import Path

# Set paths
LLAVA_EXEC_PATH = "/home/st-stationhigh1/mlkit/h2ogpt/llama.cpp/build/bin/llava-cli"
MODEL_PATH = "ggml-model-q5_k.gguf"
MMPROJ_PATH = "mmproj-model-f16.gguf"
DATA_DIR = "data"
IMAGE_DIR = Path(DATA_DIR, "image")
TXT_DIR = Path(DATA_DIR, "txt")

# Read image paths
# image_paths = sorted(glob.glob(str(IMAGE_DIR.joinpath("*.jpg"))))
image_paths = ["data/image/faqs-what-happens-to-your-body-in-a-car-crash-2.jpg", "data/image/india-skoda-license-plate.jpg"]
#image_paths = ["data/image/india-skoda-license-plate.jpg"]

# Define prompt
PROMPT = "What is the vehicle license plate number?"
PROMPT_FOR_STOP_SIGN = ("Is there any stop sign attached to the bus? If yes just respond True, if no just respond "
                        "False, with just one word")
PROMPT_FOR_CAR_PLATE_RECOGNITION = "extract and display only the license plate number, no sentence and no grammar"
# Define bash command
TEMP = 1
bash_command = f"{LLAVA_EXEC_PATH} -m {MODEL_PATH} --mmproj {MMPROJ_PATH} --temp {TEMP} -p '{PROMPT}'"

# Loop over images and generate text summaries
for image_path in image_paths:
    print("image_path: "+image_path)
    image_name = Path(image_path).stem
    image_summary_path = TXT_DIR.joinpath(image_name + ".txt")

    bash_command_cur = f"{bash_command} --image '{image_path}' > '{image_summary_path}'"

    process = subprocess.Popen(
        bash_command_cur, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    output, error = process.communicate()

    print(f"Return code: {process.returncode}")
    print(error)
