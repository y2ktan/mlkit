package com.ressphere.speech2text

import android.os.Bundle
import android.speech.RecognitionListener
import android.speech.SpeechRecognizer
import android.util.Log
import kotlinx.coroutines.CoroutineDispatcher
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharedFlow
import kotlinx.coroutines.flow.asSharedFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class SpeechRecognitionListener(dispatcher: CoroutineDispatcher = Dispatchers.Default) : RecognitionListener {
    private val _flow = MutableSharedFlow<String>()
    private val job = SupervisorJob()
    private val coroutineScope = CoroutineScope(dispatcher+job)
    val flow: SharedFlow<String> = _flow.asSharedFlow()

    private val _endOfSpeech = MutableStateFlow(true)
    val endOfSpeech = _endOfSpeech.asStateFlow()
    override fun onReadyForSpeech(params: Bundle?) {
        // Called when the speech recognition is ready to start
        Log.d("vcfr67", "onReadyForSpeech")
        _endOfSpeech.value = false
    }

    override fun onBeginningOfSpeech() {
        Log.d("vcfr67", "onBeginningOfSpeech")
        // Called when the user starts speaking
        _endOfSpeech.value = false
    }

    override fun onRmsChanged(rmsdB: Float) {
        // Called when the RMS value of the input audio changes
    }

    override fun onBufferReceived(buffer: ByteArray?) {
        // Called when partial recognition results are available
    }

    override fun onEndOfSpeech() {
        Log.d("vcfr67", "onEndOfSpeech")
        _endOfSpeech.value = true
        // Called when the user stops speaking
    }

    override fun onError(error: Int) {
        // Called when an error occurs during speech recognition
        Log.d("vcfr67", "onError: $error")
        _endOfSpeech.value = true
    }

    override fun onResults(results: Bundle?) {
        // Called when the final recognition results are available
        Log.d("vcfr67", "results: ${results?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)}")
        results?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)?.let {
            coroutineScope.launch {
                _flow.emit(it.first())
            }
        }

    }

    override fun onPartialResults(partialResults: Bundle?) {

    }

    override fun onEvent(eventType: Int, params: Bundle?) {
        //Log.d("vcfr67", "event: $eventType")
        // Called when an event related to the recognition is triggered
    }
}