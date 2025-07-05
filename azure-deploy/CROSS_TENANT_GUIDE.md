# Cross-Tenant Deployment Guide

## Problem
When the Azure Function App is deployed in a different Azure tenant/organization than your local development environment, you cannot use Azure CLI commands directly from your local machine.

## Solution
Use Azure Cloud Shell in the target tenant to execute the fix commands.

## Steps

### 1. Identify the Cross-Tenant Scenario
- You click "Deploy to Azure" and it works
- Function App is created successfully
- But when you try to run fix commands locally, you get authentication errors
- Or Azure CLI shows a different subscription/tenant than expected

### 2. Use Cloud Shell
1. Open [Azure Cloud Shell](https://shell.azure.com)
2. **Make sure you're logged into the correct tenant/organization**
3. Run: `az account show` to verify your context
4. If wrong tenant, log out and log back in with the correct account

### 3. Run the Fix Commands
Use the `cross-tenant-fix.ps1` script which outputs all the commands you need:

```powershell
.\cross-tenant-fix.ps1 -SubscriptionId "your-sub-id" -ResourceGroupName "your-rg" -FunctionAppName "your-app-name"
```

This will output commands like:
```bash
az account set --subscription your-sub-id
az functionapp stop --name your-app-name --resource-group your-rg
# ... more commands
```

### 4. Copy and Paste
Copy all the commands and paste them into Azure Cloud Shell in one go.

### 5. Wait and Test
- Wait 3-5 minutes for the Function App to initialize
- Test the endpoint: `https://your-app-name.azurewebsites.net/api/GetAnalytics?days=7`
- Check the Azure Portal to see if all 7 functions are loaded

## Why This Happens
- Azure resources can be in different tenants/organizations
- Your local Azure CLI is authenticated to your "home" tenant
- The Function App might be in a partner/customer/different organization's tenant
- Azure Cloud Shell automatically uses the correct tenant context when you log in

## Alternative
If the cross-tenant fix doesn't work, use the "Deploy to Azure" button to create a fresh Function App. The ARM template is now optimized for one-click deployment with all functions.
