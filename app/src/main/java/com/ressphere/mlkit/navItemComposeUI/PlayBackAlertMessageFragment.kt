package com.ressphere.mlkit.navItemComposeUI

import android.content.Context
import android.content.Intent
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.Button
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import com.ressphere.mlkit.SpeechService
import com.ressphere.mlkit.data.ChatMessage

@Composable
fun PlayBackAlertMessageFragment(
    sendLastMessageAsAlertMessage: () -> Unit

) {
    Column(
        modifier = Modifier.fillMaxSize(),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Button(onClick = {
            sendLastMessageAsAlertMessage()
        }) {
            Text(text = "Repeat last message")
        }
    }
}