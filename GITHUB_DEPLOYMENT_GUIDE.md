# CoPPA Analytics - GitHub Deployment Solution

## Overview
This is the **FINAL, PRODUCTION-READY** deployment solution for CoPPA Analytics. After extensive testing and troubleshooting, this method provides the most reliable deployment for non-technical users across all 44 police forces.

## Why GitHub Deployment?
Azure Function Apps on Linux plans **require** a deployment source (GitHub, Azure Repos, or CI/CD). Manual ZIP uploads are not supported and will result in read-only mode. GitHub deployment is:
- ✅ Fully automated
- ✅ No manual steps required
- ✅ Reliable across all Azure regions
- ✅ Easy to support and troubleshoot
- ✅ Suitable for non-technical users

## Quick Start (2-Step Process)

### Step 1: Deploy Infrastructure
1. Click the **Deploy to Azure** button below
2. Fill in your force prefix and email
3. Wait for deployment to complete (5-10 minutes)

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FRuss-Holloway%2FCoPPA-Analytics%2Fmain%2Fchatbot-analytics-azure-deploy%2Fazuredeploy.json)

### Step 2: Configure GitHub Deployment
1. Go to your new Function App in the Azure Portal
2. Navigate to **Deployment Center**
3. Select **GitHub** as source
4. Configure:
   - **Organization**: `Russ-Holloway` 
   - **Repository**: `CoPPA-Analytics`
   - **Branch**: `main`
5. Click **Save**
6. Wait 2-3 minutes for automatic deployment

**That's it!** All 7 functions will be automatically detected and deployed.

## What Gets Deployed?

### Azure Resources
- **Function App** (Linux, Python 3.11)
- **App Service Plan** (B1 tier)
- **Storage Account** (for function storage)
- **Application Insights** (for monitoring)

### Functions Deployed from GitHub
1. **GetAnalytics** - Main analytics API endpoint
2. **Dashboard** - Web dashboard interface  
3. **GetQuestions** - Question analytics
4. **SeedData** - Demo data seeding
5. **TestFunction** - Health check endpoint
6. **TimerTrigger** - Scheduled analytics processing
7. **FunctionSync** - Data synchronization

## Verification Steps

After deployment, verify everything is working:

1. **Check Functions**: In Function App → Functions, you should see all 7 functions listed
2. **Test Analytics API**: Visit `https://[your-function-app].azurewebsites.net/api/analytics`
3. **View Dashboard**: Visit `https://[your-function-app].azurewebsites.net/api/dashboard`
4. **Check Logs**: Monitor Application Insights for any errors

## Troubleshooting

### No Functions Visible
- **Cause**: GitHub deployment hasn't completed
- **Solution**: Check Deployment Center → Logs, wait for build to complete

### Functions Show but Don't Work
- **Cause**: Missing environment variables
- **Solution**: Check Configuration → Application Settings for COSMOS_DB_ENDPOINT and COSMOS_DB_KEY

### Read-Only Mode Warning
- **Cause**: Normal behavior with GitHub deployment
- **Solution**: This is expected and correct - all changes go through GitHub

## Support Information

### For Police Force IT Teams
- **Deployment Method**: ARM Template + GitHub source
- **Runtime**: Python 3.11 on Linux
- **Dependencies**: Automatically installed via requirements.txt
- **Monitoring**: Built-in Application Insights
- **Scaling**: Automatic based on demand

### For Developers
- **Repository**: https://github.com/Russ-Holloway/CoPPA-Analytics
- **Function Code Location**: Repository root (not in subfolder)
- **Deployment**: Automatic on every commit to main branch
- **Local Development**: Clone repo, use Azure Functions Core Tools

## Important Notes

⚠️ **Do NOT use manual ZIP upload** - this will not work with Linux Function Apps and will cause read-only mode.

✅ **Always use GitHub deployment** - this is the only supported method for this solution.

📧 **Contact**: For support or questions, contact the BTP Digital Analytics Team.

---

**Version**: 2.0 (GitHub Deployment)  
**Last Updated**: December 2024  
**Status**: Production Ready ✅
