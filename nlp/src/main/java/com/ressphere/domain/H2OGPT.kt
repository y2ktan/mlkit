package com.ressphere.domain
import com.ressphere.di.GPTGateway
import com.ressphere.domain.dto.GPTRequest

class H2OGPT: GPTGateway {
    private val h2OPostsService: H2OPostsService = H2OPostsService.create()
    override suspend fun ask(question: String): String? {
        h2OPostsService.postQuestion(GPTRequest(question))?.also {
            return it.answer
        }
        return null
    }

}