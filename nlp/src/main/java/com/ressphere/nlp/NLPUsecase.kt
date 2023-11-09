package com.ressphere.nlp

import android.app.Application
import android.util.Log
import com.ressphere.dataset.LoadDataSetClient
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Deferred
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.async
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

    private val _vpReply = MutableSharedFlow<String>()
    val vpReply = _vpReply.asSharedFlow()

    private val reply: (answer: String) -> Unit = {
        scope.launch {
            withContext(coroutineContext) {
                Log.d(TAG, "question: $it")
                _vpReply.emit(it)
            }
        }
    }


    private val bertQaUseCaseExecutor: NLPExecutor by lazy {
        BertQaUseCase(
            app.applicationContext, reply, scope
        )
    }

    private val entityExtractionUseCaseExecutor: NLPExecutor by lazy {
        EntityExtractorUsecase(
            reply, scope, coroutineDispatcherContext
        )
    }


    fun loadBertQa() {
        bertQaUseCaseExecutor.init()
    }

    fun unloadBertQa() {
        bertQaUseCaseExecutor.close()
    }

    fun loadEntityExtractor() {
        entityExtractionUseCaseExecutor.init()
    }

    fun unloadentityExtractor() {
        entityExtractionUseCaseExecutor.close()
    }

    fun answer(question: String) {
        Log.d(TAG, "question: $question")
        //bertQaUseCaseExecutor.execute(question)
        entityExtractionUseCaseExecutor.execute(question)
    }

    companion object {
        private const val TAG = "NLPUsecase"
    }
}