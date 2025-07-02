# CoPPA Analytics - Post-Deployment Verification Script
# This script validates the deployment after using "Deploy to Azure" button

param(
    [Parameter(Mandatory=$true)]
    [string]$ResourceGroupName,
    
    [Parameter(Mandatory=$false)]
    [string]$SubscriptionId
)

Write-Host "🔍 CoPPA Analytics - Post-Deployment Verification" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host ""

# Set subscription if provided
if ($SubscriptionId) {
    Write-Host "🔄 Setting Azure subscription..." -ForegroundColor Yellow
    az account set --subscription $SubscriptionId
}

# Get deployment outputs
Write-Host "📋 Retrieving deployment information..." -ForegroundColor Yellow
try {
    $deployment = az deployment group list --resource-group $ResourceGroupName --query "[0]" | ConvertFrom-Json
    
    if ($deployment) {
        $outputs = $deployment.properties.outputs
        $functionAppName = $outputs.functionAppName.value
        $storageAccountName = $outputs.storageAccountName.value
        $dashboardUrl = $outputs.coppaAnalyticsDashboard.value
        $apiUrl = $outputs.coppaAnalyticsAPI.value
        
        Write-Host "✅ Deployment found:" -ForegroundColor Green
        Write-Host "   Function App: $functionAppName" -ForegroundColor White
        Write-Host "   Storage Account: $storageAccountName" -ForegroundColor White
        Write-Host "   Dashboard URL: $dashboardUrl" -ForegroundColor White
        Write-Host "   API URL: $apiUrl" -ForegroundColor White
    }
} catch {
    Write-Host "⚠️  Could not retrieve deployment outputs. Continuing with manual lookup..." -ForegroundColor Yellow
    
    # Try to find resources manually
    $functionApp = az functionapp list --resource-group $ResourceGroupName --query "[0]" | ConvertFrom-Json
    if ($functionApp) {
        $functionAppName = $functionApp.name
        Write-Host "✅ Found Function App: $functionAppName" -ForegroundColor Green
    } else {
        Write-Host "❌ No Function App found in resource group" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""

# Step 1: Verify Function App is running
Write-Host "🔄 Step 1: Checking Function App status..." -ForegroundColor Yellow
try {
    $appStatus = az functionapp show --name $functionAppName --resource-group $ResourceGroupName --query "state" -o tsv
    
    if ($appStatus -eq "Running") {
        Write-Host "✅ Function App is running" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Function App status: $appStatus" -ForegroundColor Yellow
        Write-Host "   Attempting to start Function App..." -ForegroundColor Yellow
        az functionapp start --name $functionAppName --resource-group $ResourceGroupName
        Start-Sleep -Seconds 30
    }
} catch {
    Write-Host "❌ Error checking Function App status: $($_.Exception.Message)" -ForegroundColor Red
}

# Step 2: Verify Python runtime settings
Write-Host ""
Write-Host "🔄 Step 2: Verifying Python runtime configuration..." -ForegroundColor Yellow

$requiredSettings = @{
    "FUNCTIONS_EXTENSION_VERSION" = "~4"
    "FUNCTIONS_WORKER_RUNTIME" = "python"
    "FUNCTIONS_WORKER_RUNTIME_VERSION" = "3.11"
    "WEBSITE_PYTHON_DEFAULT_VERSION" = "3.11"
    "PYTHON_ISOLATE_WORKER_DEPENDENCIES" = "1"
    "SCM_DO_BUILD_DURING_DEPLOYMENT" = "true"
    "ENABLE_ORYX_BUILD" = "true"
}

$needsUpdate = $false
try {
    $currentSettings = az functionapp config appsettings list --name $functionAppName --resource-group $ResourceGroupName | ConvertFrom-Json
    $settingsHash = @{}
    $currentSettings | ForEach-Object { $settingsHash[$_.name] = $_.value }
    
    foreach ($setting in $requiredSettings.GetEnumerator()) {
        $currentValue = $settingsHash[$setting.Key]
        if ($currentValue -ne $setting.Value) {
            Write-Host "⚠️  Setting '$($setting.Key)' needs update: '$currentValue' → '$($setting.Value)'" -ForegroundColor Yellow
            $needsUpdate = $true
        } else {
            Write-Host "✅ Setting '$($setting.Key)' is correct: '$($setting.Value)'" -ForegroundColor Green
        }
    }
} catch {
    Write-Host "❌ Error checking app settings: $($_.Exception.Message)" -ForegroundColor Red
    $needsUpdate = $true
}

# Update settings if needed
if ($needsUpdate) {
    Write-Host ""
    Write-Host "🔧 Updating Function App settings..." -ForegroundColor Yellow
    
    foreach ($setting in $requiredSettings.GetEnumerator()) {
        try {
            az functionapp config appsettings set --name $functionAppName --resource-group $ResourceGroupName --settings "$($setting.Key)=$($setting.Value)" --output none
            Write-Host "✅ Updated: $($setting.Key)" -ForegroundColor Green
        } catch {
            Write-Host "❌ Failed to update: $($setting.Key)" -ForegroundColor Red
        }
    }
    
    # Restart after updates
    Write-Host ""
    Write-Host "🔄 Restarting Function App to apply changes..." -ForegroundColor Yellow
    az functionapp restart --name $functionAppName --resource-group $ResourceGroupName
    
    Write-Host "⏳ Waiting 2 minutes for Function App to initialize..." -ForegroundColor Yellow
    Start-Sleep -Seconds 120
}

# Step 3: Test Functions
Write-Host ""
Write-Host "🔄 Step 3: Testing Function endpoints..." -ForegroundColor Yellow

# Test Analytics endpoint
$analyticsUrl = "https://$functionAppName.azurewebsites.net/api/GetAnalytics?days=7"
Write-Host "   Testing: $analyticsUrl" -ForegroundColor Gray

try {
    $response = Invoke-RestMethod -Uri $analyticsUrl -Method Get -TimeoutSec 60
    Write-Host "✅ Analytics endpoint is working!" -ForegroundColor Green
    Write-Host "   Data source: $($response.metadata.data_source)" -ForegroundColor Gray
    Write-Host "   Total conversations: $($response.metadata.total_conversations)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Analytics endpoint failed: $($_.Exception.Message)" -ForegroundColor Red
    
    # Check if it's a cold start issue
    if ($_.Exception.Message -match "timeout|502|503") {
        Write-Host "⏳ This might be a cold start. Trying again in 30 seconds..." -ForegroundColor Yellow
        Start-Sleep -Seconds 30
        
        try {
            $response = Invoke-RestMethod -Uri $analyticsUrl -Method Get -TimeoutSec 60
            Write-Host "✅ Analytics endpoint is working (after retry)!" -ForegroundColor Green
        } catch {
            Write-Host "❌ Analytics endpoint still failing after retry" -ForegroundColor Red
        }
    }
}

# Test Dashboard endpoint
$dashboardUrl = "https://$functionAppName.azurewebsites.net/api/Dashboard"
Write-Host "   Testing: $dashboardUrl" -ForegroundColor Gray

try {
    $response = Invoke-WebRequest -Uri $dashboardUrl -Method Get -TimeoutSec 30
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Dashboard endpoint is working!" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Dashboard endpoint failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Step 4: Final summary
Write-Host ""
Write-Host "📊 Deployment Verification Summary" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

if ($functionAppName) {
    Write-Host "🔗 Your CoPPA Analytics URLs:" -ForegroundColor Yellow
    Write-Host "   📊 Analytics API: https://$functionAppName.azurewebsites.net/api/GetAnalytics?days=7" -ForegroundColor White
    Write-Host "   🏠 Dashboard: https://$functionAppName.azurewebsites.net/api/Dashboard" -ForegroundColor White
    Write-Host "   📋 Azure Portal: https://portal.azure.com/#resource/subscriptions/{subscription}/resourceGroups/$ResourceGroupName" -ForegroundColor White
}

Write-Host ""
Write-Host "✅ Deploy to Azure verification complete!" -ForegroundColor Green
Write-Host ""
Write-Host "💡 Next Steps:" -ForegroundColor Yellow
Write-Host "   1. Test your analytics API endpoint" -ForegroundColor White
Write-Host "   2. Configure email settings if needed" -ForegroundColor White
Write-Host "   3. Update Cosmos DB connection if using real data" -ForegroundColor White
Write-Host "   4. Set up automated daily reports" -ForegroundColor White

Write-Host ""
Write-Host "📞 Need help? Check the documentation or contact support." -ForegroundColor Cyan
