# GitHub Repository URLs to Update

Once your repository is live at `https://github.com/[your-username]/AI-Analytics`, you'll need to update these files:

## Files to Update:

### 1. README.md
Update the "Deploy to Azure" button URL:
```markdown
[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2F[your-username]%2FAI-Analytics%2Fmain%2Fchatbot-analytics-azure-deploy%2Fazuredeploy.json/createUIDefinitionUri/https%3A%2F%2Fraw.githubusercontent.com%2F[your-username]%2FAI-Analytics%2Fmain%2Fchatbot-analytics-azure-deploy%2FcreateUiDefinition.json)
```

### 2. All Documentation Files
Update any GitHub references from:
```
https://github.com/british-transport-police/AI-Analytics
```
To:
```
https://github.com/[your-username]/AI-Analytics
```

### 3. Distribution Materials
Update the repository URLs in:
- POLICE_FORCE_DEPLOYMENT_GUIDE.md
- DISTRIBUTION_EMAIL_TEMPLATE.md
- POLICE_FORCE_PRESENTATION_OUTLINE.md
- deploy-coppa.ps1
- quick-deploy scripts

## Repository Structure Should Be:
```
AI-Analytics/
├── README.md
├── chatbot-analytics-azure-deploy/
│   ├── azuredeploy.json
│   ├── createUiDefinition.json
│   ├── function-code/
│   │   ├── GetAnalytics/
│   │   ├── Dashboard/
│   │   ├── host.json
│   │   └── requirements.txt
│   ├── deploy-coppa.ps1
│   ├── quick-deploy.bat
│   └── quick-deploy.sh
├── POLICE_FORCE_DEPLOYMENT_GUIDE.md
├── DISTRIBUTION_EMAIL_TEMPLATE.md
└── POLICE_FORCE_PRESENTATION_OUTLINE.md
```

## After Repository is Live:

1. **Test the Deploy Button**: Click it to ensure it works
2. **Test Quick Deploy Scripts**: Verify they point to correct URLs
3. **Update Documentation**: Replace placeholder URLs with actual ones
4. **Share with Forces**: Begin distribution to police forces
