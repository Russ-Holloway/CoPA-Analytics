# Azure Functions Chatbot Analytics Deployment Script
# For Police Forces - Automated Deployment
param(
    [Parameter(Mandatory=$true)]
    [string]$ForceId,
    
    [Parameter(Mandatory=$false)]
    [string]$Location = "UK South",
    
    [Parameter(Mandatory=$false)]
    [string]$SubscriptionId,
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipLogin
)

# Colors for output
$Red = "`e[31m"
$Green = "`e[32m"
$Yellow = "`e[33m"
$Blue = "`e[34m"
$Reset = "`e[0m"

function Write-ColorText {
    param($Text, $Color)
    Write-Host "$Color$Text$Reset"
}

function Write-Step {
    param($Step, $Description)
    Write-ColorText "[$Step] $Description" $Blue
}

function Write-Success {
    param($Message)
    Write-ColorText "✓ $Message" $Green
}

function Write-Warning {
    param($Message)
    Write-ColorText "⚠ $Message" $Yellow
}

function Write-Error {
    param($Message)
    Write-ColorText "✗ $Message" $Red
}

# Main deployment script
try {
    Write-ColorText "========================================" $Blue
    Write-ColorText "Azure Functions Chatbot Analytics" $Blue
    Write-ColorText "Police Force Deployment Script" $Blue
    Write-ColorText "Force ID: $ForceId" $Blue
    Write-ColorText "Location: $Location" $Blue
    Write-ColorText "========================================" $Blue
    Write-Host ""

    # Step 1: Azure Login
    if (-not $SkipLogin) {
        Write-Step "1" "Connecting to Azure..."
        Connect-AzAccount
        
        if ($SubscriptionId) {
            Set-AzContext -SubscriptionId $SubscriptionId
        }
        
        $context = Get-AzContext
        Write-Success "Connected to subscription: $($context.Subscription.Name)"
    }

    # Step 2: Resource Group
    $resourceGroupName = "rg-$ForceId-chatbot-analytics"
    Write-Step "2" "Creating resource group: $resourceGroupName"
    
    $rg = Get-AzResourceGroup -Name $resourceGroupName -ErrorAction SilentlyContinue
    if (-not $rg) {
        $rg = New-AzResourceGroup -Name $resourceGroupName -Location $Location
        Write-Success "Resource group created successfully"
    } else {
        Write-Warning "Resource group already exists"
    }

    # Step 3: Deploy ARM Template
    Write-Step "3" "Deploying Azure resources using ARM template..."
    
    $templateFile = Join-Path $PSScriptRoot "azuredeploy.json"
    $parametersFile = Join-Path $PSScriptRoot "azuredeploy.parameters.json"
    
    if (-not (Test-Path $templateFile)) {
        throw "ARM template not found: $templateFile"
    }

    # Update parameters for this deployment
    $parameters = @{
        forceIdentifier = $ForceId
        location = $Location
    }

    $deployment = New-AzResourceGroupDeployment `
        -ResourceGroupName $resourceGroupName `
        -TemplateFile $templateFile `
        -TemplateParameterObject $parameters `
        -Mode Incremental

    if ($deployment.ProvisioningState -eq "Succeeded") {
        Write-Success "ARM template deployment completed successfully"
        
        $functionAppName = $deployment.Outputs.functionAppName.Value
        $functionAppUrl = $deployment.Outputs.functionAppUrl.Value
        
        Write-Success "Function App: $functionAppName"
        Write-Success "Function App URL: $functionAppUrl"
    } else {
        throw "ARM template deployment failed: $($deployment.ProvisioningState)"
    }

    # Step 4: Deploy Function Code
    Write-Step "4" "Deploying function code..."
    
    $functionCodePath = Join-Path $PSScriptRoot "function-code"
    if (-not (Test-Path $functionCodePath)) {
        throw "Function code directory not found: $functionCodePath"
    }

    # Check if Azure Functions Core Tools is installed
    $funcVersion = func --version 2>$null
    if (-not $funcVersion) {
        Write-Warning "Azure Functions Core Tools not found. Please install it first:"
        Write-Host "npm install -g azure-functions-core-tools@4 --unsafe-perm true"
        throw "Azure Functions Core Tools required for deployment"
    }

    # Change to function code directory and deploy
    Push-Location $functionCodePath
    try {
        Write-Host "Publishing functions to $functionAppName..."
        func azure functionapp publish $functionAppName --python
        Write-Success "Function code deployed successfully"
    }
    finally {
        Pop-Location
    }

    # Step 5: Test Deployment
    Write-Step "5" "Testing deployment..."
    
    Start-Sleep -Seconds 30  # Wait for functions to initialize
    
    try {
        $testUrl = "$functionAppUrl/api/TestFunction?name=$ForceId"
        $response = Invoke-RestMethod -Uri $testUrl -Method GET
        Write-Success "Test function responded successfully"
        Write-Host "Response: $response"
    }
    catch {
        Write-Warning "Test function may still be initializing. Please test manually in a few minutes."
    }

    # Step 6: Display Results
    Write-ColorText "========================================" $Green
    Write-ColorText "DEPLOYMENT COMPLETED SUCCESSFULLY!" $Green
    Write-ColorText "========================================" $Green
    Write-Host ""
    Write-Host "Resource Group: " -NoNewline
    Write-ColorText $resourceGroupName $Yellow
    Write-Host "Function App: " -NoNewline
    Write-ColorText $functionAppName $Yellow
    Write-Host "Base URL: " -NoNewline
    Write-ColorText $functionAppUrl $Yellow
    Write-Host ""
    Write-ColorText "Available Endpoints:" $Blue
    Write-Host "• Test Function: $functionAppUrl/api/TestFunction"
    Write-Host "• Analytics: $functionAppUrl/api/GetAnalytics"
    Write-Host "• Timer Trigger: Automated (runs daily at 2 AM UTC)"
    Write-Host ""
    Write-ColorText "Next Steps:" $Blue
    Write-Host "1. Configure Cosmos DB connection strings (optional)"
    Write-Host "2. Test all endpoints in Azure portal or Postman"
    Write-Host "3. Set up monitoring and alerts"
    Write-Host "4. Customize analytics logic for your force's needs"
    Write-Host ""

}
catch {
    Write-Error "Deployment failed: $($_.Exception.Message)"
    Write-Host ""
    Write-ColorText "Troubleshooting:" $Yellow
    Write-Host "1. Check that you have sufficient Azure permissions"
    Write-Host "2. Verify that the force ID is unique and valid"
    Write-Host "3. Ensure Azure Functions Core Tools is installed"
    Write-Host "4. Check the Azure portal for detailed error messages"
    exit 1
}

Write-ColorText "Deployment script completed." $Green
