package com.ressphere.alertmanager.data

import io.ktor.client.*
import io.ktor.client.features.websocket.*
import io.ktor.client.request.*
import io.ktor.http.cio.websocket.*
import kotlinx.coroutines.flow.*

class KtorRealtimeMessageClient(
    private val client: HttpClient
): RealtimeMessagingClient {

    private var session: WebSocketSession? = null

    override fun getAlertStateStream(urlString: String): Flow<String> {
        return flow {
            session = client.webSocketSession {
                url(urlString)
            }
            val alertMessage = session!!
                .incoming
                .consumeAsFlow()
                .filterIsInstance<Frame.Text>()
                .mapNotNull { it.readText() }

            emitAll(alertMessage)
        }
    }

    override suspend fun sendMessage(message: String) {
        session?.outgoing?.send(
            Frame.Text("message#$message")
        )
    }

    override suspend fun close() {
        session?.close()
        session = null
    }
}