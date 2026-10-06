# NSE Signal Provider — Android Studio Client V25

Read-only monitoring client for the signal-only NSE provider.

- REAL_TRADING = FALSE
- No broker credentials
- No order placement/modification/cancellation
- Emulator backend: `http://10.0.2.2:8010`
- Physical device: use the backend PC LAN address

The client reads `/api/publication-health`, `/api/readiness`, and `/api/providers`.
