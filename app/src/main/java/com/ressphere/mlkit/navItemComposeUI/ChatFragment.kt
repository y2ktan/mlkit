package com.ressphere.mlkit.navItemComposeUI

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.IntrinsicSize
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Button
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import com.ressphere.mlkit.ColorContrastCalculator
import com.ressphere.mlkit.data.ChatMessage
import com.ressphere.mlkit.ui.theme.M3NavigationDrawerTheme

@Composable
fun ChatFragment(
    chatMessages: List<ChatMessage>,
    onRecordStart: () -> Unit = {},
    onRecordStop: () -> Unit = {},
    isRecording:Boolean = false

) {
    Column(
        modifier = Modifier.fillMaxSize().padding(top=50.dp),
        verticalArrangement = Arrangement.SpaceBetween
    ) {
        LazyColumn(
            modifier = Modifier
                .weight(1f),
            reverseLayout = true
        ) {
            items(chatMessages.reversed()) { msg ->
                ChatMessageItem(chatMessage = msg)
            }
        }
        Button(
            onClick = {
                if (isRecording) {
                    onRecordStop()
                } else {
                    onRecordStart()
                }
            },
            modifier = Modifier
                .padding(bottom = 16.dp)
                .align(Alignment.CenterHorizontally)
        ) {
            Text(text = if (!isRecording) "Talk" else "Done")
        }
    }
}

@Composable
fun ChatMessageItem(chatMessage: ChatMessage) {
    Text(
        text = "${chatMessage.name}: ${chatMessage.message}",
        modifier = Modifier
            .padding(16.dp)
            .background(chatMessage.bgColor)
            .padding(8.dp)
            .fillMaxWidth(),
        color = chatMessage.color
    )
}

fun generateAppealingFontColor(background: Color): Color {
    val whiteContrast = ColorContrastCalculator.calculateContrastRatio(background, Color.White)
    val blackContrast = ColorContrastCalculator.calculateContrastRatio(background, Color.Black)

    return if (whiteContrast > blackContrast) {
        Color.White
    } else {
        Color.Black
    }
}

@Preview
@Composable
fun ChatFragmentPreview() {
    val messages = mutableListOf(
        ChatMessage("1", "John", "Hello", Color.Gray),
        ChatMessage("2", "Alice", "Hi, how are you?", Color.Green),
        ChatMessage("3", "John", "I'm good, thanks! How about you?"),
        ChatMessage("4", "Alice", "I'm doing great too!"),
        ChatMessage("5", "John", "That's awesome!"),
        ChatMessage("1", "John", "Hello", Color.Gray),
        ChatMessage("2", "Alice", "Hi, how are you?", Color.Green),
        ChatMessage("3", "John", "I'm good, thanks! How about you?"),
        ChatMessage("4", "Alice", "I'm doing great too!"),
        ChatMessage("1", "John", "Hello", Color.Gray),
        ChatMessage("2", "Alice", "Hi, how are you?", Color.Green),
        ChatMessage("3", "John", "I'm good, thanks! How about you?"),
        ChatMessage("4", "Alice", "I'm doing great too!")
    )
    M3NavigationDrawerTheme {
        ChatFragment(chatMessages = messages)
    }
}