package com.ressphere.nlp

import android.util.Log
import com.google.mlkit.nl.entityextraction.EntityExtraction
import com.google.mlkit.nl.entityextraction.EntityExtractionParams
import com.google.mlkit.nl.entityextraction.EntityExtractor
import com.google.mlkit.nl.entityextraction.EntityExtractorOptions
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import kotlin.coroutines.CoroutineContext

class EntityExtractorUsecase(
    private val response: (ans: String) -> Unit,
    private val scope: CoroutineScope,
    private val coroutineDispatchContext: CoroutineContext = Dispatchers.Default
) : NLPExecutor {
    @set:Synchronized
    @get:Synchronized
    private var isEntityExtractionModelDownloadCompleted = false

    private var entityExtractor: EntityExtractor? = null
    private val mutex = Mutex()

    override fun init() {
        scope.launch(coroutineDispatchContext) {
            mutex.withLock {
                entityExtractor = EntityExtraction.getClient(
                    EntityExtractorOptions.Builder(EntityExtractorOptions.ENGLISH)
                        .build()
                )

                entityExtractor
                    ?.downloadModelIfNeeded()
                    ?.addOnSuccessListener { _ ->
                        isEntityExtractionModelDownloadCompleted = true
                        /* Model downloading succeeded, you can call extraction API here. */
                        Log.d(TAG, "Downloaded the model")
                    }
                    ?.addOnFailureListener { _ -> /* Model downloading failed. */ }
            }
        }
    }


    override fun execute(question: String) {
        if (isEntityExtractionModelDownloadCompleted) {
            val params =
                EntityExtractionParams.Builder(question)
                    .build()
            entityExtractor?.annotate(params)
                ?.addOnSuccessListener { entityAnnotations ->
                    for (entityAnnotation in entityAnnotations) {
                        for (entity in entityAnnotation.entities) {
                            scope.launch(coroutineDispatchContext) {
                                response("entity: $entity")
                            }

                        }
                        scope.launch(coroutineDispatchContext) {
                            response("annotated text: ${entityAnnotation.annotatedText}")
                        }
                    }

                    // Annotation process was successful, you can parse the EntityAnnotations list here.
                }
                ?.addOnFailureListener {
                    // Check failure message here.
                    Log.e(TAG, "analyzeMessage: $it", it)
                }
        }
    }

    override fun close() {
        scope.launch(coroutineDispatchContext) {
            mutex.withLock {
                entityExtractor?.close()
                entityExtractor = null
            }
        }
    }

    companion object {
        private const val TAG = "EntityExtractorUsecase"
    }
}