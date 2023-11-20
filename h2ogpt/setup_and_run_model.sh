#!/bin/bash

H2OGPT_FOLDER="h2ogpt"
H2OGPT_REPO="https://github.com/h2oai/h2ogpt.git"

echo "Please select your Python version:"
echo "1. Python"
echo "2. Python3"
read -p "Enter the number (1/2): " py_version

echo "Please select your pip version:"
echo "1. pip"
echo "2. pip3"
read -p "Enter the number (1/2): " pip_version

case $py_version in
    1) python_cmd="python" ;;
    2) python_cmd="python3" ;;
    *) echo "Invalid option"; exit 1 ;;
esac

case $pip_version in
    1) pip_cmd="pip" ;;
    2) pip_cmd="pip3" ;;
    *) echo "Invalid option"; exit 1 ;;
esac

# If the h2ogpt folder is not available, clone the repo
if [ ! -d "$H2OGPT_FOLDER" ]; then
    git clone "$H2OGPT_REPO"
    cd "$H2OGPT_FOLDER" || exit
    # Install required packages
    $pip_cmd install -r requirements.txt
    $pip_cmd install -r reqs_optional/requirements_optional_langchain.txt
    $pip_cmd install -r reqs_optional/requirements_optional_gpt4all.txt
    $pip_cmd install gradio_client==0.6.1
    $pip_cmd install Flask==2.3.2

    mkdir -p gradio_utils
    if [ -f "../grclient.py" ]; then
        cp ../grclient.py gradio_utils
    else
        # If not, download the grclient.py file
        wget https://raw.githubusercontent.com/h2oai/h2ogpt/main/gradio_utils/grclient.py
        # move the grclient.py file
        mv grclient.py gradio_utils
    fi

    if [ -f "../grclient.py" ]; then
      cp ../h2oclient.py .
    fi
else
    cd "$H2OGPT_FOLDER" || exit
    git pull
fi

# Check the OSTYPE
case "$(uname -s)" in
    Linux*)     terminal_cmd="gnome-terminal --working-directory=\"$PWD\" -- bash -c \"$python_cmd h2oclient.py; read -p \\\"Press enter to exit...\\\"\"" ;;
    Darwin*)    terminal_cmd="osascript -e \"tell app \\\"Terminal\\\" to do script \\\"cd \\\"$PWD\\\"; $python_cmd h2oclient.py; read -p \\\"Press enter to exit...\\\"\\\"\"" ;;
    CYGWIN*|MINGW*|MSYS*)    terminal_cmd="start cmd.exe /k \"cd \\\"$PWD\\\" && $python_cmd h2oclient.py & pause\"" ;;
    *)          echo "Unsupported OS type: $(uname -s)"; exit 1 ;;
esac

# Open a new terminal and run h2oclient.py
eval "$terminal_cmd"

$python_cmd generate.py \
         --base_model=llama \
         --prompt_type=llama2 \
         --model_path_llama=https://huggingface.co/TheBloke/Llama-2-7b-Chat-GGUF/resolve/main/llama-2-7b-chat.Q6_K.gguf \
         --max_seq_len=4096 \
         --gradio_offline_level=1 \
         --share=False \
         --prompt_type=human_bot \
         --langchain_mode=MyData