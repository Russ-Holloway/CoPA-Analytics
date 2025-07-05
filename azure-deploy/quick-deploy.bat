@echo off
REM CoPPA Analytics Quick Deploy for Police Forces
REM Double-click this file to deploy CoPPA Analytics

echo.
echo 🚔 CoPPA Analytics - Quick Deployment for Police Forces
echo ==================================================
echo.

REM Check if Azure CLI is installed
where az >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Azure CLI not found. Please install it first:
    echo https://docs.microsoft.com/en-us/cli/azure/install-azure-cli
    pause
    exit /b 1
)

REM Prompt for force details
set /p FORCE_CODE="Enter your police force code (e.g., BTP, MET, GMP): "
set /p ADMIN_EMAIL="Enter admin email for reports: "
set /p REGION="Enter Azure region (default: uksouth): "
if "%REGION%"=="" set REGION=uksouth

REM Create resource group name
for /f %%i in ('echo %FORCE_CODE%') do set FORCE_LOWER=%%i
call :LoCase FORCE_LOWER
set RG_NAME=rg-coppa-analytics-%FORCE_LOWER%

echo.
echo Creating resource group: %RG_NAME%
az group create --name %RG_NAME% --location %REGION%

echo.
echo Deploying CoPPA Analytics...
az deployment group create ^
    --resource-group %RG_NAME% ^
    --template-uri "https://raw.githubusercontent.com/british-transport-police/AI-Analytics/main/chatbot-analytics-azure-deploy/azuredeploy.json" ^
    --parameters forcePrefix=%FORCE_CODE% adminEmail=%ADMIN_EMAIL%

if %errorlevel% equ 0 (
    echo.
    echo ✅ Deployment complete!
    echo Your dashboard: https://func-coppa-%FORCE_LOWER%-analytics.azurewebsites.net/api/Dashboard
    echo.
    echo 📧 Daily reports will be sent to: %ADMIN_EMAIL%
    echo.
) else (
    echo.
    echo ❌ Deployment failed. Please check the error messages above.
    echo.
)

echo Press any key to continue...
pause >nul
exit /b

:LoCase
for %%i in ("A=a" "B=b" "C=c" "D=d" "E=e" "F=f" "G=g" "H=h" "I=i" "J=j" "K=k" "L=l" "M=m" "N=n" "O=o" "P=p" "Q=q" "R=r" "S=s" "T=t" "U=u" "V=v" "W=w" "X=x" "Y=y" "Z=z") do call set "%1=%%%1:%%~i%%"
goto :eof
