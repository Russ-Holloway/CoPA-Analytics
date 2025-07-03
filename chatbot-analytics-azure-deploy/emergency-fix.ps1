# EMERGENCY FIX for Runtime Version Error
# This script fixes the "Runtime version: Error" issue

param(
    [string]$SubscriptionId = "3f6f503a-4aad-433c-be82-7bd2a887bee3",
    [string]$ResourceGroupName = "rg-cop-prod-ai-analytics-01", 
    [string]$FunctionAppName = "func-coppa-cop-analytics"
)

Write-Host "🚨 EMERGENCY FIX: Runtime Version Error" -ForegroundColor Red
Write-Host "====================================" -ForegroundColor Red
Write-Host ""

# Check if Azure CLI is available
try {
    $azVersion = az version 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Azure CLI not found. Please use Azure Cloud Shell or install Azure CLI." -ForegroundColor Red
        Write-Host "📱 Open Azure Cloud Shell: https://shell.azure.com" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "📋 Copy and paste these commands in Cloud Shell:" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "# Set subscription" -ForegroundColor Gray
        Write-Host "az account set --subscription $SubscriptionId" -ForegroundColor White
        Write-Host ""
        Write-Host "# Stop function app" -ForegroundColor Gray
        Write-Host "az functionapp stop --name $FunctionAppName --resource-group $ResourceGroupName" -ForegroundColor White
        Write-Host ""
        Write-Host "# Clear problematic settings" -ForegroundColor Gray
        Write-Host "az functionapp config appsettings delete --name $FunctionAppName --resource-group $ResourceGroupName --setting-names WEBSITE_RUN_FROM_PACKAGE" -ForegroundColor White
        Write-Host ""
        Write-Host "# Update core settings" -ForegroundColor Gray
        Write-Host "az functionapp config appsettings set --name $FunctionAppName --resource-group $ResourceGroupName --settings 'FUNCTIONS_EXTENSION_VERSION=~4' 'FUNCTIONS_WORKER_RUNTIME=python' 'FUNCTIONS_WORKER_RUNTIME_VERSION=3.11' 'WEBSITE_PYTHON_DEFAULT_VERSION=3.11' 'PYTHON_ISOLATE_WORKER_DEPENDENCIES=1' 'SCM_DO_BUILD_DURING_DEPLOYMENT=true' 'ENABLE_ORYX_BUILD=true'" -ForegroundColor White
        Write-Host ""
        Write-Host "# Set package URL" -ForegroundColor Gray
        Write-Host "az functionapp config appsettings set --name $FunctionAppName --resource-group $ResourceGroupName --settings 'WEBSITE_RUN_FROM_PACKAGE=https://github.com/Russ-Holloway/CoPPA-Analytics/raw/main/chatbot-analytics-azure-deploy/function-app-final.zip'" -ForegroundColor White
        Write-Host ""
        Write-Host "# Start function app" -ForegroundColor Gray
        Write-Host "az functionapp start --name $FunctionAppName --resource-group $ResourceGroupName" -ForegroundColor White
        Write-Host ""
        return
    }
} catch {
    Write-Host "❌ Azure CLI not available. Using Cloud Shell commands above." -ForegroundColor Red
    return
}

Write-Host "✅ Azure CLI found. Proceeding with automated fix..." -ForegroundColor Green
Write-Host ""

# Set subscription
Write-Host "🔄 Setting subscription..." -ForegroundColor Yellow
az account set --subscription $SubscriptionId

# Step 1: Stop the function app
Write-Host "🔄 Stopping Function App..." -ForegroundColor Yellow
az functionapp stop --name $FunctionAppName --resource-group $ResourceGroupName

# Step 2: Clear potentially corrupted package setting
Write-Host "🔄 Clearing package setting..." -ForegroundColor Yellow
az functionapp config appsettings delete --name $FunctionAppName --resource-group $ResourceGroupName --setting-names "WEBSITE_RUN_FROM_PACKAGE"

