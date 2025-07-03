# POST-DEPLOYMENT FUNCTION LOADER
# This script ensures all functions are loaded after ARM deployment
# Run this if functions don't appear immediately after deployment

param(
    [Parameter(Mandatory=$true)]
    [string]$ResourceGroupName,
    
    [Parameter(Mandatory=$true)]  
    [string]$FunctionAppName,
    
    [string]$SubscriptionId = ""
)

Write-Host "🔄 CoPPA Analytics - Function Loader" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# Check if Azure CLI is available
try {
    $azVersion = az version 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "Azure CLI not found"
    }
} catch {
    Write-Host "❌ Azure CLI not found. Please install Azure CLI or use Azure Cloud Shell." -ForegroundColor Red
    Write-Host "📱 Azure Cloud Shell: https://shell.azure.com" -ForegroundColor Yellow
    return
}

# Set subscription if provided
if ($SubscriptionId) {
    Write-Host "🔄 Setting subscription..." -ForegroundColor Yellow
    az account set --subscription $SubscriptionId
}

Write-Host "🔄 Loading functions for: $FunctionAppName" -ForegroundColor Yellow
Write-Host ""

# Step 1: Get current function app status
Write-Host "1️⃣ Checking current status..." -ForegroundColor Yellow
$appStatus = az functionapp show --name $FunctionAppName --resource-group $ResourceGroupName --query "state" -o tsv
Write-Host "   Status: $appStatus" -ForegroundColor Gray

# Step 2: Stop the function app
Write-Host "2️⃣ Stopping Function App..." -ForegroundColor Yellow
az functionapp stop --name $FunctionAppName --resource-group $ResourceGroupName

# Step 3: Clear and reset package setting
Write-Host "3️⃣ Resetting package deployment..." -ForegroundColor Yellow
az functionapp config appsettings delete --name $FunctionAppName --resource-group $ResourceGroupName --setting-names "WEBSITE_RUN_FROM_PACKAGE"

Start-Sleep -Seconds 10

az functionapp config appsettings set --name $FunctionAppName --resource-group $ResourceGroupName --settings `
    "WEBSITE_RUN_FROM_PACKAGE=https://github.com/Russ-Holloway/CoPPA-Analytics/raw/main/chatbot-analytics-azure-deploy/function-app-final.zip"

# Step 4: Force sync triggers
Write-Host "4️⃣ Syncing function triggers..." -ForegroundColor Yellow
az functionapp function sync --name $FunctionAppName --resource-group $ResourceGroupName

# Step 5: Start the function app
Write-Host "5️⃣ Starting Function App..." -ForegroundColor Yellow
az functionapp start --name $FunctionAppName --resource-group $ResourceGroupName

# Step 6: Wait for initialization
Write-Host "6️⃣ Waiting for initialization (2 minutes)..." -ForegroundColor Yellow
Start-Sleep -Seconds 120

# Step 7: Check function count
Write-Host "7️⃣ Checking functions..." -ForegroundColor Yellow
$functions = az functionapp function list --name $FunctionAppName --resource-group $ResourceGroupName --query "length(@)" -o tsv

if ($functions -eq "6") {
    Write-Host "✅ SUCCESS! All 6 functions are loaded:" -ForegroundColor Green
    $functionList = az functionapp function list --name $FunctionAppName --resource-group $ResourceGroupName --query "[].name" -o tsv
    foreach ($func in $functionList) {
        Write-Host "   ✅ $func" -ForegroundColor Green
    }
} elseif ($functions -gt "0") {
    Write-Host "⚠️ Partial success: $functions functions loaded" -ForegroundColor Yellow
    $functionList = az functionapp function list --name $FunctionAppName --resource-group $ResourceGroupName --query "[].name" -o tsv
    foreach ($func in $functionList) {
        Write-Host "   ✅ $func" -ForegroundColor Green
    }
    Write-Host ""
    Write-Host "💡 Try running this script again in 2-3 minutes." -ForegroundColor Yellow
} else {
    Write-Host "❌ No functions loaded yet." -ForegroundColor Red
    Write-Host "💡 This can happen with Linux Function Apps. Trying restart..." -ForegroundColor Yellow
    
    # Emergency restart
    az functionapp restart --name $FunctionAppName --resource-group $ResourceGroupName
    Start-Sleep -Seconds 120
    
    $functions = az functionapp function list --name $FunctionAppName --resource-group $ResourceGroupName --query "length(@)" -o tsv
    if ($functions -gt "0") {
        Write-Host "✅ Functions loaded after restart!" -ForegroundColor Green
    } else {
        Write-Host "❌ Functions still not loading. This may require Azure support." -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "📊 Function App URL: https://$FunctionAppName.azurewebsites.net" -ForegroundColor Cyan
Write-Host "📈 Analytics API: https://$FunctionAppName.azurewebsites.net/api/GetAnalytics?days=7" -ForegroundColor Cyan
Write-Host "🔧 Azure Portal: https://portal.azure.com" -ForegroundColor Cyan

Write-Host ""
Write-Host "📋 Expected Functions:" -ForegroundColor Gray
Write-Host "   • Dashboard" -ForegroundColor Gray
Write-Host "   • GetAnalytics" -ForegroundColor Gray
Write-Host "   • GetQuestions" -ForegroundColor Gray
Write-Host "   • SeedData" -ForegroundColor Gray
Write-Host "   • TestFunction" -ForegroundColor Gray
Write-Host "   • TimerTrigger" -ForegroundColor Gray
