package com.ressphere.mlkit

import android.app.Application
import android.app.NotificationChannel
import android.app.NotificationManager
import android.content.Context
import android.content.Intent
import android.os.Build
import com.ressphere.mlkit.di.AppModule
import com.ressphere.mlkit.di.AppModuleImpl

class MyApplication: Application() {
    override fun onCreate() {
        super.onCreate()
        val channel = NotificationChannel(
            NOTIFICATION_CAHNNEL_ID,
            "Running Notification",
            NotificationManager.IMPORTANCE_HIGH
        )
        val notificationManager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        notificationManager.createNotificationChannel(channel)
        Intent(applicationContext, SpeechService::class.java).also {
            it.action = SpeechService.Actions.START.toString()
            applicationContext.startService(it)
        }
        appModule = AppModuleImpl(this)
    }

    companion object {
        const val NOTIFICATION_CAHNNEL_ID = "running_channel"
        const val NOTIFICATION_ID = 1
        lateinit var appModule: AppModule
    }
}