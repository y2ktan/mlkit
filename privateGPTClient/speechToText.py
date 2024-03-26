import speech_recognition as sr


def speech_to_text(audio_source) -> str:
    r = sr.Recognizer()
    with sr.AudioFile(audio_source) as source:
        audio_text = r.listen(source)
    result = r.recognize_google(audio_text)
    print("result: "+result)
    return result