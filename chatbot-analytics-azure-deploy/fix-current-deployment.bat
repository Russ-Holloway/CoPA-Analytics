@echo off
echo Fixing Python runtime for func-coppa-cop-analytics...
echo.

REM Update Function App settings for Python 3.11
echo Updating Function App settings...
az functionapp config appsettings set --name "func-coppa-cop-analytics" --resource-group "rg-cop-prod-ai-analytics-01" --settings "FUNCTIONS_EXTENSION_VERSION=~4" "FUNCTIONS_WORKER_RUNTIME=python" "FUNCTIONS_WORKER_RUNTIME_VERSION=3.11" "WEBSITE_PYTHON_DEFAULT_VERSION=3.11" "PYTHON_ISOLATE_WORKER_DEPENDENCIES=1" "SCM_DO_BUILD_DURING_DEPLOYMENT=true" "ENABLE_ORYX_BUILD=true" "WEBSITE_NODE_DEFAULT_VERSION=18.x"

REM Force redeploy the function package
echo.
echo Forcing package redeployment...
az functionapp config appsettings set --name "func-coppa-cop-analytics" --resource-group "rg-cop-prod-ai-analytics-01" --settings "WEBSITE_RUN_FROM_PACKAGE=https://github.com/Russ-Holloway/CoPPA-Analytics/raw/main/chatbot-analytics-azure-deploy/function-app-updated.zip"

REM Restart the function app
echo.
echo Restarting Function App...
az functionapp restart --name "func-coppa-cop-analytics" --resource-group "rg-cop-prod-ai-analytics-01"

echo.
echo Fix complete! Wait 2-3 minutes then test: https://func-coppa-cop-analytics.azurewebsites.net/api/GetAnalytics?days=7
pause
