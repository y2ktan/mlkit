import os

import speech_recognition as sr
import io
import wave
import pyaudioconvert as pac
import json
import uuid
from vosk import Model, KaldiRecognizer

MODEL_PATH = "vosk-model-small-en-us-0.15"


def speech_to_text(audio_source) -> str:
    recognizer = KaldiRecognizer(Model(MODEL_PATH), 16000)

    source_audio_file = str(uuid.uuid4()) + ".wav"
    target_audio_file = str(uuid.uuid4()) + ".wav"
    audio_source.save(source_audio_file)

    pac.convert_wav_to_16bit_mono(source_audio_file, target_audio_file)
    with wave.open(target_audio_file) as wav_file:
        audio_data = wav_file.readframes(wav_file.getnframes())
    recognizer.AcceptWaveform(audio_data)
    result = recognizer.Result()
    res = json.loads(result)
    print(res["text"])
    os.remove(source_audio_file)
    os.remove(target_audio_file)
    return res["text"]