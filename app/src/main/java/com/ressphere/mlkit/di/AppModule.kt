package com.ressphere.mlkit.di

import android.app.Application
import com.ressphere.nlp.NLPUsecase
import com.ressphere.speech2text.SpeechRecognitionListener
import com.ressphere.speech2text.SpeechToTextUseCase

interface AppModule {
    val speechToTextUseCase: SpeechToTextUseCase
    val speechRecognitionListener: SpeechRecognitionListener
    val nlpUseCase: NLPUsecase
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

    override val speechRecognitionListener: SpeechRecognitionListener by lazy {
        SpeechRecognitionListener()
    }

    override val nlpUseCase: NLPUsecase by lazy {
        NLPUsecase(application)
    }
}