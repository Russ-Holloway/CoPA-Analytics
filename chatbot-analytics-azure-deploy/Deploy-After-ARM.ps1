# INSTANT FUNCTION DEPLOYMENT SCRIPT
# Run this immediately after "Deploy to Azure" completes

param(
    [Parameter(Mandatory=$false)]
    [string]$ResourceGroupName,
    
    [Parameter(Mandatory=$false)]
    [string]$FunctionAppName
)

Write-Host "🚀 CoPPA Analytics - Instant Function Deployment" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green
Write-Host ""

# Auto-detect if parameters not provided
if (-not $ResourceGroupName -or -not $FunctionAppName) {
    Write-Host "🔍 Auto-detecting Function App..." -ForegroundColor Yellow
    
    try {
        # Try to find CoPPA function apps in subscription
        $functionApps = az functionapp list --query "[?contains(name, 'coppa') || contains(name, 'cop')].{name:name, resourceGroup:resourceGroup}" -o json | ConvertFrom-Json
        
        if ($functionApps.Count -eq 1) {
            $ResourceGroupName = $functionApps[0].resourceGroup
            $FunctionAppName = $functionApps[0].name
            Write-Host "✅ Found Function App: $FunctionAppName in $ResourceGroupName" -ForegroundColor Green
        }
        elseif ($functionApps.Count -gt 1) {
            Write-Host "Multiple Function Apps found:" -ForegroundColor Yellow
            for ($i = 0; $i -lt $functionApps.Count; $i++) {
                Write-Host "  $($i+1). $($functionApps[$i].name) in $($functionApps[$i].resourceGroup)" -ForegroundColor White
            }
            $choice = Read-Host "Enter number (1-$($functionApps.Count))"
            $selected = $functionApps[$choice-1]
            $ResourceGroupName = $selected.resourceGroup
            $FunctionAppName = $selected.name
        }
        else {
            throw "No CoPPA Function Apps found"
        }
    }
    catch {
        Write-Host "❌ Could not auto-detect. Please provide manually:" -ForegroundColor Red
        $ResourceGroupName = Read-Host "Enter Resource Group name"
        $FunctionAppName = Read-Host "Enter Function App name"
    }
}

Write-Host ""
Write-Host "🎯 Target Function App:" -ForegroundColor Cyan
Write-Host "   Resource Group: $ResourceGroupName" -ForegroundColor White
Write-Host "   Function App: $FunctionAppName" -ForegroundColor White
Write-Host ""

# Method 1: Try Azure CLI ZIP deployment (most reliable)
Write-Host "🚀 Method 1: Azure CLI ZIP Deployment" -ForegroundColor Yellow
try {
    $zipUrl = "https://github.com/Russ-Holloway/CoPPA-Analytics/raw/main/chatbot-analytics-azure-deploy/function-app.zip"
    
    Write-Host "   📦 Deploying function package..." -ForegroundColor Cyan
    az functionapp deployment source config-zip --resource-group $ResourceGroupName --name $FunctionAppName --src $zipUrl
    
    Write-Host "   🔄 Restarting Function App..." -ForegroundColor Cyan
    az functionapp restart --resource-group $ResourceGroupName --name $FunctionAppName
    
    Write-Host "   ⏳ Waiting for functions to load (30 seconds)..." -ForegroundColor Cyan
    Start-Sleep -Seconds 30
    
    # Check if functions are loaded
    $functions = az functionapp function list --resource-group $ResourceGroupName --name $FunctionAppName --query "[].name" -o json | ConvertFrom-Json
    
    if ($functions.Count -ge 6) {
        Write-Host "✅ SUCCESS! All $($functions.Count) functions deployed via Azure CLI" -ForegroundColor Green
        Write-Host ""
        Write-Host "📋 Deployed functions:" -ForegroundColor Yellow
        $functions | ForEach-Object { Write-Host "   ✅ $_" -ForegroundColor Green }
        
        Write-Host ""
        Write-Host "🧪 Test your endpoints:" -ForegroundColor Yellow
        Write-Host "   https://$FunctionAppName.azurewebsites.net/api/TestFunction" -ForegroundColor Cyan
        Write-Host "   https://$FunctionAppName.azurewebsites.net/api/GetAnalytics?days=7" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "🎉 DEPLOYMENT COMPLETE! Your Function App is ready to use." -ForegroundColor Green
        return
    }
    else {
        Write-Host "⚠️ Azure CLI deployment completed but functions not detected yet." -ForegroundColor Yellow
        Write-Host "   This may be normal. Trying alternative method..." -ForegroundColor Gray
    }
}
catch {
    Write-Host "❌ Azure CLI method failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "   Trying alternative method..." -ForegroundColor Gray
}

# Method 2: Manual instructions if CLI fails
Write-Host ""
Write-Host "🔧 Method 2: Manual Kudu Deployment" -ForegroundColor Yellow
Write-Host "If the Azure CLI method didn't work, follow these steps:" -ForegroundColor White
Write-Host ""
Write-Host "1. Open your Function App in Azure Portal:" -ForegroundColor Cyan
Write-Host "   https://portal.azure.com/#resource/subscriptions/[subscription]/resourceGroups/$ResourceGroupName/providers/Microsoft.Web/sites/$FunctionAppName" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Go to Advanced Tools > Go (Kudu)" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. In Kudu, go to Tools > Zip Push Deploy" -ForegroundColor Cyan
Write-Host ""
Write-Host "4. Drag and drop this ZIP file:" -ForegroundColor Cyan
Write-Host "   https://github.com/Russ-Holloway/CoPPA-Analytics/raw/main/chatbot-analytics-azure-deploy/function-app.zip" -ForegroundColor Gray
Write-Host ""
Write-Host "5. Wait 2-3 minutes for deployment to complete" -ForegroundColor Cyan
Write-Host ""
Write-Host "6. Check Functions tab for all 6 functions" -ForegroundColor Cyan

Write-Host ""
Write-Host "💡 Tips:" -ForegroundColor Yellow
Write-Host "   • Functions may take 2-5 minutes to appear after deployment" -ForegroundColor Gray
Write-Host "   • Refresh your browser if functions don't show immediately" -ForegroundColor Gray
Write-Host "   • Check Log Stream for any deployment errors" -ForegroundColor Gray
Write-Host ""
Write-Host "📞 Support: If you still have issues, the ARM template creates a working" -ForegroundColor Yellow
Write-Host "   Function App - it just needs the function code deployed manually." -ForegroundColor Gray
