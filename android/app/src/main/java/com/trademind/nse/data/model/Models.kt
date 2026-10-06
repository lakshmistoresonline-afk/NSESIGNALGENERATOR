package com.trademind.nse.data.model

import com.google.gson.annotations.SerializedName

data class HealthResponse(
    @SerializedName("status") val status: String,
    @SerializedName("version") val version: String,
    @SerializedName("signal_only") val signalOnly: Boolean,
    @SerializedName("real_trading") val realTrading: Boolean,
    @SerializedName("timestamp") val timestamp: String?
)

data class SignalItem(
    @SerializedName("symbol") val symbol: String,
    @SerializedName("exchange") val exchange: String,
    @SerializedName("signal") val signal: String, // BUY, SELL, NO_SIGNAL
    @SerializedName("confidence") val confidence: Double,
    @SerializedName("price") val price: Double,
    @SerializedName("signal_time") val signalTime: String,
    @SerializedName("regime") val regime: String,
    @SerializedName("publication_status") val publicationStatus: String,
    @SerializedName("conformal_status") val conformalStatus: String?,
    @SerializedName("model_dispersion") val modelDispersion: Double?,
    @SerializedName("signal_only") val signalOnly: Boolean,
    @SerializedName("real_trading") val realTrading: Boolean,
    @SerializedName("reason") val reason: String?,
    @SerializedName("universe") val universe: String?,
    @SerializedName("model_agreement") val modelAgreement: Double?,
    @SerializedName("data_freshness") val dataFreshness: String?,
    @SerializedName("pit_provenance_verified") val pitProvenanceVerified: Boolean?,
    @SerializedName("risk_gates") val riskGates: List<String>?,
    @SerializedName("publication_gate") val publicationGate: String?
)

data class SignalsResponse(
    @SerializedName("signal_only") val signalOnly: Boolean,
    @SerializedName("real_trading") val realTrading: Boolean,
    @SerializedName("count") val count: Int,
    @SerializedName("items") val items: List<SignalItem>
)

data class MarketStatusResponse(
    @SerializedName("exchange") val exchange: String,
    @SerializedName("market_status") val marketStatus: String, // OPEN, PRE-OPEN, CLOSED, HOLIDAY
    @SerializedName("timestamp") val timestamp: String,
    @SerializedName("timezone") val timezone: String,
    @SerializedName("signal_only") val signalOnly: Boolean,
    @SerializedName("real_trading") val realTrading: Boolean
)

data class UniverseItem(
    @SerializedName("name") val name: String,
    @SerializedName("count") val count: Int,
    @SerializedName("description") val description: String
)

data class UniverseResponse(
    @SerializedName("signal_only") val signalOnly: Boolean,
    @SerializedName("real_trading") val realTrading: Boolean,
    @SerializedName("universes") val universes: List<UniverseItem>
)
