package com.ressphere.domain.dto

import kotlinx.serialization.Serializable

@Serializable
data class GPTResponse(
    val answer: String
)
