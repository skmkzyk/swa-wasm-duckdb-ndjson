# Backend API Deployment Verification

This document explains how to verify that the Azure Functions backend API is correctly deployed with your Static Web App.

## Quick Check

### 1. Test the Health Endpoint

Open your browser and navigate to:
```
https://your-app-name.azurestaticapps.net/api/health
```

**Expected Response (API Working):**
```json
{
  "status": "healthy",
  "message": "NDJSON Log Viewer API is running",
  "version": "1.0.0"
}
```

**Error Response (API Not Deployed):**
```html
<!DOCTYPE html>
<html lang="en">
...
```

If you see HTML instead of JSON, the API is **not deployed**.

### 2. Test the Containers Endpoint

Navigate to:
```
https://your-app-name.azurestaticapps.net/api/containers
```

**Expected Response (API Working, No Storage Configured):**
```json
{
  "containers": [],
  "message": "No storage accounts configured. Set STORAGE_ACCOUNTS environment variable."
}
```

**Expected Response (API Working, With Storage):**
```json
{
  "containers": [
    {
      "name": "container-name",
      "account": "storageaccount",
      "url": "https://storageaccount.blob.core.windows.net/container-name"
    }
  ]
}
```

## Deployment Configuration

### GitHub Actions Workflow

The API deployment is configured in `.github/workflows/azure-static-web-apps-*.yml`:

```yaml
api_location: "./src/api"  # Must point to the API folder
```

**⚠️ Common Issue:** If `api_location` is empty (`""`), the API will **NOT** be deployed!

### Required Files for API Deployment

The API folder must contain:
- `function_app.py` - Azure Functions app with endpoints
- `requirements.txt` - Python dependencies
- `host.json` - Functions runtime configuration

## How to Deploy the Backend

### Option 1: Automatic Deployment (via GitHub Actions)

1. Ensure `api_location: "./src/api"` is set in the workflow file
2. Push changes to the `main` branch
3. GitHub Actions will automatically build and deploy both frontend and API
4. Wait 2-5 minutes for deployment to complete
5. Test the `/api/health` endpoint

### Option 2: Manual Deployment (via Azure CLI)

```bash
# Navigate to project root
cd /path/to/swa-wasm-duckdb-ndjson

# Deploy using Azure Developer CLI
azd deploy

# Or use Static Web Apps CLI
swa deploy --app-location ./src --api-location ./src/api
```

## Monitoring Deployment

### Check GitHub Actions

1. Go to your GitHub repository
2. Click "Actions" tab
3. Check the latest workflow run
4. Look for "Build and Deploy Job"
5. Expand the "Build And Deploy" step
6. Look for API deployment logs:
   ```
   Detecting platforms...
   Detected API language: Python
   Building API...
   ```

### Check Azure Portal

1. Navigate to Azure Portal
2. Go to your Static Web App resource
3. Click "Functions" in the left menu
4. You should see:
   - `health` (GET)
   - `info` (GET)
   - `containers` (GET)
   - `generate-sas` (POST)

If the "Functions" menu shows nothing or "No functions found", the API is not deployed.

## Troubleshooting

### Issue: API Returns HTML Instead of JSON

**Cause:** API not deployed (most common)

**Solution:** 
1. Check `api_location` in GitHub Actions workflow
2. Verify it points to `./src/api`
3. Redeploy

### Issue: API Endpoints Return 404

**Cause:** Incorrect API routing or functions not registered

**Solution:**
1. Check `function_app.py` has `@app.route()` decorators
2. Verify `host.json` is present
3. Check GitHub Actions logs for build errors

### Issue: API Returns 500 Errors

**Cause:** Runtime errors in the API code

**Solution:**
1. Check Application Insights logs in Azure Portal
2. Verify environment variables are set (if using storage)
3. Check Python dependencies in `requirements.txt`

### Issue: Container Loading Says "API Not Available"

This is **expected** if:
- API is not deployed (by design)
- `STORAGE_ACCOUNTS` environment variable is not configured
- Managed Identity doesn't have storage permissions

**This is not an error** - the app works fine without the API. The container loading feature is optional.

## Environment Variables for Full API Functionality

To use the container loading feature, configure in Azure Portal:

1. Go to Static Web App → Configuration
2. Add application settings:
   ```
   STORAGE_ACCOUNTS=storageaccount1,storageaccount2
   ```
3. Ensure Managed Identity has "Storage Blob Data Reader" role on storage accounts

## API Endpoints Reference

| Endpoint | Method | Purpose | Required |
|----------|--------|---------|----------|
| `/api/health` | GET | Health check | No |
| `/api/info` | GET | API information | No |
| `/api/containers` | GET | List storage containers | No |
| `/api/generate-sas` | POST | Generate SAS token | No |

**Note:** All API endpoints are optional. The main app functionality (file upload and SQL queries) works without the API.

## Testing Locally

To test the API locally before deploying:

```bash
# Install Azure Functions Core Tools
# https://learn.microsoft.com/azure/azure-functions/functions-run-local

# Navigate to API folder
cd src/api

# Install dependencies
pip install -r requirements.txt

# Run the API locally
func start

# Test endpoints
curl http://localhost:7071/api/health
curl http://localhost:7071/api/containers
```

## Summary Checklist

- [ ] `api_location: "./src/api"` is set in GitHub Actions workflow
- [ ] Latest commit is deployed (check GitHub Actions)
- [ ] `/api/health` returns JSON (not HTML)
- [ ] Functions appear in Azure Portal
- [ ] Environment variables configured (if using storage)
- [ ] Managed Identity has permissions (if using storage)
