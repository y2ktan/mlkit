package com.ressphere.speech2text


import android.content.Context
import android.content.Intent
import android.speech.RecognitionListener
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import android.util.Log
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.launchIn
import kotlinx.coroutines.flow.onEach
import kotlinx.coroutines.flow.update
import java.util.Locale

class SpeechToTextUseCase(private val context: Context,
                          private val listener: SpeechRecognitionListener) {
    private val job = SupervisorJob()
    private val scope: CoroutineScope = CoroutineScope(Dispatchers.Default+job)

    private val speechRecognizer: SpeechRecognizer by lazy(LazyThreadSafetyMode.SYNCHRONIZED) {
        SpeechRecognizer.createSpeechRecognizer(context).apply {
            this.setRecognitionListener(listener)
        }
    }


    private val _isRecording = MutableStateFlow(false)
    val isRecording = _isRecording.asStateFlow()

    init {
        listener.endOfSpeech.onEach { isEndOfSpeech ->
            Log.d("vcfr67", "endOfSpeech: $isEndOfSpeech")
            _isRecording.value = !isEndOfSpeech
        }.launchIn(scope)
    }

    fun startListening() {
        if(_isRecording.value) return
        if (SpeechRecognizer.isRecognitionAvailable(context)) {
            val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH)
            intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE, Locale.getDefault())
            intent.putExtra(RecognizerIntent.EXTRA_PARTIAL_RESULTS, true)
            speechRecognizer.startListening(intent)
            _isRecording.value = true
        } else {
            Log.e("SpeechToText", "Speech recognition not available on this device.")
        }
    }

    fun stopListening() {
        speechRecognizer.cancel()
        _isRecording.value = false
    }
}