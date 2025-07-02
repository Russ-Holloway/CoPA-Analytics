# IMMEDIATE FIX - Step by Step Instructions

## Your Current Error: "Did not find functions with language [python]"

This error occurs because the function app is not properly configured for Python 3.11. Here's how to fix it immediately:

## Option 1: Azure Portal Fix (Easiest)

### Step 1: Go to Your Function App
1. Open Azure Portal: https://portal.azure.com
2. Navigate to your Function App: `func-coppa-cop-analytics`
3. Go to **Settings** > **Configuration**

### Step 2: Update Application Settings
Add/Update these settings (click "New application setting" if they don't exist):

```
FUNCTIONS_EXTENSION_VERSION = ~4
FUNCTIONS_WORKER_RUNTIME = python
FUNCTIONS_WORKER_RUNTIME_VERSION = 3.11
WEBSITE_PYTHON_DEFAULT_VERSION = 3.11
PYTHON_ISOLATE_WORKER_DEPENDENCIES = 1
SCM_DO_BUILD_DURING_DEPLOYMENT = true
ENABLE_ORYX_BUILD = true
WEBSITE_NODE_DEFAULT_VERSION = 18.x
```

### Step 3: Force Package Redeployment
Update this setting to force a fresh download:
```
WEBSITE_RUN_FROM_PACKAGE = https://github.com/Russ-Holloway/CoPPA-Analytics/raw/main/chatbot-analytics-azure-deploy/function-app.zip
```

### Step 4: Restart Function App
1. Click **Save** in Configuration
2. Go to **Overview** tab
3. Click **Stop** button
4. Wait 10 seconds
5. Click **Start** button
6. Wait 2-3 minutes for full initialization

### Step 5: Test
Visit: https://func-coppa-cop-analytics.azurewebsites.net/api/GetAnalytics?days=7

---

## Option 2: Azure CLI Fix (Faster)

If you have Azure CLI installed, run these commands:

```bash
# Login to Azure (if not already logged in)
az login

# Update Function App settings
az functionapp config appsettings set \
  --name "func-coppa-cop-analytics" \
  --resource-group "rg-cop-prod-ai-analytics-01" \
  --settings \
    "FUNCTIONS_EXTENSION_VERSION=~4" \
    "FUNCTIONS_WORKER_RUNTIME=python" \
    "FUNCTIONS_WORKER_RUNTIME_VERSION=3.11" \
    "WEBSITE_PYTHON_DEFAULT_VERSION=3.11" \
    "PYTHON_ISOLATE_WORKER_DEPENDENCIES=1" \
    "SCM_DO_BUILD_DURING_DEPLOYMENT=true" \
    "ENABLE_ORYX_BUILD=true" \
    "WEBSITE_NODE_DEFAULT_VERSION=18.x"

# Force package redeployment
az functionapp config appsettings set \
  --name "func-coppa-cop-analytics" \
  --resource-group "rg-cop-prod-ai-analytics-01" \
  --settings "WEBSITE_RUN_FROM_PACKAGE=https://github.com/Russ-Holloway/CoPPA-Analytics/raw/main/chatbot-analytics-azure-deploy/function-app.zip"

# Restart Function App
az functionapp restart --name "func-coppa-cop-analytics" --resource-group "rg-cop-prod-ai-analytics-01"
```

Wait 2-3 minutes, then test: https://func-coppa-cop-analytics.azurewebsites.net/api/GetAnalytics?days=7

---

## Option 3: Azure Cloud Shell (If CLI not available locally)

1. Open Azure Cloud Shell: https://shell.azure.com
2. Run the same commands as Option 2

---

## Expected Result

After the fix, you should see:
- Function App shows "Running" status
- Functions tab shows all 6 functions (GetAnalytics, Dashboard, etc.)
- Analytics endpoint returns JSON data
- No more "language [python]" errors

## What This Fix Does

1. **Updates Python Runtime**: Sets correct Python 3.11 configuration
2. **Enables Oryx Build**: Allows proper dependency installation
3. **Forces Package Reload**: Downloads the fixed function package
4. **Restarts Clean**: Ensures all changes take effect

## If It Still Doesn't Work

1. Check Function App logs in Azure Portal
2. Wait 5-10 minutes (cold start can be slow)
3. Try deleting and redeploying with the "Deploy to Azure" button
4. The Deploy to Azure button now works correctly with all fixes included

---

**The root cause was the extension bundle version and missing build settings. This fix addresses both issues and should resolve your Python runtime error completely.**
