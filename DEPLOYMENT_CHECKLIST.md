# Deployment Checklist for Container Selection Feature

Use this checklist to deploy and configure the new container selection feature.

## Pre-Deployment

- [ ] Review the implementation in this PR
- [ ] Understand the [Container Setup Guide](./CONTAINER_SETUP.md)
- [ ] Ensure you have access to Azure subscription and storage accounts
- [ ] Have Azure CLI installed and authenticated

## Deployment Steps

### 1. Deploy the Application

```bash
# Clone or pull the latest changes
git pull

# Deploy with Azure Developer CLI
azd up
```

**Expected Output:**
- Static Web App URL
- Static Web App Principal ID (save this for step 2)

### 2. Grant Storage Access

For each storage account that contains logs:

```bash
# Set variables
PRINCIPAL_ID="<from-azd-output>"
STORAGE_ACCOUNT="<your-storage-account-name>"
RESOURCE_GROUP="<storage-account-resource-group>"

# Assign Storage Blob Data Reader role
az role assignment create \
  --assignee $PRINCIPAL_ID \
  --role "Storage Blob Data Reader" \
  --scope "/subscriptions/$(az account show --query id -o tsv)/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Storage/storageAccounts/$STORAGE_ACCOUNT"
```

**Verification:**
```bash
# List role assignments
az role assignment list \
  --assignee $PRINCIPAL_ID \
  --scope "/subscriptions/$(az account show --query id -o tsv)/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Storage/storageAccounts/$STORAGE_ACCOUNT"
```

### 3. Configure Storage Accounts Environment Variable

```bash
# Set variables
SWA_NAME="<your-static-web-app-name>"
SWA_RESOURCE_GROUP="<static-web-app-resource-group>"
STORAGE_ACCOUNTS="account1,account2,account3"  # comma-separated

# Set application setting
az staticwebapp appsettings set \
  --name $SWA_NAME \
  --resource-group $SWA_RESOURCE_GROUP \
  --setting-names STORAGE_ACCOUNTS=$STORAGE_ACCOUNTS
```

**Verification:**
```bash
# List application settings
az staticwebapp appsettings list \
  --name $SWA_NAME \
  --resource-group $SWA_RESOURCE_GROUP
```

### 4. Configure CORS on Storage Accounts

For each storage account:

```bash
STORAGE_ACCOUNT="<your-storage-account-name>"

# Add CORS rules
az storage cors add \
  --methods GET HEAD \
  --origins '*' \
  --allowed-headers '*' \
  --exposed-headers '*' \
  --max-age 86400 \
  --services b \
  --account-name $STORAGE_ACCOUNT
```

**For Production:** Replace `'*'` with your Static Web App URL for better security.

**Verification:**
```bash
# List CORS rules
az storage cors list \
  --services b \
  --account-name $STORAGE_ACCOUNT
```

## Post-Deployment Testing

### 1. Test Container Listing

- [ ] Open your Static Web App URL in a browser
- [ ] Open browser DevTools (F12) → Console tab
- [ ] You should see: "Container loading: ..." messages
- [ ] The dropdown should populate with containers or show "No containers available"

**If you see "Failed to load containers":**
- Check that `STORAGE_ACCOUNTS` environment variable is set
- Verify role assignments are in place
- Check Azure Functions logs for errors

### 2. Test SAS Token Generation

- [ ] Select a container from the dropdown
- [ ] Click "Load Today's Logs"
- [ ] You should see: "Generating SAS token..." message
- [ ] Logs should load automatically

**If you see errors:**
- Check browser console for detailed error messages
- Verify CORS is configured on the storage account
- Ensure today's date has log files in `y=YYYY/m=MM/d=DD/` format

### 3. Test API Endpoints Directly

```bash
# Test health endpoint
curl https://your-app-name.azurestaticapps.net/api/health

# Test containers endpoint
curl https://your-app-name.azurestaticapps.net/api/containers

# Test SAS generation (requires POST)
curl -X POST https://your-app-name.azurestaticapps.net/api/generate-sas \
  -H "Content-Type: application/json" \
  -d '{"container":"your-container","account":"your-account"}'
```

## Troubleshooting

### Issue: "No containers available"

**Possible causes:**
1. `STORAGE_ACCOUNTS` not set or empty
2. Managed Identity doesn't have access to storage accounts
3. No containers exist in the storage accounts

**Solutions:**
- Verify environment variable: Check Application Settings in Azure Portal
- Verify role assignments: Use `az role assignment list`
- Check storage accounts: Verify containers exist

### Issue: "Failed to generate SAS"

**Possible causes:**
1. Managed Identity doesn't have sufficient permissions
2. Storage account name not in `STORAGE_ACCOUNTS` list
3. Container doesn't exist

**Solutions:**
- Verify "Storage Blob Data Reader" role is assigned
- Check that account name is in the allowed list
- Verify container exists in the storage account

### Issue: CORS errors in browser

**Symptoms:**
- Browser console shows "CORS policy" errors
- SAS token generated but file loading fails

**Solutions:**
- Configure CORS on storage account (see step 4 above)
- Verify allowed origins include your app URL or '*'
- Check that GET and HEAD methods are allowed

### Issue: "Managed Identity not available"

**Symptoms:**
- API logs show "Using DefaultAzureCredential" in production
- Container listing or SAS generation fails

**Solutions:**
- Verify Managed Identity is enabled on Static Web App
- Check that the identity has been assigned roles
- Wait a few minutes after deployment for identity propagation

## Monitoring

### View Logs

**Application Insights (if configured):**
```bash
az monitor app-insights query \
  --app your-app-insights-name \
  --analytics-query "traces | where message contains 'container' or message contains 'SAS' | order by timestamp desc | take 50"
```

**Azure Portal:**
1. Go to your Static Web App
2. Navigate to "Functions" → "Logs"
3. Monitor for errors or warnings

### Key Metrics to Monitor

- Container listing success rate
- SAS token generation success rate
- Storage access errors
- CORS-related errors

## Rollback Plan

If issues occur:

1. **Disable the feature:**
   ```bash
   az staticwebapp appsettings delete \
     --name $SWA_NAME \
     --resource-group $SWA_RESOURCE_GROUP \
     --setting-names STORAGE_ACCOUNTS
   ```

2. **Revert the deployment:**
   ```bash
   # Deploy previous version
   git checkout <previous-commit>
   azd deploy
   ```

3. **Users can still use:**
   - File upload (drag & drop)
   - Direct URL input with SAS tokens

## Security Notes

- ✅ Managed Identity means no credentials in code or config
- ✅ SAS tokens are read-only (no write/delete permissions)
- ✅ SAS tokens expire after 1 hour
- ✅ Input validation prevents injection attacks
- ✅ Only configured storage accounts can be accessed
- ⚠️ Use specific origins in CORS for production (not '*')

## Support

For issues or questions:
- Review [CONTAINER_SETUP.md](./CONTAINER_SETUP.md) for detailed setup
- Check [README.md](./README.md) for general usage
- Review this PR description for implementation details
- Check Azure portal for service health status

## Success Criteria

✅ The deployment is successful when:
- Container dropdown populates with available containers
- Selecting a container and clicking "Load Today's Logs" works
- Log files load and display in the viewer
- No CORS errors in browser console
- API endpoints respond with valid JSON
