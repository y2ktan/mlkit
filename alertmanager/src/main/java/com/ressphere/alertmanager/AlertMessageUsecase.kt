package com.ressphere.alertmanager

import com.ressphere.alertmanager.di.Component
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch

class AlertMessageUsecase(
    private val scope: CoroutineScope = CoroutineScope(Dispatchers.IO)
) {
    fun send(message: String) = scope.launch {
        Component.provideRealTimeMessageClient.sendMessage(message)
    }
}