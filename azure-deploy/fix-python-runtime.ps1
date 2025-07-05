# Fix Python Runtime Issues for CoPPA Analytics Function App
# This script updates the function app settings to resolve Python 3.11 runtime issues

param(
    [Parameter(Mandatory=$true)]
    [string]$ResourceGroupName,
    
    [Parameter(Mandatory=$true)]
    [string]$FunctionAppName
)

Write-Host "Fixing Python runtime issues for Function App: $FunctionAppName" -ForegroundColor Green

# Update Function App settings for Python 3.11 compatibility
Write-Host "Updating Function App configuration..." -ForegroundColor Yellow

# Set the correct runtime settings
az functionapp config appsettings set --name $FunctionAppName --resource-group $ResourceGroupName --settings @'
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
  }
]
'@

# Restart the function app to apply changes
Write-Host "Restarting Function App to apply changes..." -ForegroundColor Yellow
az functionapp restart --name $FunctionAppName --resource-group $ResourceGroupName

Write-Host "Waiting 30 seconds for restart to complete..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Check function app status
Write-Host "Checking Function App status..." -ForegroundColor Yellow
$status = az functionapp show --name $FunctionAppName --resource-group $ResourceGroupName --query "state" -o tsv

if ($status -eq "Running") {
    Write-Host "✅ Function App is now running!" -ForegroundColor Green
} else {
    Write-Host "⚠️  Function App status: $status" -ForegroundColor Yellow
}

# Test the analytics endpoint
Write-Host "Testing analytics endpoint..." -ForegroundColor Yellow
$url = "https://$FunctionAppName.azurewebsites.net/api/GetAnalytics?days=7"
try {
    $response = Invoke-RestMethod -Uri $url -Method Get -TimeoutSec 30
    Write-Host "✅ Analytics endpoint is responding!" -ForegroundColor Green
} catch {
    Write-Host "❌ Analytics endpoint test failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "This might be normal if the function is still initializing." -ForegroundColor Yellow
}

Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "1. Wait 2-3 minutes for the function app to fully initialize" -ForegroundColor White
Write-Host "2. Check the Function App logs in the Azure portal" -ForegroundColor White
Write-Host "3. Test the analytics endpoint: $url" -ForegroundColor White
