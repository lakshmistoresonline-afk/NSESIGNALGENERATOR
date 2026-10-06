package com.trademind.nse

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.viewModels
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import com.trademind.nse.ui.navigation.AppNavGraph
import com.trademind.nse.ui.viewmodel.NseViewModel

class MainActivity : ComponentActivity() {
    private val viewModel: NseViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MaterialTheme {
                Surface(color = MaterialTheme.colorScheme.background) {
                    AppNavGraph(viewModel = viewModel)
                }
            }
        }
    }
}
