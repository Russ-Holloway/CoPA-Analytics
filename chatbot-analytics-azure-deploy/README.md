# CoPPA Analytics - Azure Deployment Solution

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FRuss-Holloway%2FCoPPA-Analytics%2Fmain%2Fchatbot-analytics-azure-deploy%2Fazuredeploy.json/createUIDefinitionUri/https%3A%2F%2Fraw.githubusercontent.com%2FRuss-Holloway%2FCoPPA-Analytics%2Fmain%2Fchatbot-analytics-azure-deploy%2FcreateUiDefinition.json)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Azure](https://img.shields.io/badge/Azure-Functions-blue.svg)](https://azure.microsoft.com/en-us/services/functions/)
[![Python](https://img.shields.io/badge/Python-3.11-green.svg)](https://www.python.org/)

> 🎯 **LATEST UPDATE**: Deployment issues **RESOLVED**! The ARM template now uses ZipDeploy for reliable one-click deployment on Linux Function Apps. All 6 functions load automatically. See [ONE_CLICK_DEPLOYMENT_FINAL.md](ONE_CLICK_DEPLOYMENT_FINAL.md) for details.

## 🚔 About CoPPA Analytics

**CoPPA Analytics** is a comprehensive analytics and reporting solution designed specifically for police forces using the **College of Policing - Policing Assistant (CoPPA)** chatbot platform. This solution provides automated insights, reporting, and dashboard capabilities to help police forces understand citizen engagement patterns and improve community policing effectiveness.

### ✨ Key Features

- **📊 Real-time Analytics Dashboard** - Interactive web dashboard showing chatbot usage, citizen engagement, and trending topics
- **📧 Automated Daily Reports** - Email reports sent to administrators with key metrics and insights
- **🔄 Seamless Integration** - Connects directly to existing CoPPA Cosmos DB deployments
- **🎯 One-Click Deployment** - Complete Azure infrastructure deployed in minutes
- **🏛️ Multi-Force Ready** - Easily customizable for different police forces
- **📈 Performance Monitoring** - Built-in Application Insights and monitoring
- **🔒 Secure by Design** - Enterprise-grade security with Azure best practices
- **⚡ Python 3.11 Ready** - Latest runtime with optimized performance

## 🚀 Quick Start - Deploy to Azure

### Step 1: Deploy Infrastructure (5-10 minutes)
1. **Click the "Deploy to Azure" button above** ⬆️
2. **Sign in to your Azure account** when prompted  
3. **Select your subscription** and choose or create a resource group
4. **Fill in the required parameters** and click "Create"
5. **Wait for deployment to complete** (creates Function App with Python 3.11)

### Step 2: Deploy Functions (2-3 minutes)
**After Step 1 completes, run this PowerShell command:**

```powershell
# Download and run the function deployment script
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/Russ-Holloway/CoPPA-Analytics/main/chatbot-analytics-azure-deploy/Deploy-After-ARM.ps1" -OutFile "Deploy-After-ARM.ps1"
.\Deploy-After-ARM.ps1
```

**Alternative methods:**
- **Azure CLI**: See [TWO_STEP_DEPLOYMENT.md](TWO_STEP_DEPLOYMENT.md)
- **Manual Kudu**: See [TWO_STEP_DEPLOYMENT.md](TWO_STEP_DEPLOYMENT.md)

✅ **Total time: 10-13 minutes for complete working solution**

### Step 2: Fill in the Deployment Form
- **Force Code**: Your police force identifier (e.g., "BTP", "MET", "GMP", "COP")
- **Administrator Email**: Email for automated reports and notifications
- **Cosmos DB Endpoint**: *(Optional)* Your existing CoPPA Cosmos DB URL
- **Cosmos DB Key**: *(Optional)* Primary key for your Cosmos DB
- **Database Name**: Default is "db_conversation_history"
- **Container Name**: Default is "conversations"

> **💡 Tip**: Leave Cosmos DB fields blank to use demo data for testing

### Step 3: Deploy and Verify
1. **Click "Review + create"** then **"Create"**
2. **Wait 5-10 minutes** for deployment to complete
3. **Run verification script** (optional but recommended):

```powershell
# Download and run verification
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/Russ-Holloway/CoPPA-Analytics/main/chatbot-analytics-azure-deploy/verify-deployment.ps1" -OutFile "verify-deployment.ps1"
.\verify-deployment.ps1 -ResourceGroupName "your-resource-group-name"
```

### Step 4: Test Your Deployment
After deployment, you'll get these URLs:
- **📊 Analytics API**: `https://func-coppa-{force}-analytics.azurewebsites.net/api/GetAnalytics?days=7`
- **🏠 Dashboard**: `https://func-coppa-{force}-analytics.azurewebsites.net/api/Dashboard`

## ✅ What Gets Deployed

The "Deploy to Azure" button creates:

- **🔧 Azure Function App** (Python 3.11 runtime)
- **📦 Storage Account** (for Function App and dashboard hosting)
- **📊 Application Insights** (monitoring and logging)
- **📋 Log Analytics Workspace** (centralized logging)
- **⚙️ Optimized Configuration** (all Python runtime fixes included)

### Included Functions:
- `GetAnalytics` - Main analytics API endpoint
- `Dashboard` - Interactive web dashboard
- `GetQuestions` - Question analysis endpoint
- `SeedData` - Demo data generator
- `TestFunction` - Health check endpoint
- `TimerTrigger` - Automated reporting (daily emails)

### Alternative: Azure CLI Deployment

```bash
# Clone the repository
git clone https://github.com/Russ-Holloway/CoPPA-Analytics.git
cd CoPPA-Analytics/chatbot-analytics-azure-deploy

# Deploy using Azure CLI
az group create --name rg-coppa-analytics --location "UK South"
az deployment group create --resource-group rg-coppa-analytics --template-file azuredeploy.json --parameters forceIdentifier=yourforce adminEmail=admin@yourforce.police.uk
```

## 🚀 Quick Deployment (Recommended)

For the most reliable deployment experience:

## Step 1: Deploy Infrastructure
[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FRuss-Holloway%2FCoPPA-Analytics%2Fmain%2Fchatbot-analytics-azure-deploy%2Fazuredeploy.json)

## Step 2: Upload Functions
**After deployment completes (3-5 minutes):**
1. Go to your Function App in Azure Portal
2. Click **Functions** → **+ Create** → **Upload a .zip file**
3. Download: [function-app-corrected.zip](https://github.com/Russ-Holloway/CoPPA-Analytics/raw/main/chatbot-analytics-azure-deploy/function-app-corrected.zip)
4. Upload the ZIP file and wait 2 minutes

**📋 [Detailed Upload Guide](SIMPLE_FUNCTION_UPLOAD_GUIDE.md)**

**Total time: ~5 minutes** ✅

---

# ...existing code...
