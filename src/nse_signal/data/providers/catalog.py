from __future__ import annotations
PROVIDER_CATALOG = {
 "tejhq":{"access_cost":"free_keyless_or_free_key","historical":True,"pit_authoritative":False,"automatic_fallback":True,"read_only_adapter":True,"notes":"NSE/BSE-derived secondary source; not exchange-licensed."},
 "bharatstock":{"access_cost":"free_tier","historical":True,"pit_authoritative":False,"automatic_fallback":True,"read_only_adapter":True,"notes":"Free tier is rate-limited; terms restrict redistribution."},
 "upstox":{"access_cost":"free","historical":True,"pit_authoritative":False,"automatic_fallback":True,"read_only_adapter":True},
 "5paisa":{"access_cost":"free","historical":True,"pit_authoritative":False,"automatic_fallback":True,"read_only_adapter":True},
 "angelone":{"access_cost":"free_api_access","historical":True,"pit_authoritative":False,"automatic_fallback":True,"read_only_adapter":True},
 "fyers":{"access_cost":"free_for_clients","historical":True,"pit_authoritative":False,"automatic_fallback":True,"read_only_adapter":True},
 "dhan":{"access_cost":"data_api_paid","historical":True,"pit_authoritative":False,"automatic_fallback":True,"read_only_adapter":True},
 "groww":{"access_cost":"subscription","historical":True,"pit_authoritative":False,"automatic_fallback":True,"read_only_adapter":True},
 "yahoo":{"access_cost":"public_endpoint","historical":True,"pit_authoritative":False,"automatic_fallback":False,"read_only_adapter":True,"automation_permission_required":True},
}
def get_provider_catalog(): return {k:dict(v) for k,v in PROVIDER_CATALOG.items()}
