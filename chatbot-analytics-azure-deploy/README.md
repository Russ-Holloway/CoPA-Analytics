# 🚀 CoPPA Analytics - Simple Two-Step Deployment

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FRuss-Holloway%2FCoPPA-Analytics%2Fmain%2Fchatbot-analytics-azure-deploy%2Fazuredeploy.json)

## ⚡ Quick Start (2 Steps)

### Step 1: Deploy Infrastructure
**Click the "Deploy to Azure" button above**
- Fill in your police force code (e.g., "BTP", "MET")
- Enter admin email address
- Add your existing Cosmos DB details
- Click "Create" and wait 5-10 minutes

### Step 2: Upload Functions
1. **Download**: [function-app-corrected.zip](https://github.com/Russ-Holloway/CoPPA-Analytics/raw/main/chatbot-analytics-azure-deploy/function-app-corrected.zip)
2. **Go to your Function App** in Azure Portal
3. **Functions** → **Create** → **Upload ZIP file**
4. **Upload the ZIP** and wait for deployment

## ✅ You're Done!

- **Dashboard**: `https://[function-app-name].azurewebsites.net/api/Dashboard`
- **Analytics API**: `https://[function-app-name].azurewebsites.net/api/GetAnalytics?days=7`
- **Daily reports** will be emailed automatically

## � What Gets Deployed

- **Function App** (Linux, Python 3.11) - Ready for ZIP upload
- **Storage Account** - For function storage
- **Application Insights** - For monitoring

## � Includes 7 Functions

1. **GetAnalytics** - Main analytics API
2. **Dashboard** - Interactive web dashboard  
3. **GetQuestions** - Question analysis
4. **SeedData** - Demo data generator
5. **TestFunction** - Health check
6. **TimerTrigger** - Scheduled tasks
7. **FunctionSync** - Function status monitoring

## 🚨 Troubleshooting

If you have issues, try:
1. **Delete the Function App** and redeploy
2. **Use fresh resource group** for clean deployment
3. **Check the ZIP upload** completed successfully

## 📞 Support

For deployment issues or questions, please open an issue in this repository.
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
