# Enhanced Azure Functions Chatbot Analytics Deployment Script
# For Police Forces - Automated Deployment with Cosmos DB
param(
    [Parameter(Mandatory=$true)]
    [string]$ForceId,
    
    [Parameter(Mandatory=$false)]
    [string]$Location = "UK South",
    
    [Parameter(Mandatory=$false)]
    [string]$Environment = "dev",
    
    [Parameter(Mandatory=$false)]
    [string]$SubscriptionId,
    
    [Parameter(Mandatory=$false)]
    [switch]$SeedData = $false,
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipLogin
)

# Set error action preference
$ErrorActionPreference = "Stop"

# Colors for output
$Red = "`e[31m"
$Green = "`e[32m"
$Yellow = "`e[33m"
$Blue = "`e[34m"
$Cyan = "`e[36m"
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
    Write-ColorText "✅ $Message" $Green
}

function Write-Warning {
    param($Message)
    Write-ColorText "⚠️  $Message" $Yellow
}

function Write-Error {
    param($Message)
    Write-ColorText "❌ $Message" $Red
}

function Write-Info {
    param($Message)
    Write-ColorText "ℹ️  $Message" $Cyan
}

# Main deployment script
try {
    Write-ColorText "========================================" $Blue
    Write-ColorText "🚀 Azure Functions Chatbot Analytics" $Blue
    Write-ColorText "Police Force Enhanced Deployment" $Blue
    Write-ColorText "Force ID: $ForceId" $Blue
    Write-ColorText "Location: $Location" $Blue
    Write-ColorText "Environment: $Environment" $Blue
    Write-ColorText "========================================" $Blue
    Write-Host ""

    # Variables
    $ResourceGroupName = "rg-$ForceId-chatbot-$Environment"
    $DeploymentName = "chatbot-analytics-$(Get-Date -Format 'yyyyMMdd-HHmmss')"

    # Step 1: Azure Login
    if (-not $SkipLogin) {
        Write-Step "1" "Connecting to Azure..."
        $context = Get-AzContext
        if (-not $context) {
            Connect-AzAccount
        }
        
        if ($SubscriptionId) {
            Set-AzContext -SubscriptionId $SubscriptionId
            Write-Info "Subscription set to: $SubscriptionId"
        }
        
        $currentContext = Get-AzContext
        Write-Success "Connected to subscription: $($currentContext.Subscription.Name)"
    }

    # Step 2: Resource Group
    Write-Step "2" "Creating resource group: $ResourceGroupName"
    
    $rg = Get-AzResourceGroup -Name $ResourceGroupName -ErrorAction SilentlyContinue
    if (-not $rg) {
        $rg = New-AzResourceGroup -Name $ResourceGroupName -Location $Location
        Write-Success "Resource group created successfully"
    } else {
        Write-Warning "Resource group already exists"
    }

    # Step 3: Deploy ARM Template
    Write-Step "3" "Deploying Azure resources (including Cosmos DB)..."
    
    $templateFile = Join-Path $PSScriptRoot "azuredeploy.json"
    $parametersFile = Join-Path $PSScriptRoot "azuredeploy.parameters.json"
    
    if (-not (Test-Path $templateFile)) {
        throw "ARM template not found: $templateFile"
    }

    # Deploy with parameters
    $deploymentParams = @{
        ResourceGroupName = $ResourceGroupName
        TemplateFile = $templateFile
        TemplateParameterFile = $parametersFile
        Name = $DeploymentName
        forceIdentifier = $ForceId
        location = $Location
        Verbose = $true
    }
    
    $deployment = New-AzResourceGroupDeployment @deploymentParams
    
    if ($deployment.ProvisioningState -eq "Succeeded") {
        Write-Success "Azure resources deployed successfully"
        
        # Get deployment outputs
        $functionAppName = $deployment.Outputs.functionAppName.Value
        $functionAppUrl = $deployment.Outputs.functionAppUrl.Value
        $cosmosDbEndpoint = if ($deployment.Outputs.cosmosDbEndpoint) { $deployment.Outputs.cosmosDbEndpoint.Value } else { "Not available" }
        
        Write-Info "Function App: $functionAppName"
        Write-Info "URL: $functionAppUrl"
        Write-Info "Cosmos DB: $cosmosDbEndpoint"
        
    } else {
        throw "Deployment failed with state: $($deployment.ProvisioningState)"
    }

    # Step 4: Deploy Function Code
    Write-Step "4" "Deploying function code..."
    
    # Check if Azure Functions Core Tools is available
    $funcCoreTools = Get-Command "func" -ErrorAction SilentlyContinue
    if (-not $funcCoreTools) {
        Write-Error "Azure Functions Core Tools not found"
        Write-Info "Install with: npm install -g azure-functions-core-tools@4 --unsafe-perm true"
        throw "Azure Functions Core Tools required"
    }
    
    # Change to function-code directory
    $functionCodePath = Join-Path $PSScriptRoot "function-code"
    if (-not (Test-Path $functionCodePath)) {
        throw "Function code directory not found: $functionCodePath"
    }
    
    Push-Location $functionCodePath
    
    try {
        Write-Info "Publishing functions to $functionAppName..."
        & func azure functionapp publish $functionAppName --python --build remote
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Function code deployed successfully"
        } else {
            throw "Function deployment failed"
        }
    }
    finally {
        Pop-Location
    }

    # Step 5: Verify Deployment
    Write-Step "5" "Verifying deployment..."
    
    # Wait a moment for functions to become available
    Write-Info "Waiting for functions to initialize..."
    Start-Sleep -Seconds 30
    
    # Test the health endpoint
    $testUrl = "$functionAppUrl/api/TestFunction"
    Write-Info "Testing endpoint: $testUrl"
    
    try {
        $response = Invoke-RestMethod -Uri $testUrl -Method Get -TimeoutSec 30
        Write-Success "Test endpoint responding successfully"
        Write-Info "Response: $($response | ConvertTo-Json -Compress)"
    }
    catch {
        Write-Warning "Test endpoint not yet available (this is normal immediately after deployment)"
        Write-Info "You can test manually: $testUrl"
    }

    # Step 6: Seed Cosmos DB (if requested)
    if ($SeedData) {
        Write-Step "6" "Seeding Cosmos DB with sample data..."
        
        # Wait a bit more for function app to be fully ready
        Write-Info "Waiting for function app to be fully ready..."
        Start-Sleep -Seconds 30
        
        $seedUrl = "$functionAppUrl/api/SeedData"
        Write-Info "Calling seed endpoint: $seedUrl"
        
        try {
            $seedResponse = Invoke-RestMethod -Uri $seedUrl -Method Post -TimeoutSec 120
            Write-Success "Sample data seeded successfully"
            Write-Info "Items inserted: $($seedResponse.items_inserted)"
            Write-Info "Database: $($seedResponse.database)"
            Write-Info "Container: $($seedResponse.container)"
        }
        catch {
            Write-Warning "Failed to seed data automatically"
            Write-Info "You can try manually: POST $seedUrl"
            Write-Info "Error: $($_.Exception.Message)"
        }
    }

    # Step 7: Display Final Information
    Write-ColorText "`n🎉 Deployment completed successfully!" $Green
    Write-ColorText "`n📋 Resources Created:" $Cyan
    Write-Host "  Resource Group: $ResourceGroupName"
    Write-Host "  Function App: $functionAppName"
    Write-Host "  Cosmos DB: $cosmosDbEndpoint"
    
    Write-ColorText "`n🔗 Function Endpoints:" $Cyan
    Write-Host "  Test: $functionAppUrl/api/TestFunction"
    Write-Host "  Analytics: $functionAppUrl/api/GetAnalytics"
    Write-Host "  Seed Data: $functionAppUrl/api/SeedData (POST)"
    Write-Host "  Timer: Runs daily at 2 AM UTC"
    
    Write-ColorText "`n📊 Sample Queries:" $Cyan
    Write-Host "  Get all analytics: GET $functionAppUrl/api/GetAnalytics"
    Write-Host "  Filter by category: GET $functionAppUrl/api/GetAnalytics?category=crime_reporting"
    Write-Host "  Date range: GET $functionAppUrl/api/GetAnalytics?startDate=2025-06-01&endDate=2025-06-30"
    
    Write-ColorText "`n🔗 Next Steps:" $Cyan
    Write-Host "  1. Test the endpoints above"
    Write-Host "  2. Monitor in Azure Portal: https://portal.azure.com"
    Write-Host "  3. View logs in Application Insights"
    
    if (-not $SeedData) {
        Write-Host "  4. Optionally seed sample data:"
        Write-Host "     Invoke-RestMethod -Uri '$functionAppUrl/api/SeedData' -Method Post"
    }
    
    Write-ColorText "`n📚 Documentation:" $Cyan
    Write-Host "  See README.md for detailed usage instructions"
    Write-Host "  ARM template: azuredeploy.json"
    Write-Host "  Function code: function-code/"

}
catch {
    Write-Error "Deployment failed: $($_.Exception.Message)"
    Write-Host "Check the error details above and try again." -ForegroundColor Yellow
    
    # Display troubleshooting tips
    Write-ColorText "`n🔧 Troubleshooting Tips:" $Yellow
    Write-Host "  1. Ensure you have Azure PowerShell module installed"
    Write-Host "  2. Verify Azure Functions Core Tools are installed"
    Write-Host "  3. Check Azure subscription permissions"
    Write-Host "  4. Verify resource group location is valid"
    
    exit 1
}

Write-ColorText "`n✨ Deployment script completed!" $Green
