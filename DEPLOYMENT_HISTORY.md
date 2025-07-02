# Chatbot Analytics Azure Deployment - Complete Guide

## Project Overview
This project provides a complete Azure Functions solution for chatbot analytics for police forces, with automated deployment capabilities and a "Deploy to Azure" button for easy replication across different police force tenants.

## What We've Accomplished

### 1. Manual Azure Deployment (Successfully Tested)
We successfully deployed and tested Azure Functions manually with the following components:
- **Resource Group**: Created and configured
- **Storage Account**: Set up for Azure Functions
- **Function App**: Python-based with analytics capabilities
- **Functions Deployed**:
  - `TestFunction`: HTTP trigger for testing connectivity
  - `GetAnalytics`: HTTP trigger for retrieving analytics data
  - `TimerTrigger`: Scheduled function for automated processing

### 2. Key Technical Decisions Made
- **Programming Model**: Switched from Python v2 to v1 model for better compatibility
- **Runtime**: Python 3.9 on Azure Functions
- **Architecture**: Serverless functions with HTTP and timer triggers
- **Database**: Cosmos DB integration for analytics storage

### 3. Deployment Methods Created
1. **Manual PowerShell Deployment** (tested and working)
2. **ARM Template Deployment** (one-click "Deploy to Azure")
3. **Automated CI/CD Pipeline** (GitHub Actions ready)

## Next Steps for Full Automation

### Immediate Tasks:
1. Recreate the `chatbot-analytics-azure-deploy` folder structure
2. Add ARM templates for one-click deployment
3. Include all function code with proper structure
4. Create PowerShell automation scripts
5. Set up "Deploy to Azure" button

### File Structure Needed:
```
chatbot-analytics-azure-deploy/
├── README.md (with Deploy to Azure button)
├── azuredeploy.json (ARM template)
├── azuredeploy.parameters.json (parameters)
├── deploy.ps1 (PowerShell script)
├── function-code/
│   ├── requirements.txt
│   ├── host.json
│   ├── TestFunction/
│   │   ├── __init__.py
│   │   └── function.json
│   ├── GetAnalytics/
│   │   ├── __init__.py
│   │   └── function.json
│   └── TimerTrigger/
│       ├── __init__.py
│       └── function.json
└── .github/
    └── workflows/
        └── deploy.yml
```

## Previous Deployment Commands (PowerShell)

### Resource Creation:
```powershell
# Login to Azure
Connect-AzAccount

# Create Resource Group
New-AzResourceGroup -Name "rg-chatbot-analytics" -Location "UK South"

# Create Storage Account
New-AzStorageAccount -ResourceGroupName "rg-chatbot-analytics" -Name "stchatbotanalytics" -Location "UK South" -SkuName "Standard_LRS"

# Create Function App
New-AzFunctionApp -ResourceGroupName "rg-chatbot-analytics" -Name "func-chatbot-analytics" -StorageAccountName "stchatbotanalytics" -Runtime "Python" -RuntimeVersion "3.9" -Location "UK South"
```

### Function Deployment:
```powershell
# Deploy function code
func azure functionapp publish func-chatbot-analytics --python
```

## Testing Endpoints (Confirmed Working)
- **Test Function**: `https://func-chatbot-analytics.azurewebsites.net/api/TestFunction`
- **Analytics**: `https://func-chatbot-analytics.azurewebsites.net/api/GetAnalytics`

## Environment Variables Required
- `COSMOS_DB_CONNECTION_STRING`: Connection to Cosmos DB
- `COSMOS_DB_DATABASE`: Database name
- `COSMOS_DB_CONTAINER`: Container name for analytics data

## Lessons Learned
1. Python v1 programming model is more stable for Azure Functions
2. Always test endpoints after deployment
3. Storage account names must be globally unique
4. Function app names must be globally unique
5. UK South region works well for police force deployments

## Police Force Adaptation Notes
- Resource names should include force identifier (e.g., "btp", "met", "gmp")
- Cosmos DB can be shared across forces or separate per force
- ARM templates make it easy to replicate across different tenants
- Environment variables allow customization per deployment

## Support and Troubleshooting
- Check function logs in Azure portal
- Verify storage account connection
- Ensure Python version compatibility
- Test endpoints individually before full deployment
