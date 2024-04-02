package com.ressphere.alertmanager.data

import kotlinx.coroutines.flow.Flow

interface RealtimeMessagingClient {
    fun getAlertStateStream(urlString: String): Flow<MessageInfo>
    suspend fun sendMessage(message: MessageInfo)
    suspend fun close()
}