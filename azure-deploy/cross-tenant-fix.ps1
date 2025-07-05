# CROSS-TENANT FUNCTION APP FIX
# Use this when the Function App is in a different Azure tenant/organization
# This script only outputs commands - does not execute anything

param(
    [string]$SubscriptionId,
    [string]$ResourceGroupName, 
    [string]$FunctionAppName
)

Write-Host "🌐 CROSS-TENANT AZURE FUNCTION APP FIX" -ForegroundColor Magenta
Write-Host "=====================================" -ForegroundColor Magenta
Write-Host ""
Write-Host "This script provides commands for fixing function deployment issues" -ForegroundColor Yellow
Write-Host "when the Function App is in a different Azure tenant/organization." -ForegroundColor Yellow
Write-Host ""

# Prompt for parameters if not provided
if (-not $SubscriptionId) {
    $SubscriptionId = Read-Host "Enter your Azure Subscription ID"
}
if (-not $ResourceGroupName) {
    $ResourceGroupName = Read-Host "Enter your Resource Group Name"
}
if (-not $FunctionAppName) {
    $FunctionAppName = Read-Host "Enter your Function App Name"
}

Write-Host ""
Write-Host "🔑 STEP 1: Open Azure Cloud Shell in the correct tenant" -ForegroundColor Cyan
Write-Host "   🌐 Go to: https://shell.azure.com" -ForegroundColor White
Write-Host "   ⚠️  Make sure you're logged into the CORRECT tenant/organization!" -ForegroundColor Red
Write-Host ""

Write-Host "🔍 STEP 2: Verify your context" -ForegroundColor Cyan
Write-Host "   Run this first to check you're in the right place:" -ForegroundColor White
Write-Host "   az account show" -ForegroundColor Yellow
Write-Host ""

Write-Host "📋 STEP 3: Copy and paste ALL commands below" -ForegroundColor Cyan
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
Write-Host "# Set correct subscription" -ForegroundColor Gray
Write-Host "az account set --subscription $SubscriptionId" -ForegroundColor White
Write-Host ""
Write-Host "# Stop function app to reset state" -ForegroundColor Gray
Write-Host "az functionapp stop --name $FunctionAppName --resource-group $ResourceGroupName" -ForegroundColor White
Write-Host ""
Write-Host "# Clear problematic package setting" -ForegroundColor Gray
Write-Host "az functionapp config appsettings delete --name $FunctionAppName --resource-group $ResourceGroupName --setting-names WEBSITE_RUN_FROM_PACKAGE" -ForegroundColor White
Write-Host ""
Write-Host "# Configure Python 3.11 runtime" -ForegroundColor Gray
Write-Host "az functionapp config appsettings set --name $FunctionAppName --resource-group $ResourceGroupName --settings 'FUNCTIONS_EXTENSION_VERSION=~4' 'FUNCTIONS_WORKER_RUNTIME=python' 'FUNCTIONS_WORKER_RUNTIME_VERSION=3.11' 'WEBSITE_PYTHON_DEFAULT_VERSION=3.11' 'PYTHON_ISOLATE_WORKER_DEPENDENCIES=1' 'SCM_DO_BUILD_DURING_DEPLOYMENT=true' 'ENABLE_ORYX_BUILD=true'" -ForegroundColor White
Write-Host ""
Write-Host "# Deploy function package" -ForegroundColor Gray
Write-Host "az functionapp config appsettings set --name $FunctionAppName --resource-group $ResourceGroupName --settings 'WEBSITE_RUN_FROM_PACKAGE=https://github.com/Russ-Holloway/CoPPA-Analytics/raw/main/chatbot-analytics-azure-deploy/function-app-final.zip'" -ForegroundColor White
Write-Host ""
Write-Host "# Start function app" -ForegroundColor Gray
Write-Host "az functionapp start --name $FunctionAppName --resource-group $ResourceGroupName" -ForegroundColor White
Write-Host ""
Write-Host "# Wait for initialization (3-5 minutes)" -ForegroundColor Gray
Write-Host "echo 'Function App is starting... Please wait 3-5 minutes before testing.'" -ForegroundColor White
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
Write-Host ""

Write-Host "⏳ STEP 4: Wait and test" -ForegroundColor Cyan
Write-Host "   Wait 3-5 minutes for the Function App to fully initialize" -ForegroundColor Yellow
Write-Host "   Then test: https://$FunctionAppName.azurewebsites.net/api/GetAnalytics?days=7" -ForegroundColor White
Write-Host ""

Write-Host "📊 STEP 5: Check in Azure Portal" -ForegroundColor Cyan
Write-Host "   Go to: https://portal.azure.com" -ForegroundColor White
Write-Host "   Navigate to your Function App and check the Functions tab" -ForegroundColor Gray
Write-Host "   You should see: GetAnalytics, Dashboard, GetQuestions, SeedData, TestFunction, TimerTrigger, FunctionSync" -ForegroundColor Gray
Write-Host ""

Write-Host "🆘 If this doesn't work:" -ForegroundColor Red
Write-Host "   1. Try deploying fresh using the 'Deploy to Azure' button" -ForegroundColor Yellow
Write-Host "   2. The Function App may need to be deleted and recreated" -ForegroundColor Yellow
Write-Host "   3. Check that the ZIP file is accessible from Azure" -ForegroundColor Yellow
Write-Host ""

Write-Host "✅ Commands prepared for cross-tenant deployment!" -ForegroundColor Green
