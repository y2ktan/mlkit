package com.ressphere.alertmanager.data

import io.ktor.client.*
import io.ktor.client.features.websocket.*
import io.ktor.client.request.*
import io.ktor.http.cio.websocket.*
import kotlinx.coroutines.flow.*
import kotlinx.serialization.decodeFromString
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json

class KtorRealtimeMessageClient(
    private val client: HttpClient
): RealtimeMessagingClient {

    private var session: WebSocketSession? = null

    override fun getAlertStateStream(urlString: String): Flow<MessageInfo> {
        return flow {
            session = client.webSocketSession {
                url(urlString)
            }
            val alertMessage = session!!
                .incoming
                .consumeAsFlow()
                .filterIsInstance<Frame.Text>()
                .mapNotNull { Json.decodeFromString<MessageInfo>(it.readText()) }

            emitAll(alertMessage)
        }
    }

    override suspend fun sendMessage(message: MessageInfo) {
        session?.outgoing?.send(
            Frame.Text(Json.encodeToString(message))
        )
    }

    override suspend fun close() {
        session?.close()
        session = null
    }
}