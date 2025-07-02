# CoPPA Analytics - Ready for Deployment

## ✅ Deployment Status: READY

All infrastructure and function code deployment automation is now complete and ready for the "Deploy to Azure" button.

## 🎯 What's Been Fixed and Configured

### 1. Azure Naming Policy Compliance
- ✅ **Application Insights**: Fixed to use `appi-*` naming convention
- ✅ **Log Analytics Workspace**: Fixed to use `log-*` naming convention
- ✅ **All resources**: Follow organizational naming standards

### 2. Function App Runtime Configuration
- ✅ **Platform**: Switched from Linux to Windows (eliminates dynamic workers error)
- ✅ **Python Runtime**: Configured for Python 3.11 on Windows
- ✅ **App Settings**: All required settings for Windows Python Function Apps:
  - `FUNCTIONS_WORKER_RUNTIME=python`
  - `FUNCTIONS_WORKER_RUNTIME_VERSION=3.11`
  - `WEBSITE_PYTHON_DEFAULT_VERSION=3.11`
  - `WEBSITE_USE_PLACEHOLDER_DOTNETISOLATED=1`
  - `WEBSITE_RUN_FROM_PACKAGE=https://github.com/Russ-Holloway/CoPPA-Analytics/raw/main/chatbot-analytics-azure-deploy/function-app.zip`

### 3. Application Insights Integration
- ✅ **Workspace-based**: Uses Log Analytics workspace for enterprise compliance
- ✅ **Connection String**: Properly configured in Function App settings
- ✅ **Instrumentation Key**: Added for legacy compatibility

### 4. Automated Code Deployment
- ✅ **Function Code ZIP**: Created and uploaded to GitHub (`function-app.zip`)
- ✅ **ARM Template**: Configured to automatically download and deploy code from GitHub
- ✅ **No Manual Steps**: Function code deploys automatically with infrastructure

## 🚀 Deploy to Azure

### Main Deployment (Creates new Cosmos DB)
[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FRuss-Holloway%2FCoPPA-Analytics%2Fmain%2Fchatbot-analytics-azure-deploy%2Fazuredeploy.json)

### Existing Cosmos DB Deployment
[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FRuss-Holloway%2FCoPPA-Analytics%2Fmain%2Fchatbot-analytics-azure-deploy%2Fazuredeploy-existing-cosmos.json)

## 📋 Deployment Parameters

When you click "Deploy to Azure", you'll need to provide:

1. **Force Prefix**: 2-6 character police force code (e.g., BTP, MET, WMP)
2. **Admin Email**: Email address for daily analytics reports
3. **Existing Cosmos DB Endpoint**: (Optional) Your CoPPA Cosmos DB endpoint
4. **Existing Cosmos DB Key**: (Optional) Your CoPPA Cosmos DB primary key
5. **Cosmos DB Database**: Default: `db_conversation_history`
6. **Cosmos DB Container**: Default: `conversations`

## 🎯 What Happens During Deployment

1. **Infrastructure Creation** (5-10 minutes):
   - Storage Account (for Function App and dashboard)
   - App Service Plan (Consumption tier)
   - Log Analytics Workspace
   - Application Insights (workspace-based)
   - Function App (Windows, Python 3.11)

2. **Function Code Deployment** (Automatic):
   - Downloads `function-app.zip` from GitHub
   - Extracts and deploys all Python functions
   - Configures all environment variables
   - Enables Application Insights monitoring

3. **Ready to Use**:
   - Analytics API: `https://func-coppa-{prefix}-analytics.azurewebsites.net/api/`
   - Dashboard: Available via storage account static website
   - Monitoring: Application Insights with Log Analytics

## 🔍 Functions Included

- **GetAnalytics**: Main analytics API endpoint
- **GetQuestions**: Question analysis endpoint  
- **Dashboard**: Web dashboard hosting
- **SeedData**: Demo data generation
- **TestFunction**: Health check endpoint
- **TimerTrigger**: Scheduled analytics processing

## 📊 Monitoring and Logs

- **Application Insights**: Full telemetry and performance monitoring
- **Log Analytics**: Centralized logging with enterprise compliance
- **Function Logs**: Available in Azure Portal under Function App > Monitor

## 🎉 Success Indicators

After deployment completes, verify:

1. ✅ Function App shows "Running" status
2. ✅ Functions are loaded and operational
3. ✅ Application Insights is receiving telemetry
4. ✅ Test endpoint responds: `/api/TestFunction`
5. ✅ Analytics endpoint responds: `/api/GetAnalytics`

## 🚨 If Issues Occur

1. **Check Function App Logs**: Azure Portal > Function App > Monitor > Log Stream
2. **Verify App Settings**: Ensure all Python runtime settings are correct
3. **Check Application Insights**: Verify connection string and instrumentation key
4. **Function Status**: Ensure individual functions show as "Enabled"

---

**Ready for production deployment with full automation!** 🚀
