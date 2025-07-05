# One-Click Deployment Test Guide

## What We Fixed
The ARM template now includes enhanced configuration to ensure automatic function deployment when using the "Deploy to Azure" button.

## Enhanced Settings Added
1. **`WEBSITE_RUN_FROM_PACKAGE_BLOB`** - Clears any blob-based package settings
2. **`WEBSITE_ENABLE_SYNC_UPDATE_SITE`** - Enables proper site synchronization
3. **`WEBSITE_ZIP_DEPLOYMENT_USE_RUN_FROM_PACKAGE`** - Forces ZIP package deployment
4. **`WEBSITE_DEPLOYMENT_RESTART_BEHAVIOR`** - Controls restart timing for function loading

## Test Process

### Step 1: Deploy to New Resource Group
1. Use the **"Deploy to Azure"** button
2. Create a **new resource group** (e.g., `rg-coppa-test-v2`)
3. Fill in required parameters:
   - **Force Prefix**: Your police force code
   - **Admin Email**: Your email address
4. Click **"Review + create"** → **"Create"**

### Step 2: Monitor Deployment (5-8 minutes)
- Watch deployment progress in Azure Portal
- ARM template creates infrastructure AND deploys functions automatically
- No manual intervention required

### Step 3: Verify Function Loading (2-5 minutes after deployment)
1. **Go to Function App** → **Functions** tab
2. **Wait 2-5 minutes** for function discovery
3. **Verify all 6 functions appear**:
   - ✅ GetAnalytics
   - ✅ Dashboard
   - ✅ GetQuestions
   - ✅ SeedData
   - ✅ TestFunction
   - ✅ TimerTrigger

### Step 4: Test Function Endpoints
Once functions appear, test these URLs:
```
https://[your-function-app-name].azurewebsites.net/api/TestFunction
https://[your-function-app-name].azurewebsites.net/api/GetAnalytics?days=7
https://[your-function-app-name].azurewebsites.net/api/Dashboard
```

## Expected Results
✅ **Complete one-click deployment** - No manual Kudu steps needed  
✅ **All functions auto-detected** - No waiting for manual deployment  
✅ **Immediate usability** - Functions ready to use after deployment  
✅ **Proper Python 3.11 runtime** - Linux Function App with correct configuration  

## If Functions Don't Appear
If functions still don't load automatically after 10 minutes:

1. **Check Application Insights logs**
2. **Verify package URL accessibility**: 
   - https://github.com/Russ-Holloway/CoPPA-Analytics/raw/main/chatbot-analytics-azure-deploy/function-app.zip
3. **Manual restart** (should not be needed):
   - Go to Function App → **Overview** → **Restart**
   - Wait 3-5 minutes for function discovery

## Success Criteria
- **Zero manual intervention** required after "Deploy to Azure" click
- **Functions automatically loaded** within 8 minutes of deployment completion
- **All endpoints functional** immediately after deployment

---
**Note**: This eliminates the previous manual Kudu deployment requirement and provides a true enterprise-ready one-click solution.