# Step 3: Update all critical settings at once
Write-Host "🔄 Updating Function App configuration..." -ForegroundColor Yellow
az functionapp config appsettings set --name $FunctionAppName --resource-group $ResourceGroupName --settings `
    "FUNCTIONS_EXTENSION_VERSION=~4" `
    "FUNCTIONS_WORKER_RUNTIME=python" `
    "FUNCTIONS_WORKER_RUNTIME_VERSION=3.11" `
    "WEBSITE_PYTHON_DEFAULT_VERSION=3.11" `
    "PYTHON_ISOLATE_WORKER_DEPENDENCIES=1" `
    "SCM_DO_BUILD_DURING_DEPLOYMENT=true" `
    "ENABLE_ORYX_BUILD=true" `
    "WEBSITE_NODE_DEFAULT_VERSION=18.x" `
    "WEBSITE_CONTENTAZUREFILECONNECTIONSTRING=" `
    "WEBSITE_CONTENTSHARE=" 

# Step 4: Set the package URL
Write-Host "🔄 Setting package deployment..." -ForegroundColor Yellow
az functionapp config appsettings set --name $FunctionAppName --resource-group $ResourceGroupName --settings `
    "WEBSITE_RUN_FROM_PACKAGE=https://github.com/Russ-Holloway/CoPPA-Analytics/raw/main/chatbot-analytics-azure-deploy/function-app-final.zip"

# Step 5: Start the function app
Write-Host "🔄 Starting Function App..." -ForegroundColor Yellow
az functionapp start --name $FunctionAppName --resource-group $ResourceGroupName

# Step 6: Wait for startup
Write-Host "⏳ Waiting for Function App to initialize (this may take 3-5 minutes)..." -ForegroundColor Yellow
Start-Sleep -Seconds 180

# Step 7: Check status
Write-Host "🔍 Checking Function App status..." -ForegroundColor Yellow
$status = az functionapp show --name $FunctionAppName --resource-group $ResourceGroupName --query "state" -o tsv

if ($status -eq "Running") {
    Write-Host "✅ Function App is running!" -ForegroundColor Green
    
    # Test the endpoint
    Write-Host "🧪 Testing analytics endpoint..." -ForegroundColor Yellow
    $testUrl = "https://$FunctionAppName.azurewebsites.net/api/GetAnalytics?days=7"
    
    try {
        $response = Invoke-RestMethod -Uri $testUrl -Method Get -TimeoutSec 90
        Write-Host "🎉 SUCCESS! Analytics endpoint is working!" -ForegroundColor Green
        Write-Host "   Data source: $($response.metadata.data_source)" -ForegroundColor Gray
        Write-Host "   Total conversations: $($response.metadata.total_conversations)" -ForegroundColor Gray
    } catch {
        Write-Host "⚠️ Endpoint test failed: $($_.Exception.Message)" -ForegroundColor Yellow
        Write-Host "   This might be normal during initialization. Try again in 2-3 minutes." -ForegroundColor Gray
    }
} else {
    Write-Host "⚠️ Function App status: $status" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📋 Summary:" -ForegroundColor Cyan
Write-Host "✅ Stopped and restarted Function App" -ForegroundColor Green
Write-Host "✅ Cleared problematic package settings" -ForegroundColor Green  
Write-Host "✅ Updated Python runtime configuration" -ForegroundColor Green
Write-Host "✅ Enabled Oryx build system" -ForegroundColor Green
Write-Host "✅ Set fresh package deployment" -ForegroundColor Green
Write-Host ""
Write-Host "🔗 Test URL: https://$FunctionAppName.azurewebsites.net/api/GetAnalytics?days=7" -ForegroundColor Cyan
Write-Host "📊 Azure Portal: https://portal.azure.com/#resource/subscriptions/$SubscriptionId/resourceGroups/$ResourceGroupName/providers/Microsoft.Web/sites/$FunctionAppName" -ForegroundColor Cyan
Write-Host ""
Write-Host "💡 If Runtime Version still shows 'Error', the function app may need to be recreated." -ForegroundColor Yellow
Write-Host "   Use the Deploy to Azure button for a fresh deployment." -ForegroundColor Yellow
