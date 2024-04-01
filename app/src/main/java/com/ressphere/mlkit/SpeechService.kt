package com.ressphere.mlkit


import android.app.Service
import android.content.Intent
import android.os.IBinder
import androidx.core.app.NotificationCompat
import com.ressphere.mlkit.MyApplication.Companion.NOTIFICATION_CAHNNEL_ID
import com.ressphere.mlkit.MyApplication.Companion.NOTIFICATION_ID
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.flow.collectLatest
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class SpeechService: Service() {

    private val job = SupervisorJob()
    private val speechServiceCoroutine = CoroutineScope(job)
    override fun onBind(p0: Intent?): IBinder? {
        return null
    }

    override fun onCreate() {
        super.onCreate()
        MyApplication.appModule.nlpUseCase.loadNLP()
        speechServiceCoroutine.launch {
            withContext(Dispatchers.Default) {
                MyApplication.appModule.speechRecognitionListener.flow.collectLatest {
                    MyApplication.appModule.nlpUseCase.ask(it)
                }
            }
        }
    }



    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {

        when(intent?.action) {
            Actions.START.toString() -> {
                start()
            }
            Actions.STOP.toString() -> {
                stopSelf()
            }
        }
        return START_STICKY
    }

    private fun start() {
        val notification = NotificationCompat
            .Builder(this, NOTIFICATION_CAHNNEL_ID)
            .setSmallIcon(R.drawable.ic_launcher_foreground)
            .setContentTitle("Run is action")
            .setContentText("Elapsed time: 00:50")
            .build()
        startForeground(NOTIFICATION_ID, notification)

    }

    override fun onDestroy() {
        super.onDestroy()
        MyApplication.appModule.nlpUseCase.unloadNLP()
        job.cancel()
    }


    enum class Actions {
        START, STOP
    }
}