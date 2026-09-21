@echo off
title AssistIQ Android Mobile Runner - Clean Fresh Install
echo ========================================================
echo   AssistIQ Android Mobile Runner (Fresh Update)
echo ========================================================
echo.

set PATH=E:\flutter\bin;C:\Android\sdk\platform-tools;%PATH%
set ANDROID_HOME=C:\Android\sdk

echo 1. Checking connected devices...
C:\Android\sdk\platform-tools\adb.exe devices
echo.

echo 2. Uninstalling previous version to clear stale cache...
C:\Android\sdk\platform-tools\adb.exe uninstall com.assistiq.assistiq_flutter
echo.

echo 3. Installing fresh 100% updated AssistIQ APK...
C:\Android\sdk\platform-tools\adb.exe install -r E:\AssistIQ\flutter_app\build\app\outputs\flutter-apk\app-debug.apk
echo.

echo 4. Launching updated AssistIQ on phone screen...
C:\Android\sdk\platform-tools\adb.exe shell am start -n com.assistiq.assistiq_flutter/com.assistiq.assistiq_flutter.MainActivity

echo.
echo ========================================================
echo   Done! Updated AssistIQ is running on your phone!
echo ========================================================
pause
