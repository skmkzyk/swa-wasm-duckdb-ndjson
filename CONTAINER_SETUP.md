# Container Listing and SAS Token Setup Guide

This document explains how to configure the Azure Functions backend to enable storage container listing and automatic SAS token generation for loading logs.

## Overview

The application now supports:
- **Container Listing**: Automatically discover storage containers using Managed Identity
- **SAS Token Generation**: Generate read-only, time-limited SAS tokens for secure access
- **Today's Logs Loading**: Automatically load all ndjson.gz files from the current day

## Prerequisites

1. Azure subscription with Static Web App and Storage Account(s)
2. Storage Account(s) containing log files in the format: `y=YYYY/m=MM/d=DD/**/*.ndjson.gz`
3. Azure CLI or Azure Portal access for role assignment

## Deployment Steps

### 1. Deploy the Application

Deploy the application using Azure Developer CLI:

```bash
azd up
```

This will:
- Create the Static Web App with System-Assigned Managed Identity
- Deploy the frontend and API
- Output the Managed Identity's Principal ID

### 2. Grant Storage Access

After deployment, grant the Static Web App's Managed Identity access to your Storage Account(s).

#### Option A: Using Azure Portal

1. Go to your Storage Account in Azure Portal
2. Navigate to **Access Control (IAM)**
3. Click **Add role assignment**
4. Select role: **Storage Blob Data Reader**
5. In the **Members** tab:
   - Select **Managed identity**
   - Click **+ Select members**
   - Choose **Static Web App**
   - Select your deployed app
6. Click **Review + assign**

#### Option B: Using Azure CLI

Replace placeholders with your actual values:

```bash
# Get the Static Web App's Principal ID (output from azd up)
PRINCIPAL_ID="<your-static-web-app-principal-id>"

# Your storage account name
STORAGE_ACCOUNT="<your-storage-account-name>"

# Your resource group containing the storage account
RESOURCE_GROUP="<your-resource-group>"

# Assign the Storage Blob Data Reader role
az role assignment create \
  --assignee $PRINCIPAL_ID \
  --role "Storage Blob Data Reader" \
  --scope "/subscriptions/$(az account show --query id -o tsv)/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Storage/storageAccounts/$STORAGE_ACCOUNT"
```

### 3. Configure Storage Accounts

Set the `STORAGE_ACCOUNTS` environment variable in your Static Web App to specify which storage accounts the API should list containers from.

#### Using Azure Portal

1. Go to your Static Web App in Azure Portal
2. Navigate to **Configuration**
3. Under **Application settings**, add a new setting:
   - **Name**: `STORAGE_ACCOUNTS`
   - **Value**: Comma-separated list of storage account names (e.g., `mystorageaccount1,mystorageaccount2`)
4. Click **Save**

#### Using Azure CLI

```bash
# Your Static Web App name
SWA_NAME="<your-static-web-app-name>"

# Your resource group
RESOURCE_GROUP="<your-resource-group>"

# Comma-separated storage account names
STORAGE_ACCOUNTS="mystorageaccount1,mystorageaccount2"

# Set the application setting
az staticwebapp appsettings set \
  --name $SWA_NAME \
  --resource-group $RESOURCE_GROUP \
  --setting-names STORAGE_ACCOUNTS=$STORAGE_ACCOUNTS
```

### 4. Configure CORS on Storage Accounts

The frontend needs to directly access blob storage using SAS tokens. Configure CORS on each storage account:

#### Using Azure Portal

1. Go to your Storage Account
2. Under **Settings**, select **Resource sharing (CORS)**
3. Add a CORS rule for **Blob service**:
   - **Allowed origins**: `*` (or your Static Web App URL for production)
   - **Allowed methods**: `GET`, `HEAD`
   - **Allowed headers**: `*`
   - **Exposed headers**: `*`
   - **Max age**: `86400`
4. Click **Save**

#### Using Azure CLI

```bash
STORAGE_ACCOUNT="<your-storage-account-name>"

az storage cors add \
  --methods GET HEAD \
  --origins '*' \
  --allowed-headers '*' \
  --exposed-headers '*' \
  --max-age 86400 \
  --services b \
  --account-name $STORAGE_ACCOUNT
```

## Usage

After configuration, the application will:

1. **Load Containers**: On page load, the frontend calls `/api/containers` to get a list of accessible containers
2. **Display Dropdown**: Users see a dropdown with all available containers in the format `account/container`
3. **Generate SAS**: When "Load Today's Logs" is clicked:
   - Frontend calls `/api/generate-sas` with the selected container
   - API generates a read-only SAS token valid for 1 hour
   - Frontend constructs a wildcard URL for today's logs: `y=YYYY/m=MM/d=DD/**/*.ndjson.gz`
4. **Load Logs**: The existing wildcard URL loader fetches and aggregates all matching files

## API Endpoints

### GET /api/containers

Lists all accessible containers from configured storage accounts.

**Response:**
```json
{
  "containers": [
    {
      "name": "logs-container",
      "account": "mystorageaccount",
      "url": "https://mystorageaccount.blob.core.windows.net/logs-container"
    }
  ]
}
```

### POST /api/generate-sas

Generates a read-only SAS token for a specific container.

**Request:**
```json
{
  "container": "logs-container",
  "account": "mystorageaccount"
}
```

**Response:**
```json
{
  "sas_token": "sv=2021-06-08&ss=b&srt=sco&sp=rl&se=...",
  "container_url": "https://mystorageaccount.blob.core.windows.net/logs-container",
  "full_url": "https://mystorageaccount.blob.core.windows.net/logs-container?sv=...",
  "expiry": "2026-01-29T02:00:00"
}
```

## Security Considerations

- **Managed Identity**: No credentials stored in code or configuration
- **Read-Only Access**: SAS tokens only have Read and List permissions
- **Time-Limited**: SAS tokens expire after 1 hour
- **Role-Based**: Uses Azure RBAC for access control
- **Validated Accounts**: API only generates SAS for configured storage accounts

## Troubleshooting

### "No containers available"

- Verify the `STORAGE_ACCOUNTS` environment variable is set
- Check that the Managed Identity has the "Storage Blob Data Reader" role
- Ensure containers exist in the specified storage accounts

### "Failed to generate SAS"

- Verify the Managed Identity has permissions on the storage account
- Check that the storage account name is in the `STORAGE_ACCOUNTS` list
- Review Azure Function logs in Application Insights

### CORS Errors

- Verify CORS is configured on the storage account
- Check that GET and HEAD methods are allowed
- Ensure the origin is allowed (use `*` for testing)

## Local Development

For local development:

1. Install Azure Functions Core Tools
2. Set up Azure CLI authentication: `az login`
3. Create `src/api/local.settings.json`:

```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "STORAGE_ACCOUNTS": "mystorageaccount1,mystorageaccount2"
  }
}
```

4. Start the Functions host:

```bash
cd src/api
func start
```

5. Run the frontend:

```bash
cd src
python -m http.server 8000
```

The API will use `DefaultAzureCredential` which falls back to your Azure CLI credentials.

## References

- [Managed Identities for Azure Resources](https://learn.microsoft.com/entra/identity/managed-identities-azure-resources/)
- [Azure Storage SAS Tokens](https://learn.microsoft.com/azure/storage/common/storage-sas-overview)
- [Azure Static Web Apps Configuration](https://learn.microsoft.com/azure/static-web-apps/configuration)
- [Azure Functions Python Developer Guide](https://learn.microsoft.com/azure/azure-functions/functions-reference-python)
