package com.trademind.nse.ui.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.trademind.nse.data.api.RetrofitClient
import com.trademind.nse.data.model.*
import com.trademind.nse.data.repository.NseRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class NseViewModel : ViewModel() {
    private val repository = NseRepository(RetrofitClient.create())

    private val _baseUrl = MutableStateFlow("http://10.0.2.2:8010/")
    val baseUrl: StateFlow<String> = _baseUrl.asStateFlow()

    private val _health = MutableStateFlow<HealthResponse?>(null)
    val health: StateFlow<HealthResponse?> = _health.asStateFlow()

    private val _signals = MutableStateFlow<List<SignalItem>>(emptyList())
    val signals: StateFlow<List<SignalItem>> = _signals.asStateFlow()

    private val _selectedSignal = MutableStateFlow<SignalItem?>(null)
    val selectedSignal: StateFlow<SignalItem?> = _selectedSignal.asStateFlow()

    private val _marketStatus = MutableStateFlow<MarketStatusResponse?>(null)
    val marketStatus: StateFlow<MarketStatusResponse?> = _marketStatus.asStateFlow()

    private val _universeList = MutableStateFlow<List<UniverseItem>>(emptyList())
    val universeList: StateFlow<List<UniverseItem>> = _universeList.asStateFlow()

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    private val _errorMessage = MutableStateFlow<String?>(null)
    val errorMessage: StateFlow<String?> = _errorMessage.asStateFlow()

    private val _selectedUniverse = MutableStateFlow<String?>(null)
    val selectedUniverse: StateFlow<String?> = _selectedUniverse.asStateFlow()

    private val _selectedFilter = MutableStateFlow<String?>(null)
    val selectedFilter: StateFlow<String?> = _selectedFilter.asStateFlow()

    init {
        refreshAll()
    }

    fun updateBaseUrl(newUrl: String) {
        _baseUrl.value = newUrl
        repository.updateBaseUrl(newUrl)
        refreshAll()
    }

    fun setUniverseFilter(universe: String?) {
        _selectedUniverse.value = universe
        loadSignals()
    }

    fun setSignalFilter(filter: String?) {
        _selectedFilter.value = filter
        loadSignals()
    }

    fun refreshAll() {
        viewModelScope.launch {
            _isLoading.value = true
            _errorMessage.value = null
            try {
                val hResult = repository.fetchHealth()
                hResult.onSuccess { _health.value = it }.onFailure { _errorMessage.value = "Health check failed: ${it.message}" }

                val mResult = repository.fetchMarketStatus()
                mResult.onSuccess { _marketStatus.value = it }

                val uResult = repository.fetchUniverse()
                uResult.onSuccess { _universeList.value = it.universes }

                loadSignalsCore()
            } catch (e: Exception) {
                _errorMessage.value = "Error: ${e.message}"
            } finally {
                _isLoading.value = false
            }
        }
    }

    fun loadSignals() {
        viewModelScope.launch {
            _isLoading.value = true
            loadSignalsCore()
            _isLoading.value = false
        }
    }

    private suspend fun loadSignalsCore() {
        val res = repository.fetchSignals(_selectedUniverse.value, _selectedFilter.value)
        res.onSuccess { _signals.value = it }
            .onFailure { _errorMessage.value = "Failed to load signals: ${it.message}" }
    }

    fun loadSignalDetails(symbol: String) {
        viewModelScope.launch {
            _isLoading.value = true
            val res = repository.fetchSignalDetails(symbol)
            res.onSuccess { _selectedSignal.value = it }
                .onFailure { _errorMessage.value = "Failed to load details for $symbol" }
            _isLoading.value = false
        }
    }
}
