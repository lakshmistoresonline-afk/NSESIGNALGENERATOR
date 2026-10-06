# V30 Android Build & Environment Setup Guide

This document provides the complete, reproducible setup and build instructions for the V30 NSE Signal Provider Android application on Windows.

## 1. Prerequisites & Environment Requirements
- **Operating System**: Windows 10 / 11 (64-bit)
- **Java Development Kit (JDK)**: OpenJDK 21 LTS (or compatible JDK 17/21)
- **Android Studio**: Ladybug / Koala or newer (supporting Android Gradle Plugin 8.7.3)
- **Android SDK Components** (via Android Studio SDK Manager):
  - Android SDK Platform 35 (`platforms;android-35`)
  - Android SDK Build-Tools 35.x (`build-tools;35.0.0`)
  - Android SDK Platform-Tools (`platform-tools`)
  - Android SDK Command-line Tools (`cmdline-tools;latest`)
  - Android Emulator (`emulator`)

## 2. Environment Variables Verification (PowerShell)
Open PowerShell and verify your environment variables:

```powershell
$env:JAVA_HOME
$env:ANDROID_HOME
$env:ANDROID_SDK_ROOT
```

If not set, configure them in PowerShell (or System Environment Variables):
```powershell
$env:JAVA_HOME = "C:\Program Files\Microsoft\jdk-21.0.12.8-hotspot"
$env:ANDROID_HOME = "$env:LOCALAPPDATA\Android\Sdk"
$env:ANDROID_SDK_ROOT = "$env:LOCALAPPDATA\Android\Sdk"
[Environment]::SetEnvironmentVariable("JAVA_HOME", $env:JAVA_HOME, [EnvironmentVariableTarget]::User)
[Environment]::SetEnvironmentVariable("ANDROID_HOME", $env:ANDROID_HOME, [EnvironmentVariableTarget]::User)
[Environment]::SetEnvironmentVariable("ANDROID_SDK_ROOT", $env:ANDROID_SDK_ROOT, [EnvironmentVariableTarget]::User)
```

## 3. Gradle Compatibility & Wrapper Generation
The project requires **Gradle 8.9** to support Android Gradle Plugin 8.7.3.

To generate or restore the Gradle wrapper in the `android/` directory:
1. Ensure Gradle 8.9 is installed globally on your machine (e.g., via SDKMAN, Chocolatey, or manual download).
2. Open PowerShell and run:
   ```powershell
   cd D:\NSE_Signal_Provider\android
   gradle wrapper --gradle-version 8.9
   ```
3. Verify the generated wrapper files exist:
   - `android\gradlew`
   - `android\gradlew.bat`
   - `android\gradle\wrapper\gradle-wrapper.jar`
   - `android\gradle\wrapper\gradle-wrapper.properties`
4. Commit these wrapper files to Git for reproducible builds.

## 4. Local Environment Validation Script
A diagnostic script is provided at `scripts/verify_android_environment.ps1`. Run it in PowerShell to check your local configuration:
```powershell
powershell -ExecutionPolicy Bypass -File D:\NSE_Signal_Provider\scripts\verify_android_environment.ps1
```

## 5. User-Side Build Commands (PowerShell)
Once the Gradle wrapper is generated and Android SDK components are installed, execute:

```powershell
cd D:\NSE_Signal_Provider\android

# Verify Gradle wrapper version
.\gradlew.bat --version

# Clean project build outputs
.\gradlew.bat clean

# Run Android unit tests
.\gradlew.bat test

# Assemble Debug APK
.\gradlew.bat assembleDebug

# Assemble Release APK
.\gradlew.bat assembleRelease
```

## 6. APK Output Locations
- **Debug APK**: `D:\NSE_Signal_Provider\android\app\build\outputs\apk\debug\app-debug.apk`
- **Release APK**: `D:\NSE_Signal_Provider\android\app\build\outputs\apk\release\app-release.apk`

## 7. ADB & Emulator Verification (PowerShell)
```powershell
# Verify ADB
& "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" version
& "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" devices

# List available AVDs
& "$env:LOCALAPPDATA\Android\Sdk\emulator\emulator.exe" -list-avds

# Start Emulator (replace <AVD_NAME> with your AVD)
& "$env:LOCALAPPDATA\Android\Sdk\emulator\emulator.exe" -avd <AVD_NAME>
```

## 8. APK Installation & Testing
```powershell
# Install Debug APK on running emulator/device
& "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" install -r D:\NSE_Signal_Provider\android\app\build\outputs\apk\debug\app-debug.apk

# Monitor logcat during app launch
& "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" logcat -s "com.trademind.nse"
```
