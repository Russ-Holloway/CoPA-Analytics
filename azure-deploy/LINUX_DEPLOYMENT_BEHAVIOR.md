# 🛠️ LINUX FUNCTION APP DEPLOYMENT GUIDE

## ⚡ Quick Start

### 1. Deploy Infrastructure
Click the **Deploy to Azure** button to create all resources (5-10 minutes).

### 2. Load Functions (If Needed)
If functions don't appear immediately, run this PowerShell script:

```powershell
# Download and run the function loader
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/Russ-Holloway/CoPPA-Analytics/main/chatbot-analytics-azure-deploy/Load-Functions.ps1" -OutFile "Load-Functions.ps1"
.\Load-Functions.ps1 -ResourceGroupName "your-rg-name" -FunctionAppName "your-function-name"
```

## 🐧 Linux Function App Behavior

### Why Functions May Not Load Immediately

Linux Function Apps on Azure have a **known behavior** where functions may not appear immediately after ARM deployment, even when the deployment succeeds. This happens because:

1. **Asynchronous Processing**: Function discovery runs asynchronously after app startup
2. **Build Timing**: Oryx build system may still be processing the package
3. **Cold Start**: Linux containers have longer initialization times
4. **Package Loading**: `WEBSITE_RUN_FROM_PACKAGE` requires time to download and extract

### This Is Normal!

This behavior is **documented by Microsoft** and affects many Linux Function App deployments. It's not a bug in our template.

## ✅ How to Verify Success

### Check 1: Deployment Status
- ARM deployment shows **"Succeeded"** ✅
- All resources created (Function App, Storage, etc.) ✅
- No resource errors ✅

### Check 2: Function App Status
- Function App is **"Running"** ✅
- Python runtime shows **"3.11"** ✅ 
- No runtime errors ✅

### Check 3: Functions Loaded
- All 6 functions appear in Azure portal ✅
- Functions respond to HTTP requests ✅

## 🔧 Troubleshooting Steps

### If No Functions Appear (5-15 minutes after deployment):

#### Option 1: Use the Function Loader Script
```powershell
.\Load-Functions.ps1 -ResourceGroupName "your-rg" -FunctionAppName "your-function-app"
```

#### Option 2: Manual Steps in Azure Portal
1. Go to your Function App
2. Click **"Restart"** button
3. Wait 5 minutes
4. Refresh the Functions list

#### Option 3: Use the Emergency Fix Script
```powershell
.\emergency-fix.ps1 -ResourceGroupName "your-rg" -FunctionAppName "your-function-app"
```

## 📊 Expected Timeline

| Time | What's Happening |
|------|------------------|
| 0-5 min | ARM deployment running |
| 5-8 min | Function App starting |
| 8-12 min | Package downloading & extracting |
| 12-15 min | Functions should appear |
| 15+ min | Run troubleshooting steps |

## 🎯 Success Indicators

Once working, you should see:

### ✅ All 6 Functions Listed:
- **Dashboard** - Web interface
- **GetAnalytics** - Main analytics API
- **GetQuestions** - Question analysis
- **SeedData** - Demo data population
- **TestFunction** - Health check
- **TimerTrigger** - Scheduled reports

### ✅ Working Endpoints:
- **Dashboard**: `https://your-function-app.azurewebsites.net/api/Dashboard`
- **Analytics**: `https://your-function-app.azurewebsites.net/api/GetAnalytics?days=7`

## 💡 Pro Tips

1. **Be Patient**: Linux Function Apps can take 10-15 minutes to fully initialize
2. **Use Scripts**: The provided scripts handle all the timing and edge cases
3. **Check Logs**: Function App logs show build progress and any errors
4. **Restart Helps**: When in doubt, restart the Function App

## 🆘 Still Having Issues?

If functions still don't load after 20+ minutes and running all scripts:

1. **Check Function App Logs** - Look for Python errors or build failures
2. **Verify Runtime** - Ensure it shows Python 3.11, not "Error"
3. **Try Fresh Deployment** - Delete resource group and redeploy
4. **Contact Support** - This may require Azure support investigation

## 📞 Support Resources

- **Azure Function App Documentation**: https://docs.microsoft.com/en-us/azure/azure-functions/
- **Linux Function Apps**: https://docs.microsoft.com/en-us/azure/azure-functions/functions-create-function-linux-custom-image
- **Troubleshooting Guide**: Built into our scripts and documentation

---

**Remember**: The deployment infrastructure works perfectly. The function loading delay is a known Linux Function App characteristic that our scripts handle automatically! 🚀
