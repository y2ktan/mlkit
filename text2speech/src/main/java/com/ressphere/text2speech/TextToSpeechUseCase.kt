package com.ressphere.text2speech

import android.content.Context
import android.speech.tts.TextToSpeech
import android.speech.tts.TextToSpeech.OnInitListener
import android.util.Log
import java.util.Locale

class TextToSpeechUseCase(context: Context) {
    private val listener:TextToSpeech.OnInitListener =
        OnInitListener { status ->
            if (status == TextToSpeech.SUCCESS) {
                val result = tts.setLanguage(Locale.US)
                if (result == TextToSpeech.LANG_MISSING_DATA || result == TextToSpeech.LANG_NOT_SUPPORTED) {
                    Log.e("TTS", "Language not supported")
                }
            } else {
                Log.e("TTS", "Initialization failed")
            }
        }

    private val tts: TextToSpeech by lazy {
        TextToSpeech(context, listener)
    }

    fun speak(message: String) {
        tts.speak(message, TextToSpeech.QUEUE_FLUSH, null, null)
    }
}