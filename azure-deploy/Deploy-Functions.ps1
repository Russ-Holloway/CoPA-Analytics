# Post-Deployment Function Loader Script

param(
    [Parameter(Mandatory=$true)]
    [string]$ResourceGroupName,
    
    [Parameter(Mandatory=$true)]
    [string]$FunctionAppName
)

Write-Host "=== CoPPA Analytics Post-Deployment Script ===" -ForegroundColor Green
Write-Host "Resource Group: $ResourceGroupName" -ForegroundColor Yellow
Write-Host "Function App: $FunctionAppName" -ForegroundColor Yellow
Write-Host ""

# Function to check if functions are loaded
function Test-FunctionsLoaded {
    param($appName, $rgName)
    
    try {
        $functions = Get-AzWebAppFunction -ResourceGroupName $rgName -AppName $appName -ErrorAction SilentlyContinue
        return $functions.Count
    }
    catch {
        return 0
    }
}

# Check current function count
$initialCount = Test-FunctionsLoaded -appName $FunctionAppName -rgName $ResourceGroupName
Write-Host "Initial function count: $initialCount" -ForegroundColor Cyan

if ($initialCount -ge 6) {
    Write-Host "✅ All functions already loaded! Deployment successful." -ForegroundColor Green
    exit 0
}

# If functions not loaded, try to trigger deployment
Write-Host "⚠️  Functions not detected. Triggering manual deployment..." -ForegroundColor Yellow

try {
    # Method 1: Restart the Function App
    Write-Host "Step 1: Restarting Function App..." -ForegroundColor Cyan
    Restart-AzWebApp -ResourceGroupName $ResourceGroupName -Name $FunctionAppName
    
    # Wait for restart
    Start-Sleep -Seconds 60
    
    # Check functions again
    $count = Test-FunctionsLoaded -appName $FunctionAppName -rgName $ResourceGroupName
    Write-Host "Function count after restart: $count" -ForegroundColor Cyan
    
    if ($count -ge 6) {
        Write-Host "✅ Functions loaded successfully after restart!" -ForegroundColor Green
        exit 0
    }
    
    # Method 2: If still not loaded, deploy ZIP manually via API
    Write-Host "Step 2: Deploying ZIP package via REST API..." -ForegroundColor Cyan
    
    # Get publishing credentials
    $creds = Get-AzWebAppPublishingProfile -ResourceGroupName $ResourceGroupName -Name $FunctionAppName -OutputFile $null -Format WebDeploy
    $username = $creds.userName
    $password = $creds.userPWD
    
    # Encode credentials
    $base64AuthInfo = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes(("{0}:{1}" -f $username, $password)))
    
    # Deploy ZIP
    $zipUrl = "https://github.com/Russ-Holloway/CoPPA-Analytics/raw/main/chatbot-analytics-azure-deploy/function-app.zip"
    $kuduUrl = "https://$FunctionAppName.scm.azurewebsites.net/api/zipdeploy"
    
    $headers = @{
        Authorization = "Basic $base64AuthInfo"
        "Content-Type" = "application/octet-stream"
    }
    
    # Download and deploy ZIP
    $tempFile = New-TemporaryFile
    Invoke-WebRequest -Uri $zipUrl -OutFile $tempFile.FullName
    
    Write-Host "Uploading function package..." -ForegroundColor Cyan
    Invoke-RestMethod -Uri $kuduUrl -Method POST -Headers $headers -InFile $tempFile.FullName
    
    # Clean up temp file
    Remove-Item $tempFile.FullName
    
    # Wait for deployment
    Start-Sleep -Seconds 120
    
    # Final check
    $finalCount = Test-FunctionsLoaded -appName $FunctionAppName -rgName $ResourceGroupName
    Write-Host "Final function count: $finalCount" -ForegroundColor Cyan
    
    if ($finalCount -ge 6) {
        Write-Host "✅ All functions loaded successfully!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Available functions:" -ForegroundColor Yellow
        $functions = Get-AzWebAppFunction -ResourceGroupName $ResourceGroupName -AppName $FunctionAppName
        $functions | ForEach-Object { Write-Host "  - $($_.Name)" -ForegroundColor White }
        Write-Host ""
        Write-Host "Test your endpoints:" -ForegroundColor Yellow
        Write-Host "  https://$FunctionAppName.azurewebsites.net/api/TestFunction" -ForegroundColor Cyan
        Write-Host "  https://$FunctionAppName.azurewebsites.net/api/GetAnalytics?days=7" -ForegroundColor Cyan
    }
    else {
        Write-Host "❌ Functions still not loaded. Manual intervention required." -ForegroundColor Red
        Write-Host "Please check the Function App logs and Kudu console." -ForegroundColor Yellow
    }
}
catch {
    Write-Host "❌ Error during deployment: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== Post-Deployment Script Complete ===" -ForegroundColor Green
