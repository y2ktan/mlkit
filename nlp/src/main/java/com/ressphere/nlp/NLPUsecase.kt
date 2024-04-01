package com.ressphere.nlp

import android.app.Application
import android.util.Log
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.asSharedFlow
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import kotlin.coroutines.CoroutineContext


class NLPUsecase(
    app: Application,
    coroutineDispatcherContext: CoroutineContext = Dispatchers.Default

) {

    private val scope: CoroutineScope = CoroutineScope(coroutineDispatcherContext)

    private val _vpReply = MutableSharedFlow<String?>()
    val vpReply = _vpReply.asSharedFlow()

    private val reply: (answer: String?) -> Unit = { answer ->
        scope.launch {
            withContext(coroutineContext) {
                Log.d(TAG, "question: $answer")
                _vpReply.emit(answer)
            }
        }
    }

    private val nlpExecutor: NLPExecutor by lazy {
        ChatGPTUseCase(
            reply,
            scope
        )
    }


//    private val bertQaUseCaseExecutor: NLPExecutor by lazy {
//        BertQaUseCase(
//            app.applicationContext, reply, scope
//        )
//    }
//
//    private val entityExtractionUseCaseExecutor: NLPExecutor by lazy {
//        EntityExtractorUsecase(
//            reply, scope, coroutineDispatcherContext
//        )
//    }
//
//
//    fun loadBertQa() {
//        bertQaUseCaseExecutor.init()
//    }
//
//    fun unloadBertQa() {
//        bertQaUseCaseExecutor.close()
//    }
//
//    fun loadEntityExtractor() {
//        entityExtractionUseCaseExecutor.init()
//    }
//
//    fun unloadentityExtractor() {
//        entityExtractionUseCaseExecutor.close()
//    }

    fun loadNLP() {
        nlpExecutor.init()
    }

    fun unloadNLP() {
        nlpExecutor.close()
    }

    fun ask(question: String) {
        Log.d(TAG, "question: $question")
        //bertQaUseCaseExecutor.execute(question)
        nlpExecutor.execute(question)
    }

    companion object {
        private const val TAG = "NLPUsecase"
    }
}