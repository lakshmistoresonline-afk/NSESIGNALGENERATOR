# Android Runtime & Client Validation Report

## 1. Executive Summary
This report documents the Android client implementation audit against the backend contract, enforcing strict signal-only safety (`REAL_TRADING = FALSE`), read-only signal consumption, and Firebase authentication.

## 2. Invariant Compliance
- **Broker Credentials**: None.
- **Order Placement / Execution**: None. Zero order routing or trading routes exist.
- **Signal-Only Product**: Fully enforced (`REAL_TRADING = FALSE`).

## 3. Firebase Authentication Flow
- **Client**: Android client handles user sign-in and passes the Firebase ID token in the `Authorization: Bearer <token>` header.
- **Backend**: FastAPI middleware / dependency `verify_auth_token` uses the Firebase Admin SDK (`firebase_admin.auth.verify_id_token`) to verify the token, extract claims, and authorize `analyst` role access.
- **Role Authorization**: Unauthenticated requests receive `401 Unauthorized`; unauthorized roles receive `403 Forbidden`.

## 4. Build & Runtime Execution Status
- **Gradle Build**: Gradle 8.9 build configuration configured for debug and release builds.
- **Android Instrumentation / Runtime**: `NOT EXECUTED — NO DEVICE/EMULATOR` (Headless agent container environment lacks an active connected AVD or physical device).
