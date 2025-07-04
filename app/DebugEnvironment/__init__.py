import logging
import azure.functions as func
import os
import json

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('DebugEnvironment function processed a request.')
    # Example: Return environment variables for debugging
    env_vars = {k: v for k, v in os.environ.items() if k.startswith('COSMOS_DB_') or k.startswith('WEBSITE_') or k.startswith('FUNCTIONS_')}
    debug_info = {
        "environment": env_vars,
        "request_headers": dict(req.headers),
        "method": req.method,
        "params": req.params,
    }
    return func.HttpResponse(
        json.dumps(debug_info, indent=2),
        status_code=200,
        headers={"Content-Type": "application/json"}
    )
