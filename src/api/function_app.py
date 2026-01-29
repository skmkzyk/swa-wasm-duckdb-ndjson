import azure.functions as func
import json
import logging
import os
import re
from datetime import datetime, timedelta, timezone
from azure.storage.blob import BlobServiceClient, BlobSasPermissions, generate_container_sas
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
from typing import List, Dict

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

def get_credential():
    """Get Azure credential for authentication"""
    try:
        # Try Managed Identity first (will work in Azure)
        credential = ManagedIdentityCredential()
        # Test the credential by attempting to get a token
        credential.get_token("https://storage.azure.com/.default")
        logging.info("Using Managed Identity for authentication")
        return credential
    except Exception as e:
        logging.warning(f"Managed Identity not available, falling back to DefaultAzureCredential: {e}")
        # Fallback to DefaultAzureCredential (for local development)
        # This will try various credential types: environment variables, managed identity, 
        # Azure CLI, Azure PowerShell, etc.
        return DefaultAzureCredential()

def get_storage_accounts_from_env() -> List[str]:
    """Get list of storage account names from environment variable"""
    accounts_str = os.environ.get('STORAGE_ACCOUNTS', '')
    if not accounts_str:
        return []
    return [acc.strip() for acc in accounts_str.split(',') if acc.strip()]

def validate_storage_name(name: str, name_type: str = "name") -> bool:
    """
    Validate Azure Storage account or container name.
    
    Rules:
    - Must be 3-63 characters long
    - Must contain only lowercase letters, numbers, and hyphens
    - Cannot start or end with a hyphen
    - Cannot contain consecutive hyphens
    """
    if not name or len(name) < 3 or len(name) > 63:
        return False
    
    # Azure storage names must be lowercase alphanumeric with hyphens
    # Cannot start or end with hyphen, no consecutive hyphens
    pattern = r'^[a-z0-9]([a-z0-9-]*[a-z0-9])?$'
    if not re.match(pattern, name):
        return False
    
    # Check for consecutive hyphens
    if '--' in name:
        return False
    
    return True

@app.route(route="containers", methods=["GET"])
def list_containers(req: func.HttpRequest) -> func.HttpResponse:
    """List all accessible containers from configured storage accounts"""
    logging.info('List containers endpoint was called.')
    
    try:
        # Get storage accounts from environment
        storage_accounts = get_storage_accounts_from_env()
        
        if not storage_accounts:
            logging.warning("No storage accounts configured in STORAGE_ACCOUNTS environment variable")
            return func.HttpResponse(
                json.dumps({
                    "containers": [],
                    "message": "No storage accounts configured. Set STORAGE_ACCOUNTS environment variable."
                }),
                mimetype="application/json",
                status_code=200
            )
        
        credential = get_credential()
        containers = []
        
        # Iterate through all configured storage accounts
        for account_name in storage_accounts:
            try:
                account_url = f"https://{account_name}.blob.core.windows.net"
                blob_service_client = BlobServiceClient(
                    account_url=account_url,
                    credential=credential
                )
                
                # List containers in this storage account
                container_list = blob_service_client.list_containers()
                for container in container_list:
                    containers.append({
                        "name": container.name,
                        "account": account_name,
                        "url": f"{account_url}/{container.name}"
                    })
                    
            except Exception as e:
                logging.warning(f"Failed to list containers from {account_name}: {str(e)}")
                continue
        
        logging.info(f"Found {len(containers)} containers across {len(storage_accounts)} storage accounts")
        
        return func.HttpResponse(
            json.dumps({"containers": containers}),
            mimetype="application/json",
            status_code=200
        )
        
    except Exception as e:
        logging.error(f"Error listing containers: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )

@app.route(route="generate-sas", methods=["POST"])
def generate_sas(req: func.HttpRequest) -> func.HttpResponse:
    """Generate a read-only SAS token for a specific container"""
    logging.info('Generate SAS endpoint was called.')
    
    try:
        # Parse request body
        req_body = req.get_json()
        container_name = req_body.get('container')
        account_name = req_body.get('account')
        
        if not container_name or not account_name:
            return func.HttpResponse(
                json.dumps({"error": "Missing required parameters: container and account"}),
                mimetype="application/json",
                status_code=400
            )
        
        # Validate storage names to prevent injection attacks
        if not validate_storage_name(account_name):
            return func.HttpResponse(
                json.dumps({"error": "Invalid storage account name format"}),
                mimetype="application/json",
                status_code=400
            )
        
        if not validate_storage_name(container_name):
            return func.HttpResponse(
                json.dumps({"error": "Invalid container name format"}),
                mimetype="application/json",
                status_code=400
            )
        
        # Validate that the account is in the allowed list
        allowed_accounts = get_storage_accounts_from_env()
        if allowed_accounts and account_name not in allowed_accounts:
            return func.HttpResponse(
                json.dumps({"error": f"Storage account {account_name} is not configured"}),
                mimetype="application/json",
                status_code=403
            )
        
        credential = get_credential()
        account_url = f"https://{account_name}.blob.core.windows.net"
        
        # Create BlobServiceClient
        blob_service_client = BlobServiceClient(
            account_url=account_url,
            credential=credential
        )
        
        # Get the user delegation key for generating SAS
        key_start_time = datetime.now(timezone.utc)
        key_expiry_time = key_start_time + timedelta(hours=2)
        
        user_delegation_key = blob_service_client.get_user_delegation_key(
            key_start_time=key_start_time,
            key_expiry_time=key_expiry_time
        )
        
        # Generate container SAS token with read and list permissions
        sas_token = generate_container_sas(
            account_name=account_name,
            container_name=container_name,
            user_delegation_key=user_delegation_key,
            permission=BlobSasPermissions(read=True, list=True),
            expiry=datetime.now(timezone.utc) + timedelta(hours=1),
            start=datetime.now(timezone.utc) - timedelta(minutes=5)
        )
        
        container_url = f"{account_url}/{container_name}"
        
        logging.info(f"Generated SAS token for container {container_name} in account {account_name}")
        
        return func.HttpResponse(
            json.dumps({
                "sas_token": sas_token,
                "container_url": container_url,
                "full_url": f"{container_url}?{sas_token}",
                "expiry": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
            }),
            mimetype="application/json",
            status_code=200
        )
        
    except Exception as e:
        logging.error(f"Error generating SAS token: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )
