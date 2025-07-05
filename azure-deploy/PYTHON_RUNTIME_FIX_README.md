# CoPPA Analytics - Python Runtime Fix

## Problem
You're experiencing a "503 Service Unavailable" error with the message "Function host is not running" on your CoPPA Analytics Azure Function App.

## Root Cause
This issue is typically caused by:
1. Incorrect Python runtime version configuration
2. Incompatible extension bundle version for Python 3.11
3. Missing build configuration settings
4. Package deployment issues

## Solution

### Option 1: Quick Fix (Recommended)
Run the automated fix script:

```powershell
# From the chatbot-analytics-azure-deploy folder
.\complete-python-fix.ps1
```

Or with specific parameters:
```powershell
.\complete-python-fix.ps1 -ResourceGroupName "your-rg-name" -FunctionAppName "your-function-app-name"
```

### Option 2: Manual Fix via Azure Portal

1. **Go to your Function App in Azure Portal**
2. **Navigate to Configuration > Application Settings**
3. **Update these settings:**

```json
{
  "FUNCTIONS_EXTENSION_VERSION": "~4",
  "FUNCTIONS_WORKER_RUNTIME": "python",
  "FUNCTIONS_WORKER_RUNTIME_VERSION": "3.11",
  "WEBSITE_PYTHON_DEFAULT_VERSION": "3.11",
  "PYTHON_ISOLATE_WORKER_DEPENDENCIES": "1",
  "SCM_DO_BUILD_DURING_DEPLOYMENT": "true",
  "ENABLE_ORYX_BUILD": "true",
  "WEBSITE_NODE_DEFAULT_VERSION": "18.x"
}
```

4. **Save the configuration**
5. **Restart the Function App**
6. **Wait 2-3 minutes for initialization**

### Option 3: Redeploy with Fixed Template

1. **Use the updated ARM template** (`azuredeploy.json`) which now includes:
   - Correct extension bundle version `[4.0.0, 5.0.0)`
   - Proper Python 3.11 settings
   - Required build configuration

2. **Deploy using:**
   ```powershell
   .\deploy-enhanced.ps1 -ForceId "YOUR_FORCE_ID"
   ```

## Key Changes Made

### 1. Updated host.json
```json
{
  "extensionBundle": {
    "id": "Microsoft.Azure.Functions.ExtensionBundle",
    "version": "[4.0.0, 5.0.0)"  // Updated from [3.3.0, 4.0.0)
  }
}
```

### 2. Updated requirements.txt
```
azure-functions>=1.19.0     // Updated from 1.18.0
requests>=2.31.0           // Updated from 2.28.1
email-validator>=2.0.0     // Added for email functionality
```

### 3. Added Critical Function App Settings
- `SCM_DO_BUILD_DURING_DEPLOYMENT`: `true`
- `ENABLE_ORYX_BUILD`: `true`
- `WEBSITE_CONTENTAZUREFILECONNECTIONSTRING`: Required for consumption plan
- `WEBSITE_CONTENTSHARE`: Required for consumption plan

## Verification Steps

1. **Check Function App Status:**
   - Navigate to your Function App in Azure Portal
   - Status should show "Running"

2. **Test Analytics Endpoint:**
   ```
   https://your-function-app.azurewebsites.net/api/GetAnalytics?days=7
   ```

3. **Check Logs:**
   - In Azure Portal: Function App > Log stream
   - Look for successful initialization messages

4. **Verify Function List:**
   - In Azure Portal: Function App > Functions
   - You should see: GetAnalytics, Dashboard, GetQuestions, etc.

## Expected Response
When working correctly, the analytics endpoint should return:

```json
{
  "metadata": {
    "force_id": "COP",
    "data_source": "cosmos_db",
    "period": "2025-06-25 to 2025-07-02",
    "total_conversations": 150
  },
  "summary": {
    "total_interactions": 150,
    "unique_users": 89,
    "avg_conversation_length": 4.2
  },
  // ... more analytics data
}
```

## Troubleshooting

### If the fix doesn't work immediately:

1. **Wait longer** - Function Apps can take 5-10 minutes to fully initialize
2. **Check Application Insights** - Look for error messages
3. **Verify Cosmos DB connection** - Ensure your connection string is correct
4. **Try cold start** - Stop and start the Function App

### Common Error Messages:

- **"Function host is not running"** → Apply this fix
- **"No functions found"** → Package deployment issue
- **"Python worker failed to start"** → Python version mismatch
- **"Module not found"** → Dependencies not installed properly

### Still having issues?

1. **Check the Function App logs** in Azure Portal
2. **Verify your Cosmos DB settings** are correct
3. **Try redeploying** with the updated ARM template
4. **Contact support** with the specific error messages from logs

## Files Updated
- ✅ `host.json` - Updated extension bundle version
- ✅ `requirements.txt` - Updated package versions
- ✅ `azuredeploy.json` - Added missing configuration settings
- ✅ Created fix scripts for automation

Your CoPPA Analytics should now work correctly with Python 3.11 on Azure Functions v4! 🎉
