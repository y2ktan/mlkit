package com.ressphere.alertmanager.data

import kotlinx.coroutines.flow.Flow

interface RealtimeMessagingClient {
    fun getAlertStateStream(urlString: String): Flow<String>
    suspend fun sendMessage(message: String)
    suspend fun close()
}