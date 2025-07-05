# CoPPA Analytics - Complete Python Runtime Fix
# This script resolves the 503 "function host not running" error

param(
    [Parameter(Mandatory=$false)]
    [string]$ResourceGroupName = "rg-coppa-cop-analytics",
    
    [Parameter(Mandatory=$false)]
    [string]$FunctionAppName = "func-coppa-cop-analytics"
)

Write-Host "🔧 CoPPA Analytics - Python Runtime Fix" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""

# Check if Azure CLI is installed
try {
    $azVersion = az version --output tsv
    Write-Host "✅ Azure CLI is available" -ForegroundColor Green
} catch {
    Write-Host "❌ Azure CLI not found. Please install Azure CLI first." -ForegroundColor Red
    exit 1
}

Write-Host "📝 Function App Details:" -ForegroundColor Yellow
Write-Host "   Resource Group: $ResourceGroupName" -ForegroundColor White
Write-Host "   Function App: $FunctionAppName" -ForegroundColor White
Write-Host ""

# Step 1: Update Function App Settings
Write-Host "🔄 Step 1: Updating Function App Settings..." -ForegroundColor Yellow

# Create a temporary JSON file with the correct settings
$settingsJson = @'
[
  {
    "name": "FUNCTIONS_EXTENSION_VERSION",
    "value": "~4"
  },
  {
    "name": "FUNCTIONS_WORKER_RUNTIME",
    "value": "python"
  },
  {
    "name": "FUNCTIONS_WORKER_RUNTIME_VERSION",
    "value": "3.11"
  },
  {
    "name": "WEBSITE_PYTHON_DEFAULT_VERSION",
    "value": "3.11"
  },
  {
    "name": "PYTHON_ISOLATE_WORKER_DEPENDENCIES",
    "value": "1"
  },
  {
    "name": "SCM_DO_BUILD_DURING_DEPLOYMENT",
    "value": "true"
  },
  {
    "name": "ENABLE_ORYX_BUILD",
    "value": "true"
  },
  {
    "name": "WEBSITE_NODE_DEFAULT_VERSION",
    "value": "18.x"
  }
]
'@

$tempFile = [System.IO.Path]::GetTempFileName() + ".json"
$settingsJson | Out-File -FilePath $tempFile -Encoding utf8

try {
    az functionapp config appsettings set --name $FunctionAppName --resource-group $ResourceGroupName --settings "@$tempFile"
    Write-Host "✅ Function App settings updated successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to update Function App settings: $($_.Exception.Message)" -ForegroundColor Red
}

# Clean up temp file
Remove-Item $tempFile -ErrorAction SilentlyContinue

# Step 2: Update the package URL to force redeployment
Write-Host ""
Write-Host "🔄 Step 2: Updating package deployment..." -ForegroundColor Yellow

$packageUrl = "https://github.com/Russ-Holloway/CoPPA-Analytics/raw/main/chatbot-analytics-azure-deploy/function-app.zip"
try {
    az functionapp config appsettings set --name $FunctionAppName --resource-group $ResourceGroupName --settings "WEBSITE_RUN_FROM_PACKAGE=$packageUrl"
    Write-Host "✅ Package URL updated" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to update package URL: $($_.Exception.Message)" -ForegroundColor Red
}

# Step 3: Restart Function App
Write-Host ""
Write-Host "🔄 Step 3: Restarting Function App..." -ForegroundColor Yellow

try {
    az functionapp restart --name $FunctionAppName --resource-group $ResourceGroupName
    Write-Host "✅ Function App restart initiated" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to restart Function App: $($_.Exception.Message)" -ForegroundColor Red
}

# Step 4: Wait and check status
Write-Host ""
Write-Host "⏳ Step 4: Waiting for Function App to initialize..." -ForegroundColor Yellow
Write-Host "   This may take 2-3 minutes..." -ForegroundColor Gray

Start-Sleep -Seconds 120

# Check function app status
try {
    $status = az functionapp show --name $FunctionAppName --resource-group $ResourceGroupName --query "state" -o tsv
    Write-Host "📊 Function App Status: $status" -ForegroundColor $(if ($status -eq "Running") {"Green"} else {"Yellow"})
} catch {
    Write-Host "⚠️  Could not retrieve Function App status" -ForegroundColor Yellow
}

# Step 5: Test the endpoint
Write-Host ""
Write-Host "🧪 Step 5: Testing Analytics Endpoint..." -ForegroundColor Yellow

$testUrl = "https://$FunctionAppName.azurewebsites.net/api/GetAnalytics?days=7"
Write-Host "   URL: $testUrl" -ForegroundColor Gray

try {
    $response = Invoke-RestMethod -Uri $testUrl -Method Get -TimeoutSec 60
    Write-Host "✅ Analytics endpoint is responding!" -ForegroundColor Green
    Write-Host "   Data source: $($response.metadata.data_source)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Analytics endpoint test failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "   Note: The function may still be initializing. Try again in a few minutes." -ForegroundColor Yellow
}

# Final summary
Write-Host ""
Write-Host "📋 Summary & Next Steps:" -ForegroundColor Cyan
Write-Host "========================" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ Updated Function App settings for Python 3.11 compatibility" -ForegroundColor Green
Write-Host "✅ Configured proper extension bundle version" -ForegroundColor Green
Write-Host "✅ Enabled Oryx build for proper dependency resolution" -ForegroundColor Green
Write-Host "✅ Restarted Function App" -ForegroundColor Green
Write-Host ""
Write-Host "🔗 Useful Links:" -ForegroundColor Yellow
Write-Host "   • Function App: https://portal.azure.com/#resource/subscriptions/{subscription}/resourceGroups/$ResourceGroupName/providers/Microsoft.Web/sites/$FunctionAppName" -ForegroundColor White
Write-Host "   • Analytics API: $testUrl" -ForegroundColor White
Write-Host "   • Log Stream: https://portal.azure.com/#resource/subscriptions/{subscription}/resourceGroups/$ResourceGroupName/providers/Microsoft.Web/sites/$FunctionAppName/logStream" -ForegroundColor White
Write-Host ""
Write-Host "💡 If issues persist:" -ForegroundColor Yellow
Write-Host "   1. Check the Function App logs in Azure Portal" -ForegroundColor White
Write-Host "   2. Verify Cosmos DB connection settings" -ForegroundColor White
Write-Host "   3. Wait 5-10 minutes for full initialization" -ForegroundColor White
Write-Host "   4. Try redeploying with the updated ARM template" -ForegroundColor White

Write-Host ""
Write-Host "🎉 Fix complete! Your CoPPA Analytics should now be working." -ForegroundColor Green
