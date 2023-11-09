package com.ressphere.nlp

import java.io.Closeable

interface NLPExecutor: Closeable {
    fun execute(question: String) {

    }

    fun init() {

    }
}