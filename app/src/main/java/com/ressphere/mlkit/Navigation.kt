package com.ressphere.mlkit

import android.app.Application
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.Info
import androidx.compose.material.icons.outlined.Home
import androidx.compose.material.icons.outlined.Info
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavBackStackEntry
import androidx.navigation.NavController
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.ressphere.mlkit.data.ChatMessage
import com.ressphere.mlkit.navItemComposeUI.ChatFragment
import com.ressphere.mlkit.navItemComposeUI.ServiceFragment

val homeNavItem = NavigationItem(
    title = "All",
    selectedIcon = Icons.Filled.Home,
    unselectedIcon = Icons.Outlined.Home,
    route="Home",
    home = true
)

val chatNavItem = NavigationItem(
    title = "Chat",
    selectedIcon = Icons.Filled.Info,
    unselectedIcon = Icons.Outlined.Info,
    route="Chat"
)

val items = listOf(
    homeNavItem,
    chatNavItem
)

@Composable
fun Navigation(app: Application,
               chatMessages: List<ChatMessage>,
               onRecordStart: () -> Unit = {},
               onRecordStop: () -> Unit = {},
               isRecording: Boolean = false,
               navController: NavHostController =
                   rememberNavController()

               ) {

    NavHost(navController = navController, startDestination=items.first { it.home }.route?:"home") {
        composable(homeNavItem.route!!) {
            ChatFragment(chatMessages, onRecordStart, onRecordStop, isRecording)
        }
        composable(chatNavItem.route!!) {
            ServiceFragment(context = app.applicationContext)
        }
    }
}

@Composable
inline fun <reified T:ViewModel> NavBackStackEntry.sharedViewModel(navController: NavController): T {
    val navGraphRoute = destination.parent?.route?: return viewModel()
    val parentEntry = remember(this) {
        navController.getBackStackEntry(navGraphRoute)
    }
    return viewModel(parentEntry)
}
