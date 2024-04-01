package com.ressphere.alertmanager.di

import com.ressphere.alertmanager.data.KtorRealtimeMessageClient
import com.ressphere.alertmanager.data.RealtimeMessagingClient
import io.ktor.client.HttpClient
import io.ktor.client.engine.cio.CIO
import io.ktor.client.features.logging.Logging
import io.ktor.client.features.websocket.WebSockets

object Component {
    private val provideHttpClient by lazy {
        HttpClient(CIO) {
            install(Logging)
            install(WebSockets)
        }
    }
    val provideRealTimeMessageClient: RealtimeMessagingClient by lazy {
        KtorRealtimeMessageClient(provideHttpClient)
    }
}