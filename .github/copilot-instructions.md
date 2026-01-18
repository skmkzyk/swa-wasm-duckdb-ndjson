# GitHub Copilot Instructions for swa-wasm-duckdb-ndjson

This document provides guidance for GitHub Copilot and developers working on the NDJSON Log Viewer project.

## Project Overview

This is a Static Web App that visualizes NDJSON (Newline Delimited JSON) logs using DuckDB WASM. The application is designed to work with logs from Azure App Service console output, particularly those stored by [appsvc-console-to-blob](https://github.com/skmkzyk/appsvc-console-to-blob).

## Architecture Principles

### Core Design
- **Frontend-First**: All log processing happens in the browser using DuckDB WASM
- **No Data Upload**: Files are processed client-side, never uploaded to servers
- **Python API**: Optional backend provides metadata and health endpoints only
- **Infrastructure as Code**: All Azure resources defined in Bicep templates

### Technology Stack
- **Frontend**: Vanilla HTML/CSS/JavaScript with DuckDB WASM (1.28.0)
- **Backend**: Python 3.11+ with Azure Functions v4
- **Infrastructure**: Azure Static Web Apps (Free tier compatible)
- **Deployment**: Azure Developer CLI (azd)

## Code Style and Conventions

### Python Code
- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Keep API functions simple and focused
- Use Azure Functions v4 programming model with decorators
- Always handle errors gracefully with appropriate HTTP status codes

Example:
```python
@app.route(route="endpoint", methods=["GET"])
def endpoint_handler(req: func.HttpRequest) -> func.HttpResponse:
    """Clear docstring explaining the endpoint"""
    try:
        # Implementation
        return func.HttpResponse(json.dumps(data), mimetype="application/json")
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return func.HttpResponse("Error message", status_code=500)
```

### JavaScript Code
- Use modern ES6+ features (async/await, arrow functions, template literals)
- Keep functions small and focused
- Use descriptive variable names
- Always handle promises with try/catch
- Use const by default, let when needed, never var

### HTML/CSS
- Maintain the gradient color scheme (primary: #667eea, secondary: #764ba2)
- Keep responsive design principles
- Use semantic HTML5 elements
- Maintain accessibility (ARIA labels, keyboard navigation)
- CSS should be inline in index.html for simplicity (single-file app)

### Bicep Infrastructure
- Use parameterized templates
- Follow Azure resource abbreviations from abbreviations.json
- Include descriptive comments for complex resources
- Use resource tags for environment identification

## File Organization

```
.
├── .github/
│   └── copilot-instructions.md       # This file
├── infra/                             # Infrastructure as Code
│   ├── main.bicep                    # Main template (don't modify lightly)
│   ├── main.parameters.json          # Deployment parameters
│   ├── abbreviations.json            # Azure naming conventions
│   └── core/host/
│       └── staticwebapp.bicep        # SWA resource definition
├── src/
│   ├── index.html                    # Main application (all-in-one)
│   ├── staticwebapp.config.json      # SWA routing configuration
│   └── api/                          # Python Functions API
│       ├── function_app.py           # API endpoints
│       ├── requirements.txt          # Python dependencies
│       └── host.json                 # Functions configuration
├── azure.yaml                         # azd configuration
├── sample.ndjson                      # Test data
└── README.md                          # Documentation
```

## Development Guidelines

### When Adding Features

1. **Frontend Features** (DuckDB queries, UI improvements):
   - Modify `src/index.html`
   - Test locally with `python -m http.server 8000`
   - Ensure DuckDB WASM version compatibility
   - Update example queries section if adding new query patterns
   - Test with sample.ndjson

2. **Backend API Endpoints**:
   - Add new functions in `src/api/function_app.py`
   - Follow the existing pattern with `@app.route()` decorators
   - Update `README.md` API documentation section
   - Test locally with Azure Functions Core Tools: `func start`
   - Keep endpoints simple - complex logic should be client-side

3. **Infrastructure Changes**:
   - Modify Bicep templates in `infra/` directory
   - Test with `azd provision --preview` before deploying
   - Update `README.md` if new resources are added
   - Consider cost implications of new resources

### Testing Requirements

**Before committing:**
1. Test locally with sample.ndjson file
2. Verify all example queries work correctly
3. Test drag-and-drop file upload
4. Test manual file selection
5. Verify error handling with invalid files
6. Check browser console for errors
7. Test responsive design (mobile/tablet/desktop)

**For API changes:**
1. Test endpoints with curl or Postman
2. Verify JSON responses are valid
3. Test error cases
4. Check logging output

### Common Tasks

#### Adding a New SQL Example Query
1. Open `src/index.html`
2. Find the `.example-queries` section
3. Add a new div with pattern:
```html
<div class="example-query" data-query="YOUR SQL HERE">
    <code>Description of query</code>
</div>
```

#### Adding a New API Endpoint
1. Open `src/api/function_app.py`
2. Add new function:
```python
@app.route(route="yourroute", methods=["GET", "POST"])
def your_handler(req: func.HttpRequest) -> func.HttpResponse:
    # Implementation
    pass
```
3. Update README.md API section

#### Modifying UI Colors/Theme
- Primary gradient: `#667eea` to `#764ba2`
- Keep consistent across all UI elements
- Maintain accessibility contrast ratios

#### Adding New Infrastructure Resources
1. Create/modify Bicep files in `infra/core/`
2. Reference from `infra/main.bicep`
3. Add outputs for important values
4. Update azure.yaml if needed

## DuckDB WASM Specifics

### Important Constraints
- Table is always named `logs` (hardcoded)
- Data loaded via `read_json_auto()` with `format='newline_delimited'`
- DuckDB WASM version pinned to 1.28.0 from jsDelivr CDN
- All SQL runs in browser - no server-side execution

### Working with DuckDB WASM
- Initialize once on page load
- Reuse connection for all queries
- Handle async operations properly
- Memory limits apply (browser dependent)
- Large files (>100MB) may cause performance issues

### Example Query Patterns
```sql
-- Basic filtering
SELECT * FROM logs WHERE level = 'ERROR' LIMIT 100

-- Aggregations
SELECT host, COUNT(*) as count FROM logs GROUP BY host

-- Time-based analysis
SELECT DATE_TRUNC('hour', CAST(time AS TIMESTAMP)) as hour, COUNT(*) 
FROM logs GROUP BY hour ORDER BY hour DESC

-- Multiple conditions
SELECT * FROM logs 
WHERE level IN ('ERROR', 'WARN') 
  AND host LIKE '%example%'
ORDER BY time DESC
```

## Deployment

### Local Testing
```bash
# Frontend only
cd src
python -m http.server 8000
# Visit http://localhost:8000

# With API
cd src/api
func start
# Frontend at http://localhost:7071 (or configure SWA CLI)
```

### Azure Deployment
```bash
# Full deployment
azd up

# Infrastructure only
azd provision

# Code only
azd deploy
```

## Common Issues and Solutions

### Issue: DuckDB fails to initialize
- Check browser console for WASM errors
- Verify CDN accessibility (jsDelivr)
- Ensure modern browser with WASM support
- Check for CSP (Content Security Policy) restrictions

### Issue: File upload fails
- Verify file is valid NDJSON (one JSON per line)
- Check file size (browser memory limits)
- Ensure each line is valid JSON
- Check browser console for parsing errors

### Issue: Query fails
- Verify table name is `logs`
- Check column names match data
- Verify SQL syntax (DuckDB flavor)
- Review error message in UI

### Issue: azd deployment fails
- Verify Azure CLI login: `az account show`
- Check subscription access
- Review Bicep template syntax
- Check resource name availability

## Security Considerations

### Client-Side Security
- All data processing is client-side (no data leaves browser)
- No authentication required for static content
- API endpoints are anonymous (suitable for public info only)

### When Adding Features
- Never store sensitive data in JavaScript
- Don't add endpoints that process user data server-side
- Maintain HTTPS in production
- Follow CORS best practices for APIs
- Validate all inputs client-side

## Performance Guidelines

### Frontend Performance
- Keep index.html as a single file (HTTP/2 friendly)
- Use CDN for DuckDB WASM (don't bundle)
- Lazy load results (already implemented with table scrolling)
- Limit default query results (current: 100 rows)

### Backend Performance
- Keep API responses small
- Use JSON for all API responses
- Implement caching headers where appropriate
- Avoid heavy processing in Azure Functions

## Maintenance

### Dependencies
- **DuckDB WASM**: Check for updates quarterly at https://duckdb.org
- **Azure Functions**: Pin to stable versions
- **Python**: Use LTS versions (currently 3.11+)

### Regular Updates
1. Review DuckDB WASM releases
2. Test with new browser versions
3. Check Azure Static Web Apps platform updates
4. Update README with new features

## Best Practices for AI Assistance

When using GitHub Copilot or similar tools on this project:

1. **Preserve the single-file frontend**: Keep index.html self-contained
2. **Don't add build steps**: This is intentionally a simple, no-build project
3. **Maintain Python simplicity**: API should stay minimal
4. **Follow existing patterns**: Consistency is key
5. **Test with sample.ndjson**: Always verify changes work
6. **Update documentation**: README changes should accompany code changes
7. **Consider Azure costs**: Stick to free/low-cost tiers

## Questions to Ask Before Making Changes

- Does this maintain the "client-side first" philosophy?
- Is this adding unnecessary complexity?
- Can this be done without a build step?
- Does this work with the sample.ndjson file?
- Is the README still accurate?
- Will this work on the Free tier of Static Web Apps?
- Is this following the existing code style?

## Resources

- [DuckDB WASM Documentation](https://duckdb.org/docs/api/wasm)
- [Azure Static Web Apps Docs](https://learn.microsoft.com/azure/static-web-apps/)
- [Azure Functions Python Docs](https://learn.microsoft.com/azure/azure-functions/functions-reference-python)
- [Azure Developer CLI Docs](https://learn.microsoft.com/azure/developer/azure-developer-cli/)
- [NDJSON Specification](http://ndjson.org/)

## Contact

For questions or issues, please refer to:
- GitHub Issues in this repository
- README.md for user documentation
- Azure documentation for platform-specific questions
