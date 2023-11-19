package com.ressphere.domain.dto

import kotlinx.serialization.Serializable

@Serializable
data class GPTRequest(
    val question: String

)
