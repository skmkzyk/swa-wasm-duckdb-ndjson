import azure.functions as func
import json
import logging

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="health", methods=["GET"])
def health(req: func.HttpRequest) -> func.HttpResponse:
    """Health check endpoint"""
    logging.info('Health check endpoint was called.')
    
    return func.HttpResponse(
        json.dumps({
            "status": "healthy",
            "message": "NDJSON Log Viewer API is running",
            "version": "1.0.0"
        }),
        mimetype="application/json",
        status_code=200
    )

@app.route(route="info", methods=["GET"])
def info(req: func.HttpRequest) -> func.HttpResponse:
    """Information about the log viewer"""
    logging.info('Info endpoint was called.')
    
    info_data = {
        "name": "NDJSON Log Viewer",
        "description": "Visualize NDJSON logs from App Service using DuckDB WASM",
        "features": [
            "Client-side DuckDB WASM for fast queries",
            "SQL query interface",
            "Drag-and-drop file upload",
            "Statistics and aggregations",
            "Support for App Service console logs"
        ],
        "supported_formats": [".ndjson", ".jsonl"],
        "example_queries": [
            "SELECT * FROM logs ORDER BY time DESC LIMIT 100",
            "SELECT level, COUNT(*) as count FROM logs GROUP BY level",
            "SELECT * FROM logs WHERE level = 'ERROR'"
        ]
    }
    
    return func.HttpResponse(
        json.dumps(info_data, indent=2),
        mimetype="application/json",
        status_code=200
    )
