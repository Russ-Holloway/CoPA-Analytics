# Deploy to Azure - Complete Guide

## 🎯 One-Click Deployment for CoPPA Analytics

This guide walks you through deploying CoPPA Analytics using the "Deploy to Azure" button - the easiest and most reliable method.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FRuss-Holloway%2FCoPPA-Analytics%2Fmain%2Fchatbot-analytics-azure-deploy%2Fazuredeploy.json/createUIDefinitionUri/https%3A%2F%2Fraw.githubusercontent.com%2FRuss-Holloway%2FCoPPA-Analytics%2Fmain%2Fchatbot-analytics-azure-deploy%2FcreateUiDefinition.json)

## ✅ Pre-Deployment Checklist

Before clicking "Deploy to Azure", ensure you have:

- [ ] **Azure Subscription** with appropriate permissions
- [ ] **Force Code** ready (e.g., "BTP", "MET", "GMP", "COP")
- [ ] **Administrator Email** for reports
- [ ] **Cosmos DB Details** (optional - for real CoPPA data)
  - [ ] Cosmos DB Endpoint URL
  - [ ] Primary Access Key
  - [ ] Database Name (usually "db_conversation_history")
  - [ ] Container Name (usually "conversations")

## 🚀 Step-by-Step Deployment

### Step 1: Click Deploy to Azure
1. Click the blue "Deploy to Azure" button above
2. Sign in to your Azure account when prompted
3. You'll be taken to a custom deployment form

### Step 2: Basic Configuration
Fill in the **Basics** section:

**Subscription**: Select your Azure subscription
**Resource Group**: Choose existing or create new (recommended: `rg-coppa-{force}-analytics`)
**Region**: Select closest region (UK South recommended for UK forces)
**Force Code**: Enter your force identifier
- ✅ Examples: `BTP`, `MET`, `GMP`, `COP`, `TVP`
- ❌ Avoid: spaces, numbers, special characters
**Administrator Email**: Enter email for reports
- ✅ Example: `admin@yourforce.police.uk`
- ❌ Avoid: personal emails

### Step 3: Cosmos DB Configuration
In the **Cosmos DB Configuration** section:

**For Testing/Demo (Recommended for first deployment):**
- Leave **Cosmos DB Endpoint URL** blank
- Leave **Cosmos DB Primary Key** blank
- Keep default **Database Name**: `db_conversation_history`
- Keep default **Container Name**: `conversations`

**For Production with Real CoPPA Data:**
- Enter your **Cosmos DB Endpoint URL**: `https://your-cosmos.documents.azure.com:443/`
- Enter your **Cosmos DB Primary Key** (found in Azure Portal > Cosmos DB > Keys)
- Verify **Database Name** matches your CoPPA database
- Verify **Container Name** matches your conversations container

### Step 4: Review and Deploy
1. Click **"Review + create"**
2. Azure will validate your configuration
3. If validation passes, click **"Create"**
4. Deployment takes 5-10 minutes

## ⏳ During Deployment

While Azure deploys your resources:

### What's Being Created:
- **Function App** (with Python 3.11 runtime)
- **Storage Account** (for app and dashboard)
- **Application Insights** (monitoring)
- **Log Analytics Workspace** (logging)

### Automatic Configuration:
- ✅ Python 3.11 runtime settings
- ✅ Correct extension bundle version
- ✅ Oryx build configuration
- ✅ Function App settings
- ✅ CORS policies
- ✅ Monitoring setup

## ✅ Post-Deployment Verification

### Step 1: Check Deployment Status
1. Wait for "Your deployment is complete" message
2. Note the **Outputs** section with your URLs
3. Save the Function App name for later

### Step 2: Verify Function App
1. Go to **Azure Portal** > **Resource Groups** > **Your Resource Group**
2. Click on your **Function App** (name starts with `func-coppa-`)
3. Check that **Status** shows "Running"
4. Go to **Functions** and verify you see:
   - GetAnalytics
   - Dashboard
   - GetQuestions
   - SeedData
   - TestFunction
   - TimerTrigger

