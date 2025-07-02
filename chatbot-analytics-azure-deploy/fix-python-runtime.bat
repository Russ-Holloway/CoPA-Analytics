@echo off
echo CoPPA Analytics - Python Runtime Fix
echo ====================================
echo.

set /p RESOURCE_GROUP="Enter your Resource Group name: "
set /p FUNCTION_APP="Enter your Function App name: "

echo.
echo Fixing Python runtime issues...
echo Resource Group: %RESOURCE_GROUP%
echo Function App: %FUNCTION_APP%
echo.

powershell -ExecutionPolicy Bypass -File "%~dp0fix-python-runtime.ps1" -ResourceGroupName "%RESOURCE_GROUP%" -FunctionAppName "%FUNCTION_APP%"

echo.
pause
