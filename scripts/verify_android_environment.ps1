# V30 Android Environment Verification Script (Read-Only Diagnostic)
Write-Host "=== V30 Android Environment Validation ===" -ForegroundColor Cyan

# 1. Java
if ($env:JAVA_HOME) {
    Write-Host "[PASS] JAVA_HOME set to: $env:JAVA_HOME" -ForegroundColor Green
} else {
    Write-Host "[MISSING] JAVA_HOME environment variable is not set." -ForegroundColor Yellow
}

try {
    $javaVer = java -version 2>&1
    Write-Host "[PASS] Java available: $javaVer" -ForegroundColor Green
} catch {
    Write-Host "[MISSING] Java not found in PATH." -ForegroundColor Red
}

# 2. Android SDK
$sdkPath = "$env:LOCALAPPDATA\Android\Sdk"
if ($env:ANDROID_HOME) { $sdkPath = $env:ANDROID_HOME }
elseif ($env:ANDROID_SDK_ROOT) { $sdkPath = $env:ANDROID_SDK_ROOT }

if (Test-Path $sdkPath) {
    Write-Host "[PASS] Android SDK found at: $sdkPath" -ForegroundColor Green

    # Check Platform 35
    if (Test-Path "$sdkPath\platforms\android-35") {
        Write-Host "[PASS] Android SDK Platform 35 installed." -ForegroundColor Green
    } else {
        Write-Host "[MISSING] Android SDK Platform 35 not found under platforms\" -ForegroundColor Yellow
    }

    # Check Platform-Tools (adb)
    if (Test-Path "$sdkPath\platform-tools\adb.exe") {
        Write-Host "[PASS] Android Platform-Tools (adb.exe) found." -ForegroundColor Green
    } else {
        Write-Host "[MISSING] adb.exe not found in platform-tools\" -ForegroundColor Yellow
    }

    # Check Build-Tools
    if (Test-Path "$sdkPath\build-tools") {
        Write-Host "[PASS] Android Build-Tools directory found." -ForegroundColor Green
    } else {
        Write-Host "[MISSING] Build-Tools directory not found." -ForegroundColor Yellow
    }

    # Check Emulator
    if (Test-Path "$sdkPath\emulator\emulator.exe") {
        Write-Host "[PASS] Android Emulator found." -ForegroundColor Green
    } else {
        Write-Host "[MISSING] Android Emulator not found." -ForegroundColor Yellow
    }
} else {
    Write-Host "[MISSING] Android SDK not found at default location: $sdkPath" -ForegroundColor Red
}

# 3. Gradle Wrapper
$androidProj = "D:\NSE_Signal_Provider\android"
if (Test-Path "$androidProj\gradlew.bat") {
    Write-Host "[PASS] Gradle wrapper found (gradlew.bat)." -ForegroundColor Green
} else {
    Write-Host "[NOT CONFIGURED] Gradle wrapper missing from android/ directory." -ForegroundColor Yellow
}

# 4. Google Services JSON
if (Test-Path "$androidProj\app\google-services.json") {
    Write-Host "[PASS] google-services.json present in app/." -ForegroundColor Green
} else {
    Write-Host "[MISSING] google-services.json missing from app/." -ForegroundColor Red
}

Write-Host "=== Validation Check Complete ===" -ForegroundColor Cyan
