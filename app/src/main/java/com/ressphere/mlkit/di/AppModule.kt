package com.ressphere.mlkit.di

import android.app.Application
import com.ressphere.alertmanager.AlertMessageUsecase
import com.ressphere.alertmanager.ReceiveAlertMessageUseCase
import com.ressphere.domain.HttpRoutes
import com.ressphere.nlp.NLPUsecase
import com.ressphere.speech2text.SpeechRecognitionListener
import com.ressphere.speech2text.SpeechToTextUseCase
import com.ressphere.text2speech.TextToSpeechUseCase

interface AppModule {
    val speechToTextUseCase: SpeechToTextUseCase
    val speechRecognitionListener: SpeechRecognitionListener
    val nlpUseCase: NLPUsecase
    val textToSpeechUseCase: TextToSpeechUseCase
    val alertMessageUsecase: AlertMessageUsecase
    val receiveAlertMessageUsecase: ReceiveAlertMessageUseCase
}

class AppModuleImpl(
    private val application: Application
) : AppModule {
    override val speechToTextUseCase: SpeechToTextUseCase by lazy {
        SpeechToTextUseCase(
            application.applicationContext,
            speechRecognitionListener
        )
    }

    override val textToSpeechUseCase: TextToSpeechUseCase by lazy {
        TextToSpeechUseCase(
            application.applicationContext
        )
    }
    override val alertMessageUsecase: AlertMessageUsecase by lazy {
        AlertMessageUsecase()
    }

    override val receiveAlertMessageUsecase: ReceiveAlertMessageUseCase by lazy {
        ReceiveAlertMessageUseCase(HttpRoutes.BASE_URL)
    }


    override val speechRecognitionListener: SpeechRecognitionListener by lazy {
        SpeechRecognitionListener()
    }

    override val nlpUseCase: NLPUsecase by lazy {
        NLPUsecase(application)
    }
}