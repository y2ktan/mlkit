package com.ressphere.mlkit

import android.app.Application
import android.util.Log
import androidx.compose.ui.graphics.Color
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import com.ressphere.alertmanager.AlertMessageUsecase
import com.ressphere.alertmanager.ReceiveAlertMessageUseCase
import com.ressphere.domain.HttpRoutes
import com.ressphere.mlkit.MyApplication.Companion.appModule
import com.ressphere.mlkit.data.ChatMessage
import kotlinx.coroutines.CoroutineDispatcher
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.launchIn
import kotlinx.coroutines.flow.onEach
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

class ChatViewModel(app: Application, dispatcher: CoroutineDispatcher): AndroidViewModel(app) {
    private val _sourceMessage = MutableStateFlow<List<ChatMessage>>(arrayListOf())
    val sourceMessage = _sourceMessage.asStateFlow()

    private val alertMessageUsecase: AlertMessageUsecase by lazy {
        AlertMessageUsecase(viewModelScope)
    }
    private val receiveAlertMessageUsecase: ReceiveAlertMessageUseCase by lazy {
        ReceiveAlertMessageUseCase(HttpRoutes.BASE_URL, viewModelScope)
    }

    init {
        viewModelScope.launch(dispatcher) {
            appModule.speechRecognitionListener.flow.onEach { message ->
                _sourceMessage.update {
                    it.plus(ChatMessage("source", "source", message))
                }
            }.launchIn(this)
        }

        viewModelScope.launch(dispatcher) {
            appModule.nlpUseCase.vpReply.onEach {
                val message = it?: "I'm sorry, I don't know"
                _sourceMessage.update { chatMessages ->
                    chatMessages.plus(ChatMessage("source", "vp",
                        message, Color.Blue))
                }
                appModule.textToSpeechUseCase.speak(message)
            }.launchIn(this)
        }

        receiveAlertMessageUsecase.message.onEach { message ->
            _sourceMessage.update { chatMessages ->
                chatMessages.plus(ChatMessage("source", "vp",
                    message, Color.Red))
            }
            appModule.textToSpeechUseCase.speak(message)
        }.launchIn(viewModelScope)
    }

    fun sendLastMessageAsAlertMessage() {
        alertMessageUsecase.send(_sourceMessage.value.last().message)
    }

    fun onRecordStart() {
        Log.d("vcfr67", "onRecordStart: ")
        appModule.speechToTextUseCase.startListening()
    }

    fun onRecordStop() {
        Log.d("vcfr67", "onRecordStop: ")
        appModule.speechToTextUseCase.stopListening()
    }

    override fun onCleared() {
        receiveAlertMessageUsecase.close()
    }

}

class ChatViewModelFactory(
    private val app: Application,
    private val dispatcher: CoroutineDispatcher) : ViewModelProvider.Factory {
    override fun <T : ViewModel> create(modelClass: Class<T>): T {
        if (modelClass.isAssignableFrom(ChatViewModel::class.java)) {
            return ChatViewModel(app, dispatcher) as T
        }
        throw IllegalArgumentException("Unknown ViewModel class")
    }
}