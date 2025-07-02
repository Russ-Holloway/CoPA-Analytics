# CoPPA Analytics - Azure Deployment Solution

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FRuss-Holloway%2FCoPPA-Analytics%2Fmain%2Fchatbot-analytics-azure-deploy%2Fazuredeploy.json/createUIDefinitionUri/https%3A%2F%2Fraw.githubusercontent.com%2FRuss-Holloway%2FCoPPA-Analytics%2Fmain%2Fchatbot-analytics-azure-deploy%2FcreateUiDefinition.json)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Azure](https://img.shields.io/badge/Azure-Functions-blue.svg)](https://azure.microsoft.com/en-us/services/functions/)
[![Python](https://img.shields.io/badge/Python-3.9+-green.svg)](https://www.python.org/)

## 🚔 About CoPPA Analytics

**CoPPA Analytics** is a comprehensive analytics and reporting solution designed specifically for police forces using the **Community Policing Partnership Assistant (CoPPA)** chatbot platform. This solution provides automated insights, reporting, and dashboard capabilities to help police forces understand citizen engagement patterns and improve community policing effectiveness.

### ✨ Key Features

- **📊 Real-time Analytics Dashboard** - Interactive web dashboard showing chatbot usage, citizen engagement, and trending topics
- **📧 Automated Daily Reports** - Email reports sent to administrators with key metrics and insights
- **🔄 Seamless Integration** - Connects directly to existing CoPPA Cosmos DB deployments
- **🎯 One-Click Deployment** - Complete Azure infrastructure deployed in minutes
- **🏛️ Multi-Force Ready** - Easily customizable for different police forces
- **📈 Performance Monitoring** - Built-in Application Insights and monitoring
- **🔒 Secure by Design** - Enterprise-grade security with Azure best practices

## 🚀 Quick Start

### Prerequisites
- Existing CoPPA chatbot deployment with Cosmos DB
- Azure subscription with appropriate permissions
- Email account for automated reports (Office 365 recommended)

### Deploy to Azure (Recommended)

1. **Click the "Deploy to Azure" button above**
2. **Fill in the deployment form:**
   - **Force Code**: Your police force identifier (e.g., "btp", "met", "gmp")
   - **Administrator Email**: Email for reports and notifications
   - **Cosmos DB Details**: Connection string and database information from your existing CoPPA deployment
   - **Email Configuration**: SMTP settings for automated reports

3. **Review and Deploy**: The deployment typically takes 5-10 minutes

### Alternative: PowerShell Deployment

```powershell
# Clone the repository
git clone https://github.com/Russ-Holloway/CoPPA-Analytics.git
cd CoPPA-Analytics/chatbot-analytics-azure-deploy

# Run deployment script
.\deploy-coppa.ps1 -ForceId "your-force-code" -ResourceGroupName "rg-coppa-analytics" -Location "UK South" -AdminEmail "admin@yourforce.police.uk"
```

### Alternative: Azure CLI Deployment

```bash
# Clone the repository
git clone https://github.com/Russ-Holloway/CoPPA-Analytics.git
cd CoPPA-Analytics/chatbot-analytics-azure-deploy

# Deploy using Azure CLI
az group create --name rg-coppa-analytics --location "UK South"
az deployment group create --resource-group rg-coppa-analytics --template-file azuredeploy.json --parameters forceIdentifier=yourforce adminEmail=admin@yourforce.police.uk
```

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
