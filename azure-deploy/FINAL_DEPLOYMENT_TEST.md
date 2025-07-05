# 🚀 CoPPA Analytics - Final Deployment Test Guide

## ✅ ARM Template Configuration Status

**CONFIRMED READY:** The ARM template has been updated with all critical fixes:

### Linux Configuration ✅
- **Function App Kind**: `functionapp,linux` 
- **App Service Plan Kind**: `linux`
- **Reserved Property**: `true` (required for Linux)
- **Linux Framework**: `Python|3.11`

### Python Runtime Settings ✅
- **Extension Version**: `~4` (Functions v4)
- **Worker Runtime**: `python`
- **Worker Runtime Version**: `3.11`
- **Python Default Version**: `3.11`
- **Worker Dependencies**: `1` (isolation enabled)
- **Build Settings**: Oryx build enabled

### Package Deployment ✅
- **Package URL**: `function-app.zip` (fixed and ready)
- **Host.json**: Extension bundle `[4.0.0, 5.0.0)` for Python 3.11
- **Requirements.txt**: Compatible versions for Azure Functions v4

---

## 🧪 Step 1: Deploy Using Deploy to Azure Button

**USE THIS LINK TO TEST:** 
https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FRuss-Holloway%2FCoPPA-Analytics%2Fmain%2Fchatbot-analytics-azure-deploy%2Fazuredeploy.json

### Fill in the form:
- **Force Prefix**: Use a NEW prefix (e.g., `TEST`, `DEV`, `QA`)
- **Admin Email**: Your email address
- **Cosmos DB settings**: Leave blank for demo data
- **Resource Group**: Create new: `rg-{prefix}-coppa-test`
- **Region**: UK South (recommended)

### Expected Deployment Time: 8-12 minutes

---

## 🔍 Step 2: Verify Deployment Success

### Check 1: Function App Platform ✅
**Azure Portal → Function App → Overview**
- **Platform**: Should show `Linux`
- **Runtime Stack**: Should show `Python 3.11`
- **Status**: Should be `Running`

### Check 2: Function Detection ✅
**Azure Portal → Function App → Functions**
- Should see ALL functions listed:
  - ✅ `GetAnalytics`
  - ✅ `Dashboard`
  - ✅ `GetQuestions`
  - ✅ `SeedData`
  - ✅ `TestFunction`
  - ✅ `TimerTrigger`

### Check 3: App Settings ✅
**Azure Portal → Function App → Configuration**
Verify these critical settings exist:
```
FUNCTIONS_WORKER_RUNTIME = python
FUNCTIONS_WORKER_RUNTIME_VERSION = 3.11
WEBSITE_PYTHON_DEFAULT_VERSION = 3.11
PYTHON_ISOLATE_WORKER_DEPENDENCIES = 1
SCM_DO_BUILD_DURING_DEPLOYMENT = true
ENABLE_ORYX_BUILD = true
linuxFxVersion = Python|3.11
```

---

## 🧪 Step 3: Test Function Endpoints

### Test 1: Basic Function Test
```
URL: https://func-{prefix}-coppa-analytics.azurewebsites.net/api/TestFunction?name=Test
EXPECTED: JSON response with greeting message
```

### Test 2: Analytics Endpoint
```
URL: https://func-{prefix}-coppa-analytics.azurewebsites.net/api/GetAnalytics?days=7
EXPECTED: JSON analytics data (demo data if no Cosmos DB connected)
```

### Test 3: Dashboard Access
```
URL: https://func-{prefix}-coppa-analytics.azurewebsites.net/api/Dashboard
EXPECTED: HTML dashboard interface
```

---

## 🚨 Step 4: What To Look For

### ✅ SUCCESS INDICATORS:
- Function App shows `Linux` platform
- All 6 functions are detected and listed
- Test endpoints return JSON responses (not 503 errors)
- No "Function host is not running" errors
- Application Insights shows telemetry data

### ❌ FAILURE INDICATORS:
- Platform shows `Windows` instead of `Linux`
- Functions not detected: "No functions found"
- 503 Service Unavailable errors
- "Function host is not running" message
- "Did not find functions with language [python]" error

---

## 🔧 Step 5: If Issues Occur

### Issue: Still shows Windows platform
**Cause**: Cached ARM template
**Solution**: Delete resource group completely and redeploy

### Issue: Functions not detected
**Cause**: Package deployment failed
**Solution**: 
1. Check Function App → Deployment Center
2. Verify package URL is accessible
3. Force sync deployment

### Issue: 503 errors persist
**Cause**: Runtime configuration
**Solution**: Run the fix script:
```powershell
$uri = "https://raw.githubusercontent.com/Russ-Holloway/CoPPA-Analytics/main/chatbot-analytics-azure-deploy/complete-python-fix.ps1"
Invoke-WebRequest -Uri $uri -OutFile "fix.ps1"
.\fix.ps1 -ResourceGroupName "your-rg-name" -FunctionAppName "your-function-name"
```

---

## 📋 Step 6: Final Verification Checklist

Before confirming success, verify ALL of these:

- [ ] Function App platform = `Linux`
- [ ] Runtime stack = `Python 3.11`
- [ ] All 6 functions detected
- [ ] TestFunction endpoint responds with 200
- [ ] GetAnalytics endpoint responds with JSON
- [ ] No 503 errors on any endpoint
- [ ] Application Insights collecting data
- [ ] Function App logs show successful initialization

**If ALL boxes are checked: ✅ DEPLOYMENT SUCCESSFUL!**

---

## 🎯 Expected Results

With the ARM template fixes, you should see:

1. **Immediate**: Function App deploys as Linux with Python 3.11
2. **2-3 minutes**: Functions are detected and listed in portal
3. **3-5 minutes**: All endpoints respond with valid JSON
4. **5-10 minutes**: Full functionality including analytics queries

**This resolves the core issue where Function Apps were being created as Windows instead of Linux, which prevented Python functions from running.**

---

## 📞 Support

If the deployment still fails after following this guide:

1. **Check Function App logs** in Azure Portal
2. **Verify resource group location** (UK South recommended)
3. **Try with a clean resource group** (delete and recreate)
4. **Contact with specific error messages** from the logs

**The ARM template is now correctly configured for Linux/Python deployment!** 🎉
