#!/bin/bash

# CoPPA Analytics - Secondary Deployment Setup Script
# This script helps create a copy of the analytics solution for a different Cosmos database

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to prompt for user input
prompt_input() {
    local prompt="$1"
    local var_name="$2"
    local default_value="$3"
    
    if [ -n "$default_value" ]; then
        read -p "$prompt [$default_value]: " input
        if [ -z "$input" ]; then
            input="$default_value"
        fi
    else
        read -p "$prompt: " input
        while [ -z "$input" ]; do
            print_warning "This field is required."
            read -p "$prompt: " input
        done
    fi
    
    declare -g "$var_name=$input"
}

print_status "=== CoPPA Analytics - Secondary Deployment Setup ==="
echo

# Get deployment type choice
echo "Choose your deployment approach:"
echo "1. Update existing deployment (change environment variables only)"
echo "2. Fork repository for separate deployment (Recommended)"
echo "3. Copy files for separate deployment (Legacy)"
echo "4. Exit"
echo

read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        print_status "Option 1: Updating existing deployment environment variables"
        echo
        print_warning "You'll need to manually update these in Azure Portal:"
        echo "1. Go to your Function App in Azure Portal"
        echo "2. Navigate to Settings → Environment variables"
        echo "3. Update the following variables:"
        echo
        echo "Required updates:"
        
        prompt_input "Secondary Cosmos DB Endpoint" cosmos_endpoint
        prompt_input "Secondary Cosmos DB Key" cosmos_key
        prompt_input "Secondary Database Name" database_name "db_conversation_history"
        prompt_input "Secondary Container Name" container_name "conversations"
        
        echo
        print_success "Environment Variable Updates Needed:"
        echo "COSMOS_DB_ENDPOINT=$cosmos_endpoint"
        echo "COSMOS_DB_KEY=$cosmos_key"
        echo "COSMOS_DB_DATABASE=$database_name"
        echo "COSMOS_DB_CONTAINER=$container_name"
        echo
        print_warning "After updating these variables, restart your Function App for changes to take effect."
        ;;
        
    2)
        print_status "Option 2: Creating separate deployment"
        echo
        
        # Get deployment parameters
        prompt_input "Secondary deployment directory name" target_dir "CoPPA-Analytics-Secondary"
        prompt_input "Force prefix for secondary deployment (e.g., BTP-SEC)" force_prefix
        prompt_input "Admin email for secondary deployment" admin_email
        prompt_input "Secondary Cosmos DB Endpoint" cosmos_endpoint
        prompt_input "Secondary Cosmos DB Key" cosmos_key
        prompt_input "Secondary Database Name" database_name "db_conversation_history"
        prompt_input "Secondary Container Name" container_name "conversations"
        prompt_input "Force Logo URL (optional)" logo_url ""
        
        # Create the directory structure
        print_status "Creating secondary deployment directory: $target_dir"
        
        if [ -d "$target_dir" ]; then
            print_warning "Directory $target_dir already exists. Remove it? (y/N)"
            read -p "" remove_dir
            if [ "$remove_dir" = "y" ] || [ "$remove_dir" = "Y" ]; then
                rm -rf "$target_dir"
                print_success "Removed existing directory"
            else
                print_error "Cannot proceed with existing directory"
                exit 1
            fi
        fi
        
        # Copy the repository structure
        print_status "Copying repository structure..."
        cp -r . "$target_dir"
        cd "$target_dir"
        
        # Remove git history and setup files from the copy
        rm -rf .git
        rm -f setup-secondary-deployment.md
        rm -f setup-secondary.sh
        
        # Create updated ARM template parameters file
        print_status "Creating deployment parameters file..."
        cat > azure-deploy/azuredeploy.parameters.secondary.json << EOF
{
    "\$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentParameters.json#",
    "contentVersion": "1.0.0.0",
    "parameters": {
        "forcePrefix": {
            "value": "$force_prefix"
        },
        "adminEmail": {
            "value": "$admin_email"
        },
        "existingCosmosDbEndpoint": {
            "value": "$cosmos_endpoint"
        },
        "existingCosmosDbKey": {
            "value": "$cosmos_key"
        },
        "cosmosDbDatabase": {
            "value": "$database_name"
        },
        "cosmosDbContainer": {
            "value": "$container_name"
        },
        "forceLogoUrl": {
            "value": "$logo_url"
        }
    }
}
EOF

        # Create deployment script
        print_status "Creating deployment script..."
        cat > azure-deploy/deploy-secondary.sh << 'EOF'
#!/bin/bash

# Deploy secondary CoPPA Analytics instance
set -e

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo "Azure CLI is not installed. Please install it first."
    exit 1
fi

# Check if logged in to Azure
if ! az account show &> /dev/null; then
    echo "Please login to Azure CLI first:"
    echo "az login"
    exit 1
fi

# Get resource group name
read -p "Enter resource group name (will be created if it doesn't exist): " RESOURCE_GROUP
read -p "Enter Azure region (e.g., uksouth, ukwest): " LOCATION

# Create resource group if it doesn't exist
az group create --name "$RESOURCE_GROUP" --location "$LOCATION"

# Deploy ARM template
echo "Deploying CoPPA Analytics Secondary..."
az deployment group create \
    --resource-group "$RESOURCE_GROUP" \
    --template-file azuredeploy.json \
    --parameters @azuredeploy.parameters.secondary.json

echo "Deployment completed!"
echo "Check the Azure Portal for your new Function App and resources."
EOF

        chmod +x azure-deploy/deploy-secondary.sh
        
        # Update README for secondary deployment
        print_status "Creating secondary deployment README..."
        cat > README-SECONDARY.md << EOF
# CoPPA Analytics - Secondary Deployment

This is a secondary deployment of CoPPA Analytics configured to work with a different Cosmos database.

## Configuration

- **Force Prefix**: $force_prefix
- **Cosmos DB Endpoint**: $cosmos_endpoint
- **Database**: $database_name
- **Container**: $container_name

## Deployment

To deploy this secondary instance:

\`\`\`bash
cd azure-deploy
./deploy-secondary.sh
\`\`\`

## Testing

After deployment, your endpoints will be:
- Dashboard: https://func-coppa-$(echo $force_prefix | tr '[:upper:]' '[:lower:]')-analytics.azurewebsites.net/api/Dashboard
- Analytics API: https://func-coppa-$(echo $force_prefix | tr '[:upper:]' '[:lower:]')-analytics.azurewebsites.net/api/GetAnalytics

## Differences from Primary

This deployment uses:
- Different Cosmos DB connection
- Different resource naming (includes $force_prefix)
- Separate Azure resources
- Independent monitoring and logging

## Maintenance

This deployment is independent of the primary CoPPA Analytics deployment. Updates should be applied separately.
EOF

        print_success "Secondary deployment structure created successfully!"
        echo
        print_status "Next steps:"
        echo "1. cd $target_dir"
        echo "2. cd azure-deploy"
        echo "3. ./deploy-secondary.sh"
        echo
        print_warning "Make sure you have Azure CLI installed and are logged in before deploying."
        ;;
        
    3)
        print_status "Exiting..."
        exit 0
        ;;
        
    *)
        print_error "Invalid choice. Please run the script again."
        exit 1
        ;;
esac

print_success "Setup completed!"
