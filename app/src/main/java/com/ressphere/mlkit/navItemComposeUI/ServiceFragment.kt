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

@Composable
fun ServiceFragment(context: Context) {
    Column(
        modifier = Modifier.fillMaxSize(),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Button(onClick = {
            Intent(context, SpeechService::class.java).also {
                it.action = SpeechService.Actions.START.toString()
                context.startService(it)
            }
        }) {
            Text(text="Start")
        }
        Button(onClick = {
            Intent(context, SpeechService::class.java).also {
                it.action = SpeechService.Actions.STOP.toString()
                context.startService(it)
            }
        }) {
            Text(text="Stop")
        }
    }
}