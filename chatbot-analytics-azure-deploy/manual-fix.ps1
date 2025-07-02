# Manual Fix for Current Deployment
# Copy and paste these commands in Azure Cloud Shell or local Azure CLI

Write-Host "🔧 Fixing func-coppa-cop-analytics deployment..." -ForegroundColor Cyan

# Step 1: Update critical function app settings
Write-Host "1. Updating Function App settings..." -ForegroundColor Yellow
az functionapp config appsettings set --name "func-coppa-cop-analytics" --resource-group "rg-cop-prod-ai-analytics-01" --settings `
  "FUNCTIONS_EXTENSION_VERSION=~4" `
  "FUNCTIONS_WORKER_RUNTIME=python" `
  "FUNCTIONS_WORKER_RUNTIME_VERSION=3.11" `
  "WEBSITE_PYTHON_DEFAULT_VERSION=3.11" `
  "PYTHON_ISOLATE_WORKER_DEPENDENCIES=1" `
  "SCM_DO_BUILD_DURING_DEPLOYMENT=true" `
  "ENABLE_ORYX_BUILD=true" `
  "WEBSITE_NODE_DEFAULT_VERSION=18.x"

# Step 2: Force redownload the updated package
Write-Host "2. Forcing package redeployment..." -ForegroundColor Yellow
az functionapp config appsettings set --name "func-coppa-cop-analytics" --resource-group "rg-cop-prod-ai-analytics-01" --settings `
  "WEBSITE_RUN_FROM_PACKAGE=https://github.com/Russ-Holloway/CoPPA-Analytics/raw/main/chatbot-analytics-azure-deploy/function-app.zip?$(Get-Date -Format 'yyyyMMddHHmmss')"

# Step 3: Stop and start the function app for full restart
Write-Host "3. Stopping Function App..." -ForegroundColor Yellow
az functionapp stop --name "func-coppa-cop-analytics" --resource-group "rg-cop-prod-ai-analytics-01"

Start-Sleep -Seconds 10

Write-Host "4. Starting Function App..." -ForegroundColor Yellow
az functionapp start --name "func-coppa-cop-analytics" --resource-group "rg-cop-prod-ai-analytics-01"

Write-Host "5. Waiting for startup..." -ForegroundColor Yellow
Start-Sleep -Seconds 120

# Step 4: Test the deployment
Write-Host "6. Testing deployment..." -ForegroundColor Yellow
$testUrl = "https://func-coppa-cop-analytics.azurewebsites.net/api/GetAnalytics?days=7"

try {
    $response = Invoke-RestMethod -Uri $testUrl -Method Get -TimeoutSec 60
    Write-Host "✅ SUCCESS! Analytics endpoint is working!" -ForegroundColor Green
    Write-Host "Data source: $($response.metadata.data_source)" -ForegroundColor Gray
} catch {
    Write-Host "⚠️ Endpoint test failed, but this might be normal during startup" -ForegroundColor Yellow
    Write-Host "Wait 2-3 more minutes and test manually: $testUrl" -ForegroundColor White
}

Write-Host ""
Write-Host "🎉 Fix completed!" -ForegroundColor Green
Write-Host "Test your analytics: $testUrl" -ForegroundColor Cyan
