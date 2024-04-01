package com.ressphere.alertmanager

import com.ressphere.alertmanager.di.Component
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.catch
import kotlinx.coroutines.flow.onEach
import kotlinx.coroutines.flow.onStart
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch
import java.net.ConnectException

class ReceiveAlertMessageUseCase(private val urlString: String,
                                   private val scope: CoroutineScope = CoroutineScope(Dispatchers.IO)
    ) {
    private val _isConnecting = MutableStateFlow(false)
    val isConnecting = _isConnecting.asStateFlow()

    private val _showConnectionError = MutableStateFlow(false)
    val showConnectionError = _showConnectionError.asStateFlow()

    val message = Component.provideRealTimeMessageClient.getAlertStateStream(urlString)
        .onStart { _isConnecting.value = true }
        .onEach { _isConnecting.value = false }
        .catch { t -> _showConnectionError.value = t is ConnectException }
        .stateIn(scope, SharingStarted.WhileSubscribed(5000), "")

    fun close() {
        scope.launch {
            Component.provideRealTimeMessageClient.close()
        }
    }



}