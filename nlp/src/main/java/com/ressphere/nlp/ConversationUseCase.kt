package com.ressphere.nlp

import android.util.Log
import com.google.mlkit.nl.smartreply.SmartReply
import com.google.mlkit.nl.smartreply.SmartReplyGenerator
import com.google.mlkit.nl.smartreply.SmartReplySuggestion
import com.google.mlkit.nl.smartreply.TextMessage
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import kotlinx.coroutines.withContext
import kotlin.coroutines.CoroutineContext

class ConversationUseCase(private val response: (ans: String)->Unit,
                          private val userId:String = "VP",
                          private val scope: CoroutineScope,
                          private val coroutineDispatchContext: CoroutineContext = Dispatchers.Default
    ): NLPExecutor {
    private var smartReplyGenerator: SmartReplyGenerator? = null
    private val mutex = Mutex()

    private val conversation = mutableListOf<TextMessage>()
    override fun execute(question: String) {
        scope.launch(coroutineDispatchContext) {
            conversation.add(
                TextMessage.createForRemoteUser(
                    question,
                    System.currentTimeMillis(), userId
                )
            )

            val suggestionsDeferred = CompletableDeferred<List<SmartReplySuggestion>>()

            smartReplyGenerator?.suggestReplies(conversation)
                ?.addOnSuccessListener { result ->
                    Log.d(TAG, "suggest reply success")
                    for (suggestion in result.suggestions) {
                        Log.d(TAG, "reply: $suggestion")
                    }
                    suggestionsDeferred.complete(result.suggestions)
                }
                ?.addOnFailureListener { exception ->
                    Log.d(TAG, "suggest reply failed")
                    suggestionsDeferred.completeExceptionally(exception)
                }
            return@launch withContext(Dispatchers.Default) {
                try {
                    val suggestions = suggestionsDeferred.await()
                    response(suggestions.first().text)
                } catch (e: Exception) {
                    Log.e(TAG, "Failed to get any suggestion ${e.message}")
                }
            }
        }
    }

    override fun init() {
        scope.launch(coroutineDispatchContext) {
            mutex.withLock {
                if (smartReplyGenerator == null) {
                    smartReplyGenerator = SmartReply.getClient()
                }
            }
        }
    }

    override fun close() {
        scope.launch(coroutineDispatchContext) {
            mutex.withLock {
                smartReplyGenerator?.close()
                smartReplyGenerator = null
            }
        }
    }

    companion object {
        private const val TAG = "NLPUsecase"
    }
}