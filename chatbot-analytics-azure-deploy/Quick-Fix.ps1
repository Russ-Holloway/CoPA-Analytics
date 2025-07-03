# SIMPLE Function Deployment Fix
# Use this if functions don't appear after ARM template deployment

param(
    [string]$ResourceGroup,
    [string]$FunctionAppName
)

if (-not $ResourceGroup) {
    $ResourceGroup = Read-Host "Enter your Resource Group name"
}

if (-not $FunctionAppName) {
    $FunctionAppName = Read-Host "Enter your Function App name"
}

Write-Host "=== CoPPA Analytics Function Fix ===" -ForegroundColor Green
Write-Host "Resource Group: $ResourceGroup" -ForegroundColor Yellow
Write-Host "Function App: $FunctionAppName" -ForegroundColor Yellow
Write-Host ""

try {
    # Method 1: Try Azure CLI first (most reliable)
    $azCli = Get-Command az -ErrorAction SilentlyContinue
    
    if ($azCli) {
        Write-Host "Method 1: Using Azure CLI..." -ForegroundColor Cyan
        
        # Simple restart to trigger package loading
        Write-Host "Restarting Function App to trigger package loading..." -ForegroundColor Cyan
        & az functionapp restart --resource-group $ResourceGroup --name $FunctionAppName
        
        Write-Host "✅ Restart completed! Functions should appear in 2-3 minutes." -ForegroundColor Green
    }
    else {
        # Method 2: Try Azure PowerShell
        $azPowerShell = Get-Command Get-AzContext -ErrorAction SilentlyContinue
        
        if ($azPowerShell) {
            Write-Host "Method 2: Using Azure PowerShell..." -ForegroundColor Cyan
            
            Write-Host "Restarting Function App..." -ForegroundColor Cyan
            Restart-AzWebApp -ResourceGroupName $ResourceGroup -Name $FunctionAppName
            
            Write-Host "✅ Restart completed! Functions should appear in 2-3 minutes." -ForegroundColor Green
        }
        else {
            Write-Host "Method 3: Manual steps (Azure CLI/PowerShell not found)..." -ForegroundColor Yellow
            Write-Host ""
            Write-Host "Please follow these manual steps:" -ForegroundColor Cyan
            Write-Host "1. Go to Azure Portal > Your Function App" -ForegroundColor White
            Write-Host "2. Click 'Restart' button in the Overview tab" -ForegroundColor White
            Write-Host "3. Wait 2-3 minutes for functions to appear" -ForegroundColor White
            Write-Host ""
            Write-Host "OR use Kudu deployment:" -ForegroundColor Cyan
            Write-Host "1. Go to Advanced Tools > Go (Kudu)" -ForegroundColor White
            Write-Host "2. Tools > Zip Push Deploy" -ForegroundColor White
            Write-Host "3. Upload: https://github.com/Russ-Holloway/CoPPA-Analytics/raw/main/chatbot-analytics-azure-deploy/function-app.zip" -ForegroundColor White
        }
    }
    
    Write-Host ""
    Write-Host "Test your endpoints after functions appear:" -ForegroundColor Yellow
    Write-Host "https://$FunctionAppName.azurewebsites.net/api/TestFunction" -ForegroundColor Cyan
    Write-Host "https://$FunctionAppName.azurewebsites.net/api/GetAnalytics?days=7" -ForegroundColor Cyan
}
catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Please try the manual restart method in Azure Portal." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== Fix Complete ===" -ForegroundColor Green
