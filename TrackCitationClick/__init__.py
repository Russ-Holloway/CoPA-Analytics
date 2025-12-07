import azure.functions as func
import logging
import json
import os
from datetime import datetime
from azure.cosmos import CosmosClient

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Track when a user clicks on a citation link.
    Expected POST body: {
        "conversationId": "string",
        "citationTitle": "string",
        "citationUrl": "string",
        "userId": "string",
        "timestamp": "ISO datetime string"
    }
    """
    try:
        logging.info('TrackCitationClick function processed a request.')
        
        # Get request body
        try:
            req_body = req.get_json()
        except ValueError:
            return func.HttpResponse(
                json.dumps({"error": "Invalid JSON in request body"}),
                status_code=400,
                mimetype="application/json"
            )
        
        # Validate required fields
        conversation_id = req_body.get('conversationId')
        citation_title = req_body.get('citationTitle')
        citation_url = req_body.get('citationUrl')
        user_id = req_body.get('userId')
        
        if not conversation_id or not citation_title:
            return func.HttpResponse(
                json.dumps({"error": "conversationId and citationTitle are required"}),
                status_code=400,
                mimetype="application/json"
            )
        
        # Cosmos DB connection
        endpoint = os.environ.get('COSMOS_DB_ENDPOINT')
        key = os.environ.get('COSMOS_DB_KEY')
        # Allow database/container to be specified in request, otherwise use environment defaults
        database_name = req_body.get('databaseName') or os.environ.get('COSMOS_DB_DATABASE', 'coppa-db')
        container_name = req_body.get('containerName') or os.environ.get('COSMOS_DB_CONTAINER', 'questions')
        
        if not endpoint or not key:
            raise Exception('COSMOS_DB_ENDPOINT or COSMOS_DB_KEY environment variable not set')
        
        client = CosmosClient(endpoint, key)
        db = client.get_database_client(database_name)
        container = db.get_container_client(container_name)
        
        # Create citation click event document
        click_event = {
            'id': f"citation-click-{conversation_id}-{datetime.utcnow().timestamp()}",
            'type': 'citation_click',
            'conversationId': conversation_id,
            'citationTitle': citation_title,
            'citationUrl': citation_url or '',
            'userId': user_id or 'anonymous',
            'timestamp': req_body.get('timestamp') or datetime.utcnow().isoformat(),
            'createdAt': datetime.utcnow().isoformat()
        }
        
        # Store in Cosmos DB
        container.create_item(body=click_event)
        
        logging.info(f"Citation click tracked: conversation={conversation_id}, citation={citation_title}")
        
        return func.HttpResponse(
            json.dumps({"status": "success", "message": "Citation click tracked"}),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logging.error(f"TrackCitationClick error: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )
