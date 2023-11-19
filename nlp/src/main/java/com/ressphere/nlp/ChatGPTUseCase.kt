package com.ressphere.nlp

import android.content.Context
import com.ressphere.di.NlpAppModule
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlin.coroutines.CoroutineContext

class ChatGPTUseCase(
    private val response: (ans: String?) -> Unit,
    private val scope: CoroutineScope,
    private val coroutineDispatchContext: CoroutineContext = Dispatchers.Default
): NLPExecutor {
    override fun execute(question: String) {
        scope.launch(coroutineDispatchContext) {
            val result = NlpAppModule.gptGateway.ask(question)
            response(result)
        }
    }

    override fun close() {

    }
}