package com.trademind.nse.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material.icons.automirrored.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.trademind.nse.data.model.SignalItem
import com.trademind.nse.ui.viewmodel.NseViewModel
import java.text.NumberFormat
import java.util.Locale

fun formatInr(price: Double): String {
    val formatter = NumberFormat.getCurrencyInstance(Locale("en", "IN"))
    return formatter.format(price)
}

@Composable
fun SplashScreen(onNavigateToLogin: () -> Unit, onNavigateToDashboard: () -> Unit) {
    LaunchedEffect(Unit) {
        kotlinx.coroutines.delay(1800)
        onNavigateToDashboard()
    }
    Surface(modifier = Modifier.fillMaxSize(), color = MaterialTheme.colorScheme.background) {
        Column(
            modifier = Modifier.fillMaxSize().padding(24.dp),
            verticalArrangement = Arrangement.Center,
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Icon(Icons.Default.Star, contentDescription = null, modifier = Modifier.size(80.dp), tint = MaterialTheme.colorScheme.primary)
            Spacer(Modifier.height(16.dp))
            Text("NSE Signal Provider", style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold)
            Spacer(Modifier.height(8.dp))
            Text("India-Wide Market Intelligence", style = MaterialTheme.typography.bodyLarge, color = MaterialTheme.colorScheme.secondary)
            Spacer(Modifier.height(4.dp))
            Text("V30 Accuracy Hardened • Signal-Only System", style = MaterialTheme.typography.bodyMedium)
            Spacer(Modifier.height(24.dp))
            Card(colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.errorContainer)) {
                Text(
                    "REAL_TRADING = FALSE • NO BROKER EXECUTION",
                    modifier = Modifier.padding(12.dp),
                    color = MaterialTheme.colorScheme.onErrorContainer,
                    fontWeight = FontWeight.Bold,
                    fontSize = 12.sp
                )
            }
            Spacer(Modifier.height(32.dp))
            CircularProgressIndicator()
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun LoginScreen(onLoginSuccess: () -> Unit) {
    var email by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    var isLoading by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf<String?>(null) }

    Surface(modifier = Modifier.fillMaxSize()) {
        Column(
            modifier = Modifier.fillMaxSize().padding(24.dp),
            verticalArrangement = Arrangement.Center,
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text("Firebase Analyst Login", style = MaterialTheme.typography.headlineSmall, fontWeight = FontWeight.Bold)
            Spacer(Modifier.height(8.dp))
            Text("Authenticated India-Wide Research", style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.secondary)
            Spacer(Modifier.height(24.dp))
            OutlinedTextField(
                value = email,
                onValueChange = { email = it },
                label = { Text("Analyst Email") },
                modifier = Modifier.fillMaxWidth(),
                singleLine = true
            )
            Spacer(Modifier.height(16.dp))
            OutlinedTextField(
                value = password,
                onValueChange = { password = it },
                label = { Text("Password") },
                modifier = Modifier.fillMaxWidth(),
                singleLine = true,
                visualTransformation = androidx.compose.ui.text.input.PasswordVisualTransformation()
            )
            if (error != null) {
                Spacer(Modifier.height(8.dp))
                Text(error!!, color = MaterialTheme.colorScheme.error)
            }
            Spacer(Modifier.height(24.dp))
            Button(
                enabled = !isLoading && email.isNotBlank() && password.isNotBlank(),
                onClick = {
                    isLoading = true
                    error = null
                    try {
                        com.google.firebase.auth.FirebaseAuth.getInstance()
                            .signInWithEmailAndPassword(email.trim(), password)
                            .addOnCompleteListener { task ->
                                isLoading = false
                                if (task.isSuccessful) {
                                    onLoginSuccess()
                                } else {
                                    error = task.exception?.message ?: "Authentication failed: Invalid credentials"
                                }
                            }
                    } catch (e: Exception) {
                        isLoading = false
                        error = "Authentication error: ${e.message}"
                    }
                },
                modifier = Modifier.fillMaxWidth()
            ) {
                Text(if (isLoading) "Signing in..." else "Sign In with Firebase")
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DashboardScreen(
    viewModel: NseViewModel,
    onNavigateToSignals: () -> Unit,
    onNavigateToDetails: (String) -> Unit,
    onNavigateToSettings: () -> Unit
) {
    val health by viewModel.health.collectAsState()
    val signals by viewModel.signals.collectAsState()
    val marketStatus by viewModel.marketStatus.collectAsState()
    val isLoading by viewModel.isLoading.collectAsState()

    val buyCount = signals.count { it.signal.uppercase() == "BUY" }
    val sellCount = signals.count { it.signal.uppercase() == "SELL" }
    val noSignalCount = signals.count { it.signal.uppercase() == "NO_SIGNAL" || it.signal.uppercase() == "NO SIGNAL" }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("NSE Signal Dashboard") },
                actions = {
                    IconButton(onClick = { viewModel.refreshAll() }) {
                        Icon(Icons.Default.Refresh, contentDescription = "Refresh")
                    }
                    IconButton(onClick = onNavigateToSettings) {
                        Icon(Icons.Default.Settings, contentDescription = "Settings")
                    }
                }
            )
        }
    ) { pad ->
        LazyColumn(
            modifier = Modifier.padding(pad).fillMaxSize().padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Safety Banner
            item {
                Card(
                    colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.errorContainer),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Row(
                        modifier = Modifier.padding(12.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(Icons.Default.Warning, contentDescription = null, tint = MaterialTheme.colorScheme.onErrorContainer)
                        Spacer(Modifier.width(8.dp))
                        Text(
                            "REAL TRADING: DISABLED • SIGNAL ONLY",
                            fontWeight = FontWeight.Bold,
                            color = MaterialTheme.colorScheme.onErrorContainer,
                            fontSize = 13.sp
                        )
                    }
                }
            }

            // Market Status Card
            item {
                Card(modifier = Modifier.fillMaxWidth()) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text("INDIA MARKET (NSE)", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                            Badge(
                                containerColor = when (marketStatus?.marketStatus?.uppercase()) {
                                    "OPEN", "REGULAR" -> Color(0xFF10B981)
                                    "PRE_OPEN" -> Color(0xFF3B82F6)
                                    else -> Color(0xFF6B7280)
                                }
                            ) {
                                Text(marketStatus?.marketStatus ?: "CLOSED", color = Color.White, modifier = Modifier.padding(4.dp))
                            }
                        }
                        Spacer(Modifier.height(8.dp))
                        Text("Timezone: ${marketStatus?.timezone ?: "Asia/Kolkata (IST)"}", style = MaterialTheme.typography.bodyMedium)
                        Text("API Status: ${health?.status ?: "Unknown"} (v${health?.version ?: "3.8.0"})", style = MaterialTheme.typography.bodySmall)
                    }
                }
            }

            // Signal Summary Counters
            item {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    MetricCard("BUY SIGNALS", buyCount.toString(), Color(0xFF10B981), Modifier.weight(1f))
                    MetricCard("SELL SIGNALS", sellCount.toString(), Color(0xFFEF4444), Modifier.weight(1f))
                    MetricCard("NO SIGNAL", noSignalCount.toString(), Color(0xFF6B7280), Modifier.weight(1f))
                }
            }

            // Signal Feed Header
            item {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text("India-Wide Signal Feed", style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold)
                    TextButton(onClick = onNavigateToSignals) {
                        Text("View All (${signals.size})")
                    }
                }
            }

            if (isLoading) {
                item {
                    Box(modifier = Modifier.fillMaxWidth().padding(32.dp), contentAlignment = Alignment.Center) {
                        CircularProgressIndicator()
                    }
                }
            } else if (signals.isEmpty()) {
                item {
                    Text("No signals loaded. Check backend connection in settings.", color = Color.Gray)
                }
            } else {
                items(signals.take(5)) { sig ->
                    SignalCard(sig, onClick = { onNavigateToDetails(sig.symbol) })
                }
            }
        }
    }
}