### Step 3: Test Analytics Endpoint
Test your deployment by visiting:
```
https://func-coppa-{force}-analytics.azurewebsites.net/api/GetAnalytics?days=7
```

Expected response (if using demo data):
```json
{
  "metadata": {
    "force_id": "YOUR_FORCE",
    "data_source": "demo_data",
    "period": "...",
    "total_conversations": 150
  },
  "summary": {
    "total_interactions": 150,
    "unique_users": 89,
    "avg_conversation_length": 4.2
  }
  // ... more data
}
```

### Step 4: Run Automated Verification (Optional)
Download and run our verification script:

```powershell
# Download verification script
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/Russ-Holloway/CoPPA-Analytics/main/chatbot-analytics-azure-deploy/verify-deployment.ps1" -OutFile "verify-deployment.ps1"

# Run verification
.\verify-deployment.ps1 -ResourceGroupName "your-resource-group-name"
```

This script will:
- ✅ Check Function App status
- ✅ Verify Python runtime configuration
- ✅ Test all endpoints
- ✅ Provide next steps

## 🔧 Troubleshooting

### Common Issues and Solutions:

**🚫 "Function host is not running" (503 error)**
- **Cause**: Python runtime configuration issues
- **Solution**: Run the verification script, which will auto-fix settings

**🚫 "No functions found"**
- **Cause**: Package deployment failed
- **Solution**: Function App > Deployment Center > Sync to redeploy

**🚫 "Authentication failed"**
- **Cause**: Cosmos DB key issues
- **Solution**: Update COSMOS_DB_KEY in Function App settings

**🚫 "Timeout errors"**
- **Cause**: Cold start (normal for first request)
- **Solution**: Wait 30 seconds and try again

### Getting Help:

1. **Check Function App Logs**:
   - Azure Portal > Function App > Log stream
   - Look for error messages

2. **Check Application Insights**:
   - Azure Portal > Application Insights > Failures
   - Review exception details

3. **Contact Support**:
   - Include deployment outputs
   - Include error messages from logs
   - Specify force code and region

## 🎉 Success! What's Next?

Once deployment is successful:

### 1. Test All Endpoints
- **Analytics**: `/api/GetAnalytics?days=7`
- **Dashboard**: `/api/Dashboard`
- **Questions**: `/api/GetQuestions?days=30`

### 2. Configure Email Reports (Optional)
Update Function App settings for automated daily reports:
- `EMAIL_ENABLED`: `true`
- `EMAIL_TO`: Your admin email
- `EMAIL_FROM`: Your organization email
- `SMTP_SERVER`: Your email server
- `SMTP_PORT`: Usually `587`

### 3. Connect Real CoPPA Data (If not done during deployment)
Update Function App settings:
- `COSMOS_DB_ENDPOINT`: Your Cosmos DB URL
- `COSMOS_DB_KEY`: Your Cosmos DB key
- Verify `COSMOS_DB_DATABASE` and `COSMOS_DB_CONTAINER`

### 4. Set Up Monitoring
- Configure alerts in Application Insights
- Set up dashboard bookmarks
- Schedule regular health checks

## 📱 Your New URLs

After deployment, bookmark these URLs:

**Analytics API**:
```
https://func-coppa-{force}-analytics.azurewebsites.net/api/GetAnalytics?days=7
```

**Interactive Dashboard**:
```
https://func-coppa-{force}-analytics.azurewebsites.net/api/Dashboard
```

**Azure Portal - Function App**:
```
https://portal.azure.com/#resource/subscriptions/{subscription}/resourceGroups/{rg}/providers/Microsoft.Web/sites/func-coppa-{force}-analytics
```

---

## 🏆 Congratulations!

You've successfully deployed CoPPA Analytics using the Deploy to Azure button! 

Your police force now has:
- ✅ Real-time analytics dashboard
- ✅ Automated reporting capabilities  
- ✅ Performance monitoring
- ✅ Secure, scalable infrastructure

**Need help?** Contact the development team or check the troubleshooting section above.
