@echo off
REM Build the PestWatch Android APK.
REM Uses Android Studio's bundled JDK and the local Android SDK.

set "JAVA_HOME=C:\Program Files\Android\Android Studio\jbr"
set "ANDROID_SDK_ROOT=%LOCALAPPDATA%\Android\Sdk"
set "ANDROID_HOME=%LOCALAPPDATA%\Android\Sdk"

echo Using JAVA_HOME=%JAVA_HOME%
echo Using ANDROID_SDK_ROOT=%ANDROID_SDK_ROOT%

REM 1. sync the web app into the android project
call npx cap sync android
if errorlevel 1 goto :err

REM 2. build the debug APK
cd android
call gradlew.bat assembleDebug
if errorlevel 1 goto :err
cd ..

echo.
echo ===============================================================
echo  APK built:
echo   android\app\build\outputs\apk\debug\app-debug.apk
echo  Install it on a phone (same Wi-Fi as this PC, server running).
echo ===============================================================
goto :eof

:err
echo BUILD FAILED - see the error above.
exit /b 1