@Composable
fun MetricCard(title: String, value: String, color: Color, modifier: Modifier = Modifier) {
    Card(modifier = modifier) {
        Column(
            modifier = Modifier.padding(12.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(title, style = MaterialTheme.typography.labelSmall, color = Color.Gray)
            Spacer(Modifier.height(4.dp))
            Text(value, style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold, color = color)
        }
    }
}

@Composable
fun SignalCard(signal: SignalItem, onClick: () -> Unit) {
    Card(
        modifier = Modifier.fillMaxWidth().clickable(onClick = onClick),
        elevation = CardDefaults.cardElevation(2.dp)
    ) {
        Row(
            modifier = Modifier.padding(16.dp).fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text(signal.symbol, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                    Spacer(Modifier.width(8.dp))
                    Text("NSE", style = MaterialTheme.typography.bodySmall, color = Color.Gray)
                }
                Spacer(Modifier.height(4.dp))
                Text(formatInr(signal.price), style = MaterialTheme.typography.bodyLarge, fontWeight = FontWeight.SemiBold)
                Spacer(Modifier.height(2.dp))
                Text("Regime: ${signal.regime}", style = MaterialTheme.typography.bodySmall, color = Color.DarkGray)
            }
            Column(horizontalAlignment = Alignment.End) {
                val isBuy = signal.signal.uppercase() == "BUY"
                val isSell = signal.signal.uppercase() == "SELL"
                Badge(
                    containerColor = when {
                        isBuy -> Color(0xFF10B981)
                        isSell -> Color(0xFFEF4444)
                        else -> Color(0xFF6B7280)
                    }
                ) {
                    Text(
                        text = if (isBuy) "BUY SIGNAL" else if (isSell) "SELL SIGNAL" else "NO SIGNAL",
                        color = Color.White,
                        modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
                        fontWeight = FontWeight.Bold
                    )
                }
                Spacer(Modifier.height(6.dp))
                Text("Conf: ${(signal.confidence * 100).toInt()}%", style = MaterialTheme.typography.bodySmall)
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SignalListScreen(
    viewModel: NseViewModel,
    onNavigateBack: () -> Unit,
    onNavigateToDetails: (String) -> Unit
) {
    val signals by viewModel.signals.collectAsState()
    val universeList by viewModel.universeList.collectAsState()
    val selectedUniverse by viewModel.selectedUniverse.collectAsState()
    val selectedFilter by viewModel.selectedFilter.collectAsState()
    var searchQuery by remember { mutableStateOf("") }

    val filtered = signals.filter {
        it.symbol.contains(searchQuery, ignoreCase = true)
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Signal Library & Filters") },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                    }
                }
            )
        }
    ) { pad ->
        Column(modifier = Modifier.padding(pad).fillMaxSize().padding(16.dp)) {
            OutlinedTextField(
                value = searchQuery,
                onValueChange = { searchQuery = it },
                label = { Text("Search Symbol (e.g. RELIANCE, TCS)") },
                modifier = Modifier.fillMaxWidth(),
                leadingIcon = { Icon(Icons.Default.Search, contentDescription = null) }
            )
            Spacer(Modifier.height(12.dp))

            // Filter Chips
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                FilterChip(selected = selectedFilter == null, onClick = { viewModel.setSignalFilter(null) }, label = { Text("All") })
                FilterChip(selected = selectedFilter == "BUY", onClick = { viewModel.setSignalFilter("BUY") }, label = { Text("BUY") })
                FilterChip(selected = selectedFilter == "SELL", onClick = { viewModel.setSignalFilter("SELL") }, label = { Text("SELL") })
                FilterChip(selected = selectedFilter == "NO_SIGNAL", onClick = { viewModel.setSignalFilter("NO_SIGNAL") }, label = { Text("NO SIGNAL") })
            }

            Spacer(Modifier.height(12.dp))
            Text("Universe Filter", style = MaterialTheme.typography.labelMedium)
            Spacer(Modifier.height(4.dp))
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                FilterChip(selected = selectedUniverse == null, onClick = { viewModel.setUniverseFilter(null) }, label = { Text("All EQ") })
                FilterChip(selected = selectedUniverse == "NIFTY 50", onClick = { viewModel.setUniverseFilter("NIFTY 50") }, label = { Text("NIFTY 50") })
                FilterChip(selected = selectedUniverse == "NIFTY 100", onClick = { viewModel.setUniverseFilter("NIFTY 100") }, label = { Text("NIFTY 100") })
            }

            Spacer(Modifier.height(16.dp))
            LazyColumn(
                modifier = Modifier.fillMaxSize(),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                items(filtered) { sig ->
                    SignalCard(sig, onClick = { onNavigateToDetails(sig.symbol) })
                }
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SignalDetailsScreen(
    symbol: String,
    viewModel: NseViewModel,
    onNavigateBack: () -> Unit
) {
    val signals by viewModel.signals.collectAsState()
    val detail = signals.find { it.symbol.equals(symbol, ignoreCase = true) }

    LaunchedEffect(symbol) {
        viewModel.loadSignalDetails(symbol)
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("$symbol Details") },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                    }
                }
            )
        }
    ) { pad ->
        Column(
            modifier = Modifier.padding(pad).fillMaxSize().padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            if (detail == null) {
                CircularProgressIndicator()
            } else {
                Card(modifier = Modifier.fillMaxWidth()) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                            Text(detail.symbol, style = MaterialTheme.typography.headlineSmall, fontWeight = FontWeight.Bold)
                            Text(formatInr(detail.price), style = MaterialTheme.typography.headlineSmall, fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.primary)
                        }
                        Spacer(Modifier.height(8.dp))
                        HorizontalDivider()
                        Spacer(Modifier.height(8.dp))
                        DetailRow("Exchange", detail.exchange)
                        DetailRow("Signal", detail.signal)
                        DetailRow("Confidence", "${(detail.confidence * 100).toInt()}%")
                        DetailRow("Regime", detail.regime)
                        DetailRow("Publication Status", detail.publicationStatus)
                        DetailRow("Conformal Status", detail.conformalStatus ?: "N/A")
                        DetailRow("Model Dispersion", detail.modelDispersion?.toString() ?: "N/A")
                        DetailRow("Signal Time", detail.signalTime)
                    }
                }

                if (detail.signal.uppercase().contains("NO")) {
                    Card(
                        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Column(modifier = Modifier.padding(16.dp)) {
                            Text("No Signal / Abstention Reason", fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.error)
                            Spacer(Modifier.height(4.dp))
                            Text(detail.reason ?: "Conformal abstention or model uncertainty threshold triggered. System preserved fail-closed safety.", style = MaterialTheme.typography.bodyMedium)
                        }
                    }
                }

                Card(modifier = Modifier.fillMaxWidth()) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Text("V30 Governance & Safety", fontWeight = FontWeight.Bold)
                        Spacer(Modifier.height(8.dp))
                        DetailRow("Signal-Only Mode", "True (REAL_TRADING = FALSE)")
                        DetailRow("PIT Provenance", if (detail.pitProvenanceVerified != false) "Verified" else "Unverified")
                        DetailRow("Publication Gate", detail.publicationGate ?: "Passed")
                    }
                }
            }
        }
    }
}

