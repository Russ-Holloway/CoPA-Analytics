import azure.functions as func
import logging
import os
import json
from azure.cosmos import CosmosClient

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        logging.info('GetConversation function processed a request.')
        endpoint = os.environ.get('COSMOS_DB_ENDPOINT')
        key = os.environ.get('COSMOS_DB_KEY')
        database_name = os.environ.get('COSMOS_DB_DATABASE', 'coppa-db')
        container_name = os.environ.get('COSMOS_DB_CONTAINER', 'questions')
        if not endpoint or not key:
            raise Exception('COSMOS_DB_ENDPOINT or COSMOS_DB_KEY environment variable not set')
        client = CosmosClient(endpoint, key)
        db = client.get_database_client(database_name)
        container = db.get_container_client(container_name)
        conversation_id = req.params.get('conversationId')
        if not conversation_id:
            return func.HttpResponse(json.dumps({'error': 'Missing conversationId'}), status_code=400, mimetype='application/json')
        # Query all items with this conversationId or id
        query = "SELECT * FROM c WHERE c.conversationId = @cid OR c.id = @cid"
        items = list(container.query_items(
            query=query,
            parameters=[{"name": "@cid", "value": conversation_id}],
            enable_cross_partition_query=True
        ))
        # Sort by createdAt
        items = sorted(items, key=lambda x: x.get('createdAt') or '')
        return func.HttpResponse(json.dumps({'conversation': items}), status_code=200, mimetype='application/json')
    except Exception as e:
        logging.error(f"GetConversation error: {str(e)}")
        return func.HttpResponse(json.dumps({'error': str(e)}), status_code=500, mimetype='application/json')
