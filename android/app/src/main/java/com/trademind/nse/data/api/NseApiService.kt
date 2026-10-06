package com.trademind.nse.data.api

import com.trademind.nse.data.model.*
import retrofit2.http.GET
import retrofit2.http.Path
import retrofit2.http.Query

interface NseApiService {
    @GET("api/v1/health")
    suspend fun getHealth(): HealthResponse

    @GET("api/v1/signals")
    suspend fun getSignals(
        @Query("universe") universe: String? = null,
        @Query("signal_filter") signalFilter: String? = null
    ): SignalsResponse

    @GET("api/v1/signals/{symbol}")
    suspend fun getSignalBySymbol(@Path("symbol") symbol: String): SignalItem

    @GET("api/v1/market-status")
    suspend fun getMarketStatus(): MarketStatusResponse

    @GET("api/v1/universe")
    suspend fun getUniverse(): UniverseResponse

    @GET("api/v1/signal/{symbol}/details")
    suspend fun getSignalDetails(@Path("symbol") symbol: String): SignalItem
}

object RetrofitClient {
    private const val DEBUG_BASE_URL = "http://10.0.2.2:8010/"
    private const val RELEASE_BASE_URL = "http://127.0.0.1:8010/"

    private var retrofit: retrofit2.Retrofit? = null
    private var currentUrl: String = DEBUG_BASE_URL

    fun create(baseUrl: String = DEBUG_BASE_URL): NseApiService {
        if (retrofit == null || currentUrl != baseUrl) {
            currentUrl = baseUrl
            retrofit = retrofit2.Retrofit.Builder()
                .baseUrl(baseUrl)
                .addConverterFactory(retrofit2.converter.gson.GsonConverterFactory.create())
                .build()
        }
        return retrofit!!.create(NseApiService::class.java)
    }
}
