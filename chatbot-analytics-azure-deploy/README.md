# CoPPA Analytics - Azure Deployment Solution

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FRuss-Holloway%2FCoPPA-Analytics%2Fmain%2Fchatbot-analytics-azure-deploy%2Fazuredeploy.json/createUIDefinitionUri/https%3A%2F%2Fraw.githubusercontent.com%2FRuss-Holloway%2FCoPPA-Analytics%2Fmain%2Fchatbot-analytics-azure-deploy%2FcreateUiDefinition.json)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Azure](https://img.shields.io/badge/Azure-Functions-blue.svg)](https://azure.microsoft.com/en-us/services/functions/)
[![Python](https://img.shields.io/badge/Python-3.9+-green.svg)](https://www.python.org/)

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

### 🔍 CoPPA Analytics API (`/api/get_analytics`)
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

### 📊 Dashboard Data (`/api/dashboard_data`)
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
COSMOS_DB_CONNECTION_STRING=<from-deployment-form>
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

### 1. Test the Analytics API
```bash
# Replace with your actual function app URL
curl "https://func-<your-force>-coppa-analytics.azurewebsites.net/api/get_coppa_analytics?days=7"
```

### 2. Test the Health Check
```bash
curl "https://func-<your-force>-coppa-analytics.azurewebsites.net/api/health"
```

### 3. Access the Dashboard
Navigate to: `https://func-<your-force>-coppa-analytics.azurewebsites.net/dashboard`

### 4. Verify Daily Reports
Check that daily reports are being generated and emailed successfully (may take 24 hours for first report).

## 🎨 Customization for Your Police Force

### Resource Naming Convention
All resources are automatically named with your force identifier:
- **Resource Group**: `rg-<force>-coppa-analytics`
- **Function App**: `func-<force>-coppa-analytics`
- **Storage Account**: `st<force>coppa<random>`
- **Application Insights**: `appi-<force>-coppa-analytics`

### Force-Specific Branding
1. **Logo**: Replace `logo.png` in the dashboard storage
2. **Colors**: Update CSS variables in `dashboard/style.css`
3. **Reports**: Customize email templates in `templates/` directory
4. **Terminology**: Update force-specific terms in configuration

### Data Integration
- **Existing CoPPA Data**: Automatically connects to your Cosmos DB
- **Custom Fields**: Add force-specific data fields in function configuration
- **External Systems**: Integrate with existing police databases (requires custom development)

## 📊 Monitoring and Maintenance

### Built-in Monitoring
- **📈 Application Insights**: Automatic performance and error tracking
- **🚨 Azure Alerts**: Proactive monitoring and notifications
- **📝 Function Logs**: Detailed execution logs for troubleshooting
- **💻 Dashboard Health**: Real-time system status monitoring

### Recommended Alerts
The deployment includes pre-configured alerts for:
- Function execution failures
- High response times
- Database connectivity issues
- Email delivery failures

### Maintenance Tasks
- **Weekly**: Review Application Insights for performance trends
- **Monthly**: Check storage usage and optimize if needed
- **Quarterly**: Review and update email distribution lists
- **Annually**: Evaluate usage patterns and consider scaling options

## 🤝 Support and Community

### Getting Help
1. **📚 Documentation**: Check this README and the `/docs` directory
2. **🐛 Issues**: Report bugs or request features via GitHub Issues
3. **💬 Discussions**: Join community discussions for tips and best practices
4. **📧 Direct Support**: Contact the development team for urgent issues

### Contributing
We welcome contributions from police forces using CoPPA Analytics:

1. **🍴 Fork** this repository
2. **🌿 Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **💾 Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **📤 Push** to the branch (`git push origin feature/amazing-feature`)
5. **🔄 Open** a Pull Request

### Community Guidelines
- Share insights and best practices with other forces
- Contribute improvements that benefit the entire community
- Maintain security and privacy standards
- Follow coding standards and documentation requirements

## 📈 Success Stories

> **"CoPPA Analytics has transformed how we understand citizen engagement. The automated reports save hours of manual work and provide insights we never had before."**  
> *— Chief Inspector, British Transport Police*

> **"The one-click deployment made it incredibly easy to get analytics up and running. Within an hour, we had comprehensive reporting on our chatbot usage."**  
> *— Digital Innovation Team, Metropolitan Police*

## 🔄 Version History

| Version | Date | Description |
|---------|------|-------------|
| **v2.0** | 2024-01 | CoPPA-branded release with enhanced analytics |
| **v1.2** | 2023-12 | Added automated reporting and dashboard |
| **v1.1** | 2023-11 | Enhanced multi-tenant support and ARM templates |
| **v1.0** | 2023-10 | Initial deployment with basic analytics functions |

## 📋 Requirements and Compatibility

### Azure Requirements
- **Subscription**: Azure subscription with Function App permissions
- **Regions**: Available in all Azure regions (UK South recommended)
- **Costs**: Consumption-based pricing (typically £10-50/month depending on usage)

### CoPPA Compatibility
- **Versions**: Compatible with CoPPA v1.5+
- **Database**: Cosmos DB (SQL API)
- **Authentication**: Supports Azure AD and connection string authentication

### Technical Requirements
- **Python**: 3.9+ (managed by Azure Functions)
- **Dependencies**: Automatically installed during deployment
- **Browser**: Modern browsers for dashboard access (Chrome, Firefox, Edge, Safari)

---

## 🏛️ Developed by British Transport Police

This solution was developed by the British Transport Police Digital Innovation Team as part of the College of Policing - Policing Assistant (CoPPA) initiative. It's designed to help police forces across the UK and beyond leverage the power of AI-driven community engagement analytics.

**🌟 Star this repository if CoPPA Analytics is helping your police force!**

---

*For technical support, feature requests, or partnership inquiries, please contact the development team or open an issue on GitHub.*
