import shutil
from pathlib import Path

root = Path(__file__).resolve().parents[1]
dist_dir = root / ".gradle-dist"
android_dir = root / "android"
wrapper_dir = android_dir / "gradle" / "wrapper"
wrapper_dir.mkdir(parents=True, exist_ok=True)

shutil.copy2(dist_dir / "gradle-8.9" / "lib" / "plugins" / "gradle-wrapper-main-8.9.jar", wrapper_dir / "gradle-wrapper.jar")
shutil.copy2(dist_dir / "gradle-8.9" / "lib" / "gradle-wrapper-shared-8.9.jar", wrapper_dir / "gradle-wrapper-shared.jar")

props = """distributionBase=GRADLE_USER_HOME
distributionPath=wrapper/dists
distributionUrl=https\\://services.gradle.org/distributions/gradle-8.9-bin.zip
zipStoreBase=GRADLE_USER_HOME
zipStorePath=wrapper/dists
"""
(wrapper_dir / "gradle-wrapper.properties").write_text(props, encoding="utf-8")

bat_content = """@if "%DEBUG%" == "" @echo off
if "%OS%"=="Windows_NT" setlocal

set DIRNAME=%~dp0
if "%DIRNAME%"=="" set DIRNAME=.
set APP_BASE_NAME=%~n0
set APP_HOME=%DIRNAME%

pushd "%APP_HOME%"
set APP_HOME=%CD%
popd

if "%JAVA_HOME%" == "" goto gnu_java_install_error

set JAVA_EXE=%JAVA_HOME%\\bin\\java.exe
if exist "%JAVA_EXE%" goto execute

echo.
echo ERROR: JAVA_HOME is set to an invalid directory: %JAVA_HOME%
echo.
goto fail

:gnu_java_install_error
echo.
echo ERROR: JAVA_HOME is not set and no 'java' command could be found in your PATH.
echo.
goto fail

:execute
set CLASSPATH=%APP_HOME%\\gradle\\wrapper\\gradle-wrapper.jar;%APP_HOME%\\gradle\\wrapper\\gradle-wrapper-shared.jar

"%JAVA_EXE%" %DEFAULT_JVM_OPTS% %JAVA_OPTS% %GRADLE_OPTS% "-Dorg.gradle.appname=%APP_BASE_NAME%" -classpath "%CLASSPATH%" org.gradle.wrapper.GradleWrapperMain %*

if ERRORLEVEL 1 goto fail

:end
if "%OS%"=="Windows_NT" endlocal
exit /b %EXIT_CODE%

:fail
exit /b 1
"""
(android_dir / "gradlew.bat").write_text(bat_content, encoding="utf-8")
print("Gradle wrapper with shared jar established!")
