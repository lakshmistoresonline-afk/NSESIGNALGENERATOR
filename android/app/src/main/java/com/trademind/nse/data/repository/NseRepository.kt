package com.trademind.nse.data.repository

import com.trademind.nse.data.api.NseApiService
import com.trademind.nse.data.model.*
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

class NseRepository(private var apiService: NseApiService) {

    fun updateBaseUrl(baseUrl: String) {
        apiService = com.trademind.nse.data.api.RetrofitClient.create(baseUrl)
    }

    suspend fun fetchHealth(): Result<HealthResponse> = withContext(Dispatchers.IO) {
        try {
            Result.success(apiService.getHealth())
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun fetchSignals(universe: String? = null, signalFilter: String? = null): Result<List<SignalItem>> = withContext(Dispatchers.IO) {
        try {
            val resp = apiService.getSignals(universe, signalFilter)
            Result.success(resp.items)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun fetchSignalDetails(symbol: String): Result<SignalItem> = withContext(Dispatchers.IO) {
        try {
            Result.success(apiService.getSignalDetails(symbol))
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun fetchMarketStatus(): Result<MarketStatusResponse> = withContext(Dispatchers.IO) {
        try {
            Result.success(apiService.getMarketStatus())
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun fetchUniverse(): Result<UniverseResponse> = withContext(Dispatchers.IO) {
        try {
            Result.success(apiService.getUniverse())
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
