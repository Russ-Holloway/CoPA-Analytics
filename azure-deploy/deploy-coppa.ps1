# CoPPA Analytics Azure Deployment Script
# This script deploys the complete CoPPA Analytics solution to Azure

param(
    [Parameter(Mandatory=$true)]
    [string]$ForceId,
    
    [Parameter(Mandatory=$true)]
    [string]$ResourceGroupName,
    
    [Parameter(Mandatory=$false)]
    [string]$Location = "UK South",
    
    [Parameter(Mandatory=$true)]
    [string]$AdminEmail,
    
    [Parameter(Mandatory=$false)]
    [string]$CosmosDbConnectionString = "",
    
    [Parameter(Mandatory=$false)]
    [string]$CosmosDbDatabase = "chatbot-analytics",
    
    [Parameter(Mandatory=$false)]
    [string]$CosmosDbContainer = "interactions"
)

Write-Host "🚔 Starting CoPPA Analytics Deployment" -ForegroundColor Blue
Write-Host "Force ID: $ForceId" -ForegroundColor Green
Write-Host "Resource Group: $ResourceGroupName" -ForegroundColor Green
Write-Host "Location: $Location" -ForegroundColor Green
Write-Host "Admin Email: $AdminEmail" -ForegroundColor Green

# Check if Azure CLI is installed
if (!(Get-Command az -ErrorAction SilentlyContinue)) {
    Write-Error "Azure CLI is not installed. Please install it first: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
}

# Check if logged into Azure
$account = az account show --query "user.name" -o tsv 2>$null
if (!$account) {
    Write-Host "Please log into Azure..." -ForegroundColor Yellow
    az login
}

Write-Host "Logged in as: $account" -ForegroundColor Green

# Create resource group if it doesn't exist
Write-Host "Creating resource group..." -ForegroundColor Yellow
az group create --name $ResourceGroupName --location $Location

# Deploy ARM template
Write-Host "Deploying Azure resources..." -ForegroundColor Yellow
$deploymentName = "coppa-analytics-$(Get-Date -Format 'yyyyMMdd-HHmmss')"

$deploymentResult = az deployment group create `
    --resource-group $ResourceGroupName `
    --name $deploymentName `
    --template-file "azuredeploy.json" `
    --parameters forceIdentifier=$ForceId `
    --parameters adminEmail=$AdminEmail `
    --parameters cosmosDbConnectionString=$CosmosDbConnectionString `
    --parameters cosmosDbDatabase=$CosmosDbDatabase `
    --parameters cosmosDbContainer=$CosmosDbContainer `
    --output json | ConvertFrom-Json

if ($LASTEXITCODE -ne 0) {
    Write-Error "ARM template deployment failed"
    exit 1
}

$functionAppName = $deploymentResult.properties.outputs.functionAppName.value
$storageAccountName = $deploymentResult.properties.outputs.storageAccountName.value

Write-Host "Resources deployed successfully!" -ForegroundColor Green
Write-Host "Function App: $functionAppName" -ForegroundColor Green

# Package and deploy function code
Write-Host "Packaging function code..." -ForegroundColor Yellow

$tempZip = Join-Path $env:TEMP "coppa-functions.zip"
if (Test-Path $tempZip) { Remove-Item $tempZip -Force }

# Create zip package of function-code directory
Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::CreateFromDirectory((Resolve-Path "function-code").Path, $tempZip)

Write-Host "Deploying function code..." -ForegroundColor Yellow
az functionapp deployment source config-zip `
    --resource-group $ResourceGroupName `
    --name $functionAppName `
    --src $tempZip

if ($LASTEXITCODE -ne 0) {
    Write-Error "Function code deployment failed"
    exit 1
}

# Clean up temp file
Remove-Item $tempZip -Force

# Test deployment
Write-Host "Testing deployment..." -ForegroundColor Yellow
$functionUrl = "https://$functionAppName.azurewebsites.net"

Start-Sleep 30  # Wait for deployment to complete

try {
    $response = Invoke-RestMethod -Uri "$functionUrl/api/GetAnalytics?days=7" -Method GET -TimeoutSec 30
    Write-Host "✅ Analytics API is working!" -ForegroundColor Green
} catch {
    Write-Warning "Analytics API test failed, but deployment may still be successful. Please check manually."
}

try {
    $dashboardResponse = Invoke-WebRequest -Uri "$functionUrl/api/Dashboard" -Method GET -TimeoutSec 30
    if ($dashboardResponse.StatusCode -eq 200) {
        Write-Host "✅ Dashboard is working!" -ForegroundColor Green
    }
} catch {
    Write-Warning "Dashboard test failed, but deployment may still be successful. Please check manually."
}

Write-Host "`n🎉 CoPPA Analytics Deployment Complete!" -ForegroundColor Green
Write-Host "Dashboard URL: $functionUrl/api/Dashboard" -ForegroundColor Cyan
Write-Host "Analytics API: $functionUrl/api/GetAnalytics" -ForegroundColor Cyan
Write-Host "Admin Email: $AdminEmail" -ForegroundColor Cyan

Write-Host "`n📋 Next Steps:" -ForegroundColor Yellow
Write-Host "1. Visit the dashboard URL to view your analytics"
Write-Host "2. Configure automated reports in the Function App settings"
Write-Host "3. Set up custom alert thresholds if needed"
Write-Host "4. Share the dashboard URL with your team"

Write-Host "`n📧 Daily reports will be sent to: $AdminEmail" -ForegroundColor Green
