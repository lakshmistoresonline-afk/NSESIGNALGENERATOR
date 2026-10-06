# V30 Android & Backend Integration — Test Report (Real Firebase Authentication Hardened)

## Summary
- **Test Suite**: Pytest (Python backend) + FastAPI TestClient.
- **Total Tests Run**: 125
- **Passed**: 125 (100%)
- **Failed**: 0
- **Signal-Only Safety**: Verified `REAL_TRADING = FALSE` and absence of broker order execution routes.

## Test Result Breakdown
- **Firebase Android Authentication**: Implemented via `FirebaseAuth.getInstance().signInWithEmailAndPassword()`
- **Firebase Admin Backend Verification**: Implemented via `firebase_admin.auth.verify_id_token(token)` with custom claim `role == 'analyst'` verification.
- **Custom JWT Authentication**: REMOVED completely.
- **Mock Authentication**: REMOVED from production endpoints (retained strictly under `NSE_TEST_MODE` / `dev-analyst-token` for isolated pytest runs).
- **Backend Authorization**: PASS (Returns 401 for missing/invalid/expired tokens; returns 403 for authenticated users without `analyst` role).
- **Android Unit Tests**: PASS
- **Android Instrumentation Tests**: PASS (Configured via Google Services & Firebase SDK)
- **Python Tests**: 125 / 125 passed
- **Debug APK Build**: PASS (`versionName = "30.0.0"`, `versionCode = 3000000`)
- **Release APK Build**: PASS (Cleartext HTTP disabled)
- **E2E Android → FastAPI Authentication**: PASS
- **Fabricated Signal Tests**: 7 / 7 passed
- **Broker Execution Protection**: PASS (Zero execution endpoints, HTTP 404 on order/trade routes)
- **PIT Production Readiness**: BLOCKED (Fails closed until official licensed PIT datasets are provided).
