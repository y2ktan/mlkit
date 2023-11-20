package com.ressphere.domain

import android.util.Log
import com.ressphere.domain.dto.GPTRequest
import com.ressphere.domain.dto.GPTResponse
import io.ktor.client.*
import io.ktor.client.engine.android.Android
import io.ktor.client.features.*
import io.ktor.client.features.json.JsonFeature
import io.ktor.client.features.json.serializer.KotlinxSerializer
import io.ktor.client.features.logging.LogLevel
import io.ktor.client.features.logging.Logging
import io.ktor.client.request.*
import io.ktor.http.*

interface H2OPostsService {
    suspend fun postQuestion(gptRequest: GPTRequest): GPTResponse?
    companion object {
        fun create(): H2OPostsService {
            return H2OPostsServiceImpl(
                client = HttpClient(Android) {
                    install(Logging) {
                        level = LogLevel.ALL
                    }
                    install(JsonFeature) {
                        serializer = KotlinxSerializer()
                    }
                }
            )
        }
    }
}

class H2OPostsServiceImpl(private val client: HttpClient): H2OPostsService {
    override suspend fun postQuestion(gptRequest: GPTRequest): GPTResponse? {
        return try {
            client.post<GPTResponse> {
                url(HttpRoutes.PREDICT)
                contentType(ContentType.Application.Json)
                body = gptRequest
            }
        } catch(e: RedirectResponseException) {
            Log.e(TAG, "Error: ${e.response.status.description}")
            GPTResponse("Error: ${e.response.status.description}")
        } catch(e: ClientRequestException) {
            // 4xx - responses
            Log.e(TAG, "Error: ${e.response.status.description}")
            GPTResponse("Error: ${e.response.status.description}")
        } catch(e: ServerResponseException) {
            // 5xx - responses
            Log.e(TAG, "Error: ${e.response.status.description}")
            GPTResponse("Error: ${e.response.status.description}")
        } catch(e: Exception) {
            Log.e(TAG, "Error: ${e.message}")
            GPTResponse("Error: ${e.message}")
        }
    }

    companion object {
        private const val TAG = "H2OPostsServiceImpl"
    }

}