package com.ressphere.di

interface GPTGateway {
    suspend fun ask(question: String): String? {
        return null
    }
}