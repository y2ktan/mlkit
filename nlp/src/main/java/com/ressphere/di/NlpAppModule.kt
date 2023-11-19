package com.ressphere.di

import com.ressphere.domain.H2OGPT



object NlpAppModule {
    val gptGateway: GPTGateway by lazy {
       H2OGPT()
    }
}