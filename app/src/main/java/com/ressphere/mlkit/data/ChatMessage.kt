package com.ressphere.mlkit.data

import androidx.compose.ui.graphics.Color
import com.ressphere.mlkit.navItemComposeUI.generateAppealingFontColor

data class ChatMessage(
    val id: String,
    val name: String,
    val message: String,
    val bgColor: Color = Color.LightGray,
    val color: Color = generateAppealingFontColor(bgColor)
)