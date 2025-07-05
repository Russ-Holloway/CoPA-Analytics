#!/bin/bash
# CoPPA Analytics Quick Deploy Script for Police Forces
# Run this script to deploy CoPPA Analytics in your Azure tenant

echo "🚔 CoPPA Analytics - Quick Deployment for Police Forces"
echo "=================================================="

# Check if running on Windows (PowerShell) or Linux (Bash)
if command -v pwsh > /dev/null; then
    echo "Using PowerShell..."
    pwsh -File deploy-coppa.ps1
elif command -v az > /dev/null; then
    echo "Using Azure CLI..."
    
    # Prompt for required information
    read -p "Enter your police force code (e.g., BTP, MET, GMP): " FORCE_CODE
    read -p "Enter admin email for reports: " ADMIN_EMAIL
    read -p "Enter Azure region (default: uksouth): " REGION
    REGION=${REGION:-uksouth}
    
    # Create resource group
    RG_NAME="rg-coppa-analytics-$(echo $FORCE_CODE | tr '[:upper:]' '[:lower:]')"
    echo "Creating resource group: $RG_NAME"
    az group create --name $RG_NAME --location $REGION
    
    # Deploy template
    echo "Deploying CoPPA Analytics..."
    az deployment group create \
        --resource-group $RG_NAME \
        --template-uri "https://raw.githubusercontent.com/british-transport-police/AI-Analytics/main/chatbot-analytics-azure-deploy/azuredeploy.json" \
        --parameters forcePrefix=$FORCE_CODE adminEmail=$ADMIN_EMAIL
    
    echo "✅ Deployment complete!"
    echo "Your dashboard: https://func-coppa-$(echo $FORCE_CODE | tr '[:upper:]' '[:lower:]')-analytics.azurewebsites.net/api/Dashboard"
    
else
    echo "❌ Azure CLI not found. Please install Azure CLI first:"
    echo "https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi
