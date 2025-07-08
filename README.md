# CoPPA Analytics - Azure Deployment Solution

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FRuss-Holloway%2FCoPPA-Analytics%2Fmain%2Fazure-deploy%2Fazuredeploy.json)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Azure](https://img.shields.io/badge/Azure-Functions-blue.svg)](https://azure.microsoft.com/en-us/services/functions/)
[![Python](https://img.shields.io/badge/Python-3.11-green.svg)](https://www.python.org/)

## 🚔 About CoPPA Analytics

**CoPPA Analytics** is a comprehensive analytics and reporting solution designed specifically for police forces using the **College of Policing - Policing Assistant (CoPPA)** chatbot platform. This solution provides automated insights, reporting, and dashboard capabilities to help police forces understand citizen engagement patterns and improve community policing effectiveness.

### ✨ Key Features

- **📊 Real-time Analytics Dashboard** - Interactive web dashboard showing chatbot usage, citizen engagement, and trending topics
- **📧 Automated Daily Reports** - Email reports sent to administrators with key metrics and insights
- **🔄 Seamless Integration** - Connects directly to existing CoPPA Cosmos DB deployments
- **🎯 Two-Step Deployment** - Simple deployment process for non-technical users
- **🏛️ Multi-Force Ready** - Easily customizable for different police forces
- **📈 Performance Monitoring** - Built-in Application Insights and monitoring
- **🔒 Secure by Design** - Enterprise-grade security with Azure best practices

## 🚀 Quick Deployment Guide

### **Step 1: Deploy Infrastructure (5-10 minutes)**

1. **Click the "Deploy to Azure" button above** ⬆️
2. **Fill in the deployment form:**
   - **Force Prefix**: Your police force code (e.g., "BTP", "MET", "GMP", "WMP")
   - **Admin Email**: Email address for daily analytics reports
   - **Existing Cosmos DB Endpoint**: Your CoPPA Cosmos DB URL (or leave blank for demo data)
   - **Existing Cosmos DB Key**: Your CoPPA Cosmos DB primary key (or leave blank for demo data)
   - **Cosmos DB Database**: Usually `db_conversation_history` (check your CoPPA database)
   - **Cosmos DB Container**: Usually `conversations` (check your CoPPA container)
3. **Click "Review + create"** then **"Create"**
4. **Wait 5-10 minutes** for deployment to complete
5. **Note your Function App name** - it will be `func-[your-prefix]-analytics`

### **Step 2: Configure GitHub Deployment (2-3 minutes)**

1. **Go to your new Function App** in the Azure Portal
2. **Navigate to "Deployment Center"** in the left menu
3. **Select "GitHub"** as the deployment source
4. **Configure the following:**
   - **Organization**: `Russ-Holloway`
   - **Repository**: `CoPPA-Analytics`
   - **Branch**: `main`
   - **Workflow Option**: Select "Overwrite the workflow"
   - **Authentication Type**: Select "User-assigned identity"
   - **Identity**: Select "(Create new)"
5. **Click "Save"** and wait 2-3 minutes for automatic deployment

### **✅ Verification**

Your analytics solution is now running! Access:

**Dashboard**: `https://func-[your-prefix]-analytics.azurewebsites.net/api/Dashboard`  
**Analytics API**: `https://func-[your-prefix]-analytics.azurewebsites.net/api/GetAnalytics?days=7`

### **🔧 Troubleshooting**

**Dashboard shows "Error loading data":**
- Check your Cosmos DB environment variables in Function App → Settings → Environment variables
- Ensure Cosmos DB allows access from Azure services (Networking → Firewall settings)
- Verify database and container names match your CoPPA deployment

**401 Authorization errors:**
- Functions should be set to "anonymous" authorization (this is automatic with GitHub deployment)
- If issues persist, check Function App logs in Monitoring → Log stream

**Functions not appearing:**
- Check GitHub Actions at https://github.com/Russ-Holloway/CoPA-Analytics/actions
- Wait for deployment to complete (green checkmark)
- Functions may take 2-3 minutes to appear after GitHub deployment

## 📋 What Gets Deployed

After successful deployment, you'll have **7 Azure Functions** providing comprehensive analytics:

### **🎛️ Dashboard** - `/api/Dashboard`
- **Purpose**: Interactive web-based analytics dashboard
- **Features**: Real-time charts, metrics, and data visualization
- **Access**: Direct browser access to view all analytics

### **📊 GetAnalytics** - `/api/GetAnalytics` 
- **Purpose**: Main analytics API endpoint
- **Features**: Conversation metrics, trending topics, engagement data
- **Parameters**: `?days=7` (last 7 days), `?category=crime` (filter by topic)

### **❓ GetQuestions** - `/api/GetQuestions`
- **Purpose**: Most asked questions and topics analysis
- **Features**: Question frequency, trending queries, topic clustering
- **Use**: Identify citizen concerns and popular topics

### **🌱 SeedData** - `/api/SeedData`
- **Purpose**: Generate demo/test data for new deployments
- **Features**: Creates sample conversations for testing
- **Use**: Test analytics with realistic demo data

### **🧪 TestFunction** - `/api/TestFunction`
- **Purpose**: Health check and connectivity testing
- **Features**: Verifies Cosmos DB connection and function status
- **Use**: Troubleshooting and system validation

### **⏰ TimerTrigger** - (Automatic)
- **Purpose**: Scheduled daily analytics processing
- **Features**: Generates daily email reports, data aggregation
- **Schedule**: Runs automatically at 7:00 AM UTC daily

### **🔄 FunctionSync** - `/api/FunctionSync`
- **Purpose**: Data synchronization and maintenance
- **Features**: Updates analytics data, cleans old records
- **Use**: Keeps analytics data current and optimized

## 🏗️ Architecture

The solution deploys the following Azure resources:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Azure Portal  │    │  Function App    │    │  Cosmos DB      │
│   Dashboard     │───▶│  (Analytics)     │───▶│  (Existing)     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │ Application      │
                       │ Insights         │
                       └──────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │ Email Reports    │
                       │ (Daily/Weekly)   │
                       └──────────────────┘
```

### Deployed Resources:
- **📱 Function App**: Python-based serverless analytics functions
- **💾 Storage Account**: Function app storage and static dashboard hosting
- **📊 Application Insights**: Monitoring, logging, and performance analytics
- **🌐 Static Web App**: Analytics dashboard (optional)
- **📧 Logic App**: Email delivery for automated reports (optional)

## 📋 Functions Included

### 🔍 CoPPA Analytics API (`/api/GetAnalytics`)
- **Type**: HTTP Trigger (GET/POST)
- **Purpose**: Retrieve comprehensive analytics from CoPPA conversations
- **Features**:
  - Conversation volume analysis
  - Topic categorization and trending
  - Citizen engagement metrics
  - Response time analytics
  - Sentiment analysis
- **Parameters**: `start_date`, `end_date`, `category`, `format`

### ⏰ Daily Report Generator (`CoPPADailyReport`)
- **Type**: Timer Trigger
- **Schedule**: Daily at 7:00 AM UTC
- **Purpose**: Generate and email daily analytics reports
- **Features**:
  - Executive summary with key metrics
  - Trend analysis and comparisons
  - Action items and recommendations
  - Customizable recipient lists
  - PDF and HTML report formats

### 🏥 Health Check (`/api/health`)
- **Type**: HTTP Trigger (GET)
- **Purpose**: System health monitoring and diagnostics
- **Returns**: Service status, database connectivity, and performance metrics

### 📊 Dashboard Data (`/api/Dashboard`)
- **Type**: HTTP Trigger (GET)
- **Purpose**: Real-time data for analytics dashboard
- **Features**:
  - Live conversation metrics
  - Performance indicators
  - Trend visualizations
  - Custom date ranges

## ⚙️ Post-Deployment Configuration

After successful deployment, your CoPPA Analytics solution will be automatically configured. However, you may want to customize these settings:

### Environment Variables (Automatically Set)
```bash
# Cosmos DB Configuration
COSMOS_DB_ENDPOINT=<from-deployment-form>
COSMOS_DB_KEY=<from-deployment-form>
COSMOS_DB_DATABASE=<from-deployment-form>
COSMOS_DB_CONTAINER=<from-deployment-form>

# Email Configuration
SMTP_SERVER=<from-deployment-form>
SMTP_PORT=<from-deployment-form>
EMAIL_USERNAME=<from-deployment-form>
EMAIL_PASSWORD=<from-deployment-form>

# Force Configuration
FORCE_IDENTIFIER=<your-force-code>
ADMIN_EMAIL=<admin-email>
```

### Optional Customizations

1. **Report Recipients**: Add additional email addresses in the Function App configuration
2. **Report Schedule**: Modify the timer trigger schedule in `function.json`
3. **Dashboard Branding**: Update logo and colors in the dashboard configuration
4. **Alert Thresholds**: Configure custom alerts for conversation volume or response times

## 🧪 Testing Your Deployment

After deployment, test these endpoints:

### Dashboard
```
https://func-coppa-[your-force]-analytics.azurewebsites.net/api/Dashboard
```

### Analytics API
```
https://func-coppa-[your-force]-analytics.azurewebsites.net/api/GetAnalytics?days=7
```

### Health Check
```
https://func-coppa-[your-force]-analytics.azurewebsites.net/api/health
```

## 💰 Cost Estimates

### Monthly Costs (approximate):
- **Function App**: £5-20/month (depends on usage)
- **Storage**: £1-5/month 
- **Application Insights**: £5-15/month
- **Total**: ~£15-40/month for typical force

### Cost Optimization:
- Uses consumption-based pricing
- Scales automatically with usage
- No fixed monthly fees
- Can set spending limits

## 🔒 Security & Privacy

- **Secure Connection**: All data encrypted in transit (HTTPS/TLS 1.2)
- **Azure Security**: Follows Azure security best practices
- **Data Isolation**: Your analytics remain in your Azure tenant
- **No Data Sharing**: BTP cannot access your analytics data
- **GDPR Compliant**: Personal data handling follows UK police standards

## 🆘 Troubleshooting

### Common Issues:

**Dashboard shows "Loading..." forever:**
- Check Cosmos DB connection details
- Verify your CoPPA database has conversation data

**No daily emails:**
- Check admin email address is correct
- Check Azure Function App logs

**"Access Denied" errors:**
- Verify Cosmos DB key is correct
- Check firewall settings on Cosmos DB

**Function deployment failed:**
- Check Azure permissions
- Verify resource group exists
- Try deploying to different Azure region

### Getting Help:
1. Check Azure Function App logs in Azure Portal
2. Review deployment logs in Azure Portal
3. Contact your Azure support team
4. File issues on GitHub repository

## 📞 Support

- **GitHub Issues**: [Report issues here](https://github.com/Russ-Holloway/CoPPA-Analytics/issues)
- **Documentation**: Available in repository
- **Azure Support**: Contact your Azure support team for Azure-specific issues

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built for police forces using CoPPA chatbot technology
- Designed for self-service deployment and management
- Supports multiple police forces with data isolation

---

**Ready to deploy?** Click the "Deploy to Azure" button above and get started in minutes! 🚀

## 🚦 Deployment, GitHub Integration, and Dashboard Branding Flow

### 1. Azure Deployment (ARM Template)
- Click the **Deploy to Azure** button and fill in the required parameters (force prefix, admin email, Cosmos DB details, etc).
- **Force Logo URL**: Enter the public URL of your force's logo (e.g., from Azure Blob Storage). This is stored as the `FORCE_LOGO_URL` environment variable in your Function App.
- Complete the deployment. Azure will provision the Function App, storage, and monitoring resources.

### 2. Link to External GitHub Repository
- In the Azure Portal, go to your new Function App → **Deployment Center**.
- Select **GitHub** as the source, choose the `Russ-Holloway/CoPPA-Analytics` repository and the `main` branch.
- Complete the setup. Azure will automatically deploy the latest code from GitHub to your Function App.
- Any future updates to the GitHub repository will be automatically deployed to your Function App.

### 3. Dashboard Logo Branding (FORCE_LOGO_URL)
- The dashboard (`/api/Dashboard`) loads the right-side logo directly from the `FORCE_LOGO_URL` environment variable.
- The value you set at deployment (or update later in Function App → Configuration) must be a public, direct image URL (e.g., Azure Blob Storage with public read access).
- If the logo URL is valid and accessible, it will appear on the dashboard. If not, a placeholder image is shown.
- To update the logo later, simply change the `FORCE_LOGO_URL` app setting and restart the Function App.

### 4. Accessing the Dashboard
- After deployment and GitHub sync, visit:
  - `https://func-[your-prefix]-analytics.azurewebsites.net/api/Dashboard`
- The dashboard will show your force's branding and live analytics.

---
