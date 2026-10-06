package com.trademind.nse.ui.navigation

import androidx.compose.runtime.Composable
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import com.trademind.nse.ui.screens.*
import com.trademind.nse.ui.viewmodel.NseViewModel

sealed class Screen(val route: String) {
    object Splash : Screen("splash")
    object Login : Screen("login")
    object Dashboard : Screen("dashboard")
    object Signals : Screen("signals")
    object Details : Screen("details/{symbol}") {
        fun createRoute(symbol: String) = "details/$symbol"
    }
    object Settings : Screen("settings")
}

@Composable
fun AppNavGraph(viewModel: NseViewModel) {
    val navController = rememberNavController()
    NavHost(navController = navController, startDestination = Screen.Splash.route) {
        composable(Screen.Splash.route) {
            SplashScreen(onNavigateToLogin = {
                navController.navigate(Screen.Login.route) { popUpTo(Screen.Splash.route) { inclusive = true } }
            }, onNavigateToDashboard = {
                navController.navigate(Screen.Dashboard.route) { popUpTo(Screen.Splash.route) { inclusive = true } }
            })
        }
        composable(Screen.Login.route) {
            LoginScreen(onLoginSuccess = {
                navController.navigate(Screen.Dashboard.route) { popUpTo(Screen.Login.route) { inclusive = true } }
            })
        }
        composable(Screen.Dashboard.route) {
            DashboardScreen(
                viewModel = viewModel,
                onNavigateToSignals = { navController.navigate(Screen.Signals.route) },
                onNavigateToDetails = { symbol -> navController.navigate(Screen.Details.createRoute(symbol)) },
                onNavigateToSettings = { navController.navigate(Screen.Settings.route) }
            )
        }
        composable(Screen.Signals.route) {
            SignalListScreen(
                viewModel = viewModel,
                onNavigateBack = { navController.popBackStack() },
                onNavigateToDetails = { symbol -> navController.navigate(Screen.Details.createRoute(symbol)) }
            )
        }
        composable(
            route = Screen.Details.route,
            arguments = listOf(navArgument("symbol") { type = NavType.StringType })
        ) { backStackEntry ->
            val symbol = backStackEntry.arguments?.getString("symbol") ?: "RELIANCE"
            SignalDetailsScreen(
                symbol = symbol,
                viewModel = viewModel,
                onNavigateBack = { navController.popBackStack() }
            )
        }
        composable(Screen.Settings.route) {
            SettingsScreen(
                viewModel = viewModel,
                onNavigateBack = { navController.popBackStack() }
            )
        }
    }
}
