import azure.functions as func
import os
import json
from azure.cosmos import CosmosClient

def main(req: func.HttpRequest) -> func.HttpResponse:
    title = req.params.get('title')
    if not title:
        return func.HttpResponse("No conversation title provided.", status_code=400)
    endpoint = os.environ.get('COSMOS_DB_ENDPOINT')
    key = os.environ.get('COSMOS_DB_KEY')
    database_name = os.environ.get('COSMOS_DB_DATABASE', 'coppa-db')
    container_name = os.environ.get('COSMOS_DB_CONTAINER', 'questions')
    client = CosmosClient(endpoint, key)
    db = client.get_database_client(database_name)
    container = db.get_container_client(container_name)
    # Find the conversation by title (case-insensitive)
    query = "SELECT * FROM c WHERE LOWER(c.title) = @title"
    items = list(container.query_items(
        query=query,
        parameters=[{"name": "@title", "value": title.lower()}],
        enable_cross_partition_query=True
    ))
    if not items:
        return func.HttpResponse("Conversation not found.", status_code=404)
    conv = items[0]
    html = f"""<html><head><title>{conv.get('title')}</title></head>
    <body>
    <h2>{conv.get('title')}</h2>
    <p><b>User:</b> {conv.get('userId')}</p>
    <p><b>Date:</b> {conv.get('createdAt')}</p>
    <pre>{json.dumps(conv, indent=2)}</pre>
    </body></html>"""
    return func.HttpResponse(html, status_code=200, mimetype='text/html')