@Composable
fun DetailRow(label: String, value: String) {
    Row(
        modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Text(label, color = Color.Gray, style = MaterialTheme.typography.bodyMedium)
        Text(value, fontWeight = FontWeight.Medium, style = MaterialTheme.typography.bodyMedium)
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SettingsScreen(
    viewModel: NseViewModel,
    onNavigateBack: () -> Unit
) {
    val baseUrl by viewModel.baseUrl.collectAsState()
    val health by viewModel.health.collectAsState()
    var urlInput by remember { mutableStateOf(baseUrl) }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Settings & System Status") },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                    }
                }
            )
        }
    ) { pad ->
        Column(
            modifier = Modifier.padding(pad).fillMaxSize().padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            Card(
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.errorContainer),
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("REAL TRADING: DISABLED", fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.onErrorContainer)
                    Spacer(Modifier.height(4.dp))
                    Text("This application is strictly a signal provider. No broker order execution or portfolio management is enabled or possible.", color = MaterialTheme.colorScheme.onErrorContainer, style = MaterialTheme.typography.bodySmall)
                }
            }

            Card(modifier = Modifier.fillMaxWidth()) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("Backend API Configuration", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                    Spacer(Modifier.height(8.dp))
                    OutlinedTextField(
                        value = urlInput,
                        onValueChange = { urlInput = it },
                        label = { Text("API Base URL (e.g. http://10.0.2.2:8010/)") },
                        modifier = Modifier.fillMaxWidth()
                    )
                    Spacer(Modifier.height(8.dp))
                    Button(
                        onClick = { viewModel.updateBaseUrl(urlInput) },
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text("Save & Reconnect")
                    }
                }
            }

            Card(modifier = Modifier.fillMaxWidth()) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("System Information", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                    Spacer(Modifier.height(8.dp))
                    DetailRow("App Version", "27.0.0")
                    DetailRow("Signal Engine", "V30 Accuracy Hardened")
                    DetailRow("API Status", health?.status ?: "Disconnected")
                    DetailRow("API Version", health?.version ?: "3.8.0")
                    DetailRow("Timezone", "Asia/Kolkata (IST)")
                }
            }
        }
    }
}
