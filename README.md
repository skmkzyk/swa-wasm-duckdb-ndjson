# SWA WASM DuckDB NDJSON Log Viewer

A Static Web App that uses DuckDB WASM to visualize NDJSON (Newline Delimited JSON) logs from Azure App Service console output.

> **Languages / 言語**: [English](./README.md) | [日本語 (Japanese)](./README-ja.md)

## Overview

This project provides a web-based log viewer that can analyze and visualize NDJSON logs stored by [appsvc-console-to-blob](https://github.com/skmkzyk/appsvc-console-to-blob). The application runs entirely in the browser using DuckDB WASM, providing fast SQL queries on log files without requiring server-side processing.

### Key Features

- **DuckDB WASM Integration**: Client-side SQL database for fast analytical queries
- **Drag & Drop Upload**: Easy file upload interface for NDJSON log files
- **SQL Query Interface**: Write custom SQL queries to analyze your logs
- **Statistics Dashboard**: Auto-generated statistics about your log data
- **Modern UI**: Clean, responsive interface with gradient design
- **No Backend Required**: All processing happens in the browser
- **Python API (Optional)**: Additional Azure Functions endpoints for extensibility

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Static Web App (Azure)                    │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Frontend (index.html)                                        │
│  ├─ DuckDB WASM (from CDN)                                   │
│  ├─ File Upload UI                                           │
│  ├─ SQL Query Interface                                      │
│  └─ Results Visualization                                    │
│                                                               │
│  Backend API (Python - Optional)                             │
│  ├─ /api/health - Health check                              │
│  └─ /api/info - API information                             │
│                                                               │
└─────────────────────────────────────────────────────────────┘
                             ▲
                             │
                    User uploads NDJSON
                             │
                             │
┌─────────────────────────────────────────────────────────────┐
│              Azure Blob Storage (Optional)                   │
│  └─ NDJSON logs from appsvc-console-to-blob                 │
│     └─ Format: YYYY/MM/DD/console.ndjson                    │
└─────────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
.
├── azure.yaml                      # Azure Developer CLI configuration
├── infra/                          # Infrastructure as Code (Bicep)
│   ├── main.bicep                 # Main infrastructure template
│   ├── main.parameters.json       # Parameters for deployment
│   ├── abbreviations.json         # Azure resource naming conventions
│   └── core/
│       └── host/
│           └── staticwebapp.bicep # Static Web App resource definition
├── src/                           # Application source code
│   ├── index.html                 # Main frontend application
│   └── api/                       # Python Azure Functions API
│       ├── function_app.py        # API endpoints
│       ├── requirements.txt       # Python dependencies
│       └── host.json              # Functions runtime configuration
└── README.md                      # This file
```

## Technology Stack

### Frontend
- **HTML5/CSS3/JavaScript**: Core web technologies
- **DuckDB WASM**: In-browser SQL database for log analysis
  - Version: 1.28.0 from jsDelivr CDN
  - Enables SQL queries on NDJSON data client-side
- **Modern CSS**: Gradient backgrounds, flexbox/grid layouts

### Backend (Optional)
- **Python 3.11+**: Azure Functions runtime
- **Azure Functions**: Serverless API endpoints
  - Health check endpoint
  - Information endpoint

### Infrastructure
- **Azure Static Web Apps**: Hosting platform
  - Free tier available
  - Built-in CI/CD with GitHub Actions
  - Global CDN distribution
- **Bicep**: Infrastructure as Code
- **Azure Developer CLI (azd)**: Deployment automation

## Quick Start

### Prerequisites

- [Azure Developer CLI (azd)](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd)
- [Azure Subscription](https://azure.microsoft.com/free/)
- [Git](https://git-scm.com/downloads)
- Modern web browser (Chrome, Firefox, Edge, Safari)

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/skmkzyk/swa-wasm-duckdb-ndjson.git
   cd swa-wasm-duckdb-ndjson
   ```

2. **Test locally with a simple HTTP server**
   ```bash
   # Using Python
   cd src
   python -m http.server 8000
   
   # OR using Node.js
   npx http-server src -p 8000
   ```

3. **Open in browser**
   ```
   http://localhost:8000
   ```

### Deploy to Azure

Deploy everything with a single command:

```bash
azd up
```

This will:
1. Prompt for Azure subscription and location
2. Create an Azure resource group
3. Deploy the Static Web App infrastructure
4. Build and deploy the application
5. Output the deployed URL

### Manual Deployment Steps

If you prefer manual deployment:

1. **Initialize azd environment**
   ```bash
   azd init
   ```

2. **Provision infrastructure**
   ```bash
   azd provision
   ```

3. **Deploy application**
   ```bash
   azd deploy
   ```

## Using the Log Viewer

### 1. Load NDJSON Logs

**Option A: Upload Local File**
- **Drag and Drop**: Drag your `.ndjson`, `.jsonl`, or `.gz` file onto the upload area
- **Click to Browse**: Click the upload area to select a file from your computer

**Option B: Load from Azure Blob Storage**
- Enter the full blob URL in the URL input field
- Supports both plain and gzip-compressed files (`.ndjson.gz`)
- Example: `https://storageaccount.blob.core.windows.net/logs-container/y=2026/m=01/d=10/h=08/m=00/p=00/part-*.ndjson.gz`
- Click "Load from URL" or press Enter

### 2. Supported Log Format

The viewer expects NDJSON format where each line is a valid JSON object:

```json
{"time": "2026-01-10T12:34:56Z", "level": "INFO", "message": "Request received", "host": "example.com"}
{"time": "2026-01-10T12:34:57Z", "level": "ERROR", "message": "Connection timeout", "host": "example.com"}
{"time": "2026-01-10T12:34:58Z", "level": "INFO", "message": "Response sent", "host": "example.com"}
```

This format is automatically generated by [appsvc-console-to-blob](https://github.com/skmkzyk/appsvc-console-to-blob).

### 3. Query Your Logs

Use SQL to query your logs. Example queries:

**Get latest 100 entries:**
```sql
SELECT * FROM logs ORDER BY time DESC LIMIT 100
```

**Count logs by level:**
```sql
SELECT level, COUNT(*) as count 
FROM logs 
GROUP BY level 
ORDER BY count DESC
```

**Find all errors:**
```sql
SELECT * FROM logs 
WHERE level = 'ERROR' 
ORDER BY time DESC
```

**Analyze by host:**
```sql
SELECT host, COUNT(*) as count 
FROM logs 
GROUP BY host 
ORDER BY count DESC
```

**Time-based analysis:**
```sql
SELECT DATE_TRUNC('hour', CAST(time AS TIMESTAMP)) as hour, 
       COUNT(*) as count 
FROM logs 
GROUP BY hour 
ORDER BY hour DESC
```

### 4. View Results

Results are displayed in a scrollable table with:
- Column headers from your log data
- Sortable and searchable (via SQL)
- Statistics summary (total records, fields, etc.)

## API Endpoints

The Python API provides optional backend endpoints:

### GET /api/health
Health check endpoint to verify API is running.

**Response:**
```json
{
  "status": "healthy",
  "message": "NDJSON Log Viewer API is running",
  "version": "1.0.0"
}
```

### GET /api/info
Information about the application and example queries.

**Response:**
```json
{
  "name": "NDJSON Log Viewer",
  "description": "Visualize NDJSON logs from App Service using DuckDB WASM",
  "features": [...],
  "supported_formats": [".ndjson", ".jsonl"],
  "example_queries": [...]
}
```

## Use Cases

1. **App Service Log Analysis**: Analyze console logs from Azure App Service
2. **Error Investigation**: Query and filter error logs quickly
3. **Performance Analysis**: Aggregate logs by time periods
4. **Host-based Analysis**: Group logs by FQDN or host
5. **Custom Metrics**: Write SQL queries for custom aggregations

## Security Considerations

- **Client-Side Processing**: All log data stays in your browser
- **No Server Upload**: Files are processed locally, not uploaded to servers
- **CORS**: Properly configured for Azure Static Web Apps
- **HTTPS**: Automatically enabled in Azure deployment

## Development

### Testing with Sample Data

Create a sample NDJSON file for testing:

```bash
cat > sample.ndjson << 'EOF'
{"time": "2026-01-10T10:00:00Z", "level": "INFO", "message": "Application started", "host": "app1.example.com"}
{"time": "2026-01-10T10:00:01Z", "level": "INFO", "message": "Request received", "host": "app1.example.com"}
{"time": "2026-01-10T10:00:02Z", "level": "ERROR", "message": "Database connection failed", "host": "app1.example.com"}
{"time": "2026-01-10T10:00:03Z", "level": "WARN", "message": "Retry attempt 1", "host": "app1.example.com"}
{"time": "2026-01-10T10:00:05Z", "level": "INFO", "message": "Connection established", "host": "app1.example.com"}
{"time": "2026-01-10T10:01:00Z", "level": "INFO", "message": "Processing request", "host": "app2.example.com"}
{"time": "2026-01-10T10:01:30Z", "level": "ERROR", "message": "Timeout occurred", "host": "app2.example.com"}
EOF
```

### Extending the Application

**Add new Python API endpoints:**
1. Edit `src/api/function_app.py`
2. Add new route with `@app.route()`
3. Deploy with `azd deploy`

**Customize the UI:**
1. Edit `src/index.html`
2. Modify CSS in the `<style>` section
3. Update JavaScript in the `<script>` module

**Modify Infrastructure:**
1. Edit Bicep files in `infra/` directory
2. Provision with `azd provision`

## Environment Variables

For local API development, create `src/api/local.settings.json`:

```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "",
    "FUNCTIONS_WORKER_RUNTIME": "python"
  }
}
```

## CI/CD

Azure Static Web Apps automatically sets up GitHub Actions for CI/CD when deployed via `azd up`. The workflow:

1. Triggers on push to main branch
2. Builds the application
3. Deploys to Azure Static Web Apps
4. Deploys Python API as Azure Functions

## Troubleshooting

### Issue: "Failed to initialize DuckDB"
- **Solution**: Ensure you're using a modern browser with WebAssembly support
- Check browser console for detailed errors

### Issue: "File parsing failed"
- **Solution**: Verify your file is valid NDJSON (one JSON object per line)
- Check that each line is valid JSON

### Issue: "Query execution failed"
- **Solution**: Verify SQL syntax
- Check that column names match your data
- Remember the table is always named `logs`

### Issue: "azd up fails"
- **Solution**: Ensure you have Azure CLI and azd installed
- Verify you're logged in: `azd auth login`
- Check Azure subscription: `az account show`

## References

- [DuckDB WASM Documentation](https://duckdb.org/docs/api/wasm)
- [Azure Static Web Apps Documentation](https://learn.microsoft.com/azure/static-web-apps/)
- [Azure Developer CLI Documentation](https://learn.microsoft.com/azure/developer/azure-developer-cli/)
- [App Service Console to Blob](https://github.com/skmkzyk/appsvc-console-to-blob)
- [NDJSON Format Specification](http://ndjson.org/)

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Authors

- **skmkzyk** - Initial work and App Service log collection

## Acknowledgments

- DuckDB team for the excellent WASM implementation
- Azure Static Web Apps team for the hosting platform
- App Service team for diagnostic logging capabilities