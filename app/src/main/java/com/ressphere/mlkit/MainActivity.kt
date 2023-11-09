package com.ressphere.mlkit

import android.Manifest
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.activity.viewModels
import androidx.annotation.RequiresApi
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.Info
import androidx.compose.material.icons.outlined.Home
import androidx.compose.material.icons.outlined.Info
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.tooling.preview.Preview
import androidx.core.content.ContextCompat
import androidx.navigation.compose.rememberNavController
import com.ressphere.mlkit.MyApplication.Companion.appModule
import com.ressphere.mlkit.ui.theme.M3NavigationDrawerTheme
import kotlinx.coroutines.Dispatchers

@RequiresApi(Build.VERSION_CODES.TIRAMISU)
class MainActivity : ComponentActivity() {
    private val chatViewModel:ChatViewModel by viewModels {
        ChatViewModelFactory(application, Dispatchers.Default)
    }
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        if(!hasRequiredPermissions()) requestPermissions()
        setContent {
            M3NavigationDrawerTheme {
                val navController = rememberNavController()

                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    val messages by chatViewModel.sourceMessage.collectAsState()
                    val isRecording by appModule.speechToTextUseCase.isRecording.collectAsState()
                    DrawerSheet(items, "VP APP", navController) {
                        Navigation(
                            app = application,
                            chatMessages = messages,
                            navController = navController,
                            onRecordStart = chatViewModel::onRecordStart,
                            onRecordStop = chatViewModel::onRecordStop,
                            isRecording = isRecording
                        )
                    }

                }
            }
        }

    }
    private val requestPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions()
    ) { permissions ->
        val grantedPermissions = permissions.filterValues { it }
        val deniedPermissions = permissions.filterValues { !it }

        grantedPermissions.keys.forEach { permission ->
            when (permission) {
                Manifest.permission.POST_NOTIFICATIONS -> {
                    // Permission POST_NOTIFICATIONS is granted
                    // Handle accordingly
                }
                Manifest.permission.RECORD_AUDIO -> {
                    // Permission RECORD_AUDIO is granted
                    // Handle accordingly
                }

                Manifest.permission.FOREGROUND_SERVICE -> {
                    // Permission FOREGROUND_SERVICE is granted
                    // Handle accordingly
                }
            }
        }

        deniedPermissions.keys.forEach { permission ->
            when (permission) {
                Manifest.permission.POST_NOTIFICATIONS -> {
                    finish()
                }
                Manifest.permission.RECORD_AUDIO -> {
                    finish()
                }
                Manifest.permission.FOREGROUND_SERVICE -> {
                    finish()
                }
            }
        }

    }

    private fun hasRequiredPermissions(): Boolean {
        return VIRTUAL_PARTNER_PERMISSIONS.all {
            ContextCompat.checkSelfPermission(
                applicationContext,
                it
            ) == PackageManager.PERMISSION_GRANTED
        }
    }

    // Request the permissions
    private fun requestPermissions() {
        val permissionsToRequest = VIRTUAL_PARTNER_PERMISSIONS.filter {
            ContextCompat.checkSelfPermission(this, it) != PackageManager.PERMISSION_GRANTED
        }.toTypedArray()

        if (permissionsToRequest.isNotEmpty()) {
            requestPermissionLauncher.launch(permissionsToRequest)
        }
    }
    companion object {
        private val VIRTUAL_PARTNER_PERMISSIONS = arrayOf(
            Manifest.permission.POST_NOTIFICATIONS,
            Manifest.permission.RECORD_AUDIO,
            Manifest.permission.FOREGROUND_SERVICE
        )
    }
}


@Preview
@Composable
fun TabLayoutPreview() {
    val items = listOf(
        NavigationItem(
            title = "All",
            selectedIcon = Icons.Filled.Home,
            unselectedIcon = Icons.Outlined.Home,
        ),
        NavigationItem(
            title = "Chat",
            selectedIcon = Icons.Filled.Info,
            unselectedIcon = Icons.Outlined.Info,
        )
    )
    M3NavigationDrawerTheme {
        Surface(
            modifier = Modifier.fillMaxSize(),
            color = MaterialTheme.colorScheme.background
        ) {
            DrawerSheet(items, "VP APP", navigator = @Composable {

            })
        }
    }
}