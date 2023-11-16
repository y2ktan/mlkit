package com.ressphere.nlp

import android.content.Context
import android.util.Log
import com.ressphere.dataset.LoadDataSetClient
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Deferred
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.async
import kotlinx.coroutines.launch
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import kotlinx.coroutines.withContext
import org.tensorflow.lite.task.text.qa.QaAnswer
import kotlin.coroutines.CoroutineContext

//task downloadModelFile(type: Download) {
//    src 'https://storage.googleapis.com/download.tensorflow.org/models/tflite/task_library/bert_qa/android/models_tflite_task_library_bert_qa_lite-model_mobilebert_1_metadata_1.tflite'
//    dest project.ext.ASSET_DIR + '/mobilebert.tflite'
//    overwrite false
//}
//
//task downloadQAJson(type: Download) {
//    src 'https://storage.googleapis.com/download.tensorflow.org/models/tflite/bert_qa/contents_from_squad.json'
//    dest project.ext.ASSET_DIR + '/qa.json'
//    overwrite false
//}
//
//task copyTestModel(type: Copy, dependsOn: downloadModelFile) {
//    from project.ext.ASSET_DIR + '/mobilebert.tflite'
//    into project.ext.TEST_ASSETS_DIR
//}

class BertQaUseCase(
    private val context: Context,
    private val response: (ans: String) -> Unit,
    private val scope: CoroutineScope,
    private val coroutineDispatchContext: CoroutineContext = Dispatchers.Default
) : NLPExecutor {
    private val mutex = Mutex()
    private val replyAnswererListener = object : BertQaHelper.AnswererListener {
        override fun onError(error: String) {
            Log.e(TAG, "error: $error")
        }

        override fun onResults(results: List<QaAnswer>?, inferenceTime: Long) {

            results?.let {qaAnswers ->
                for(qaAnswer in qaAnswers) {
                    Log.d(TAG, "result: ${qaAnswer.text}")
                }
                response(qaAnswers.first().text)
            }
        }
    }

    private var bertQaHelper: BertQaHelper? = BertQaHelper(
        context = context,
        answererListener = replyAnswererListener
    )

    override fun close() {
        scope.launch {
            withContext(coroutineDispatchContext) {
                mutex.withLock {
                    bertQaHelper?.clearBertQuestionAnswerer()
                    bertQaHelper = null
                }
            }
        }
    }

    override fun init() {
        scope.launch {
            withContext(coroutineDispatchContext) {
                mutex.withLock {
                    if (bertQaHelper == null) {
                        bertQaHelper = BertQaHelper(
                            context = context,
                            answererListener = replyAnswererListener
                        )
                    }
                }
            }
        }
    }

    private val client = LoadDataSetClient(context)

    private val content: String
        get() {
            return client.loadJson()?.getContents()?.first() ?: ""
        }

    override fun execute(question: String) {
        scope.launch {
            Log.d(TAG, "content: $content")
            bertQaHelper?.answer(content, question)
        }
    }

    companion object {
        private const val TAG = "BertQaUseCase"
    }
}