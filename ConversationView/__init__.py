import azure.functions as func
import os
import json
from azure.cosmos import CosmosClient

def main(req: func.HttpRequest) -> func.HttpResponse:
    title = req.params.get('title')
    if not title:
        return func.HttpResponse("<html><body><h2>Error: No conversation title provided.</h2><p>Please specify a conversation title in the URL, e.g. <code>?title=YourTitle</code>.</p></body></html>", status_code=400, mimetype='text/html')
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
        return func.HttpResponse(f"<html><body><h2>Conversation not found</h2><p>No conversation found with title: <b>{title}</b></p></body></html>", status_code=404, mimetype='text/html')
    conv = items[0]
    html = f"""<html><head><title>{conv.get('title')}</title></head>
    <body>
    <h2>{conv.get('title')}</h2>
    <p><b>User:</b> {conv.get('userId')}</p>
    <p><b>Date:</b> {conv.get('createdAt')}</p>
    <pre>{json.dumps(conv, indent=2)}</pre>
    """
    # --- Minimal transcript section below JSON ---
    conversation_id = conv.get('id')
    html += "<hr><div><b>Transcript:</b><br>"
    try:
        messages_query = "SELECT * FROM c WHERE c.conversationId = @cid ORDER BY c.createdAt ASC"
        messages = list(container.query_items(
            query=messages_query,
            parameters=[{"name": "@cid", "value": conversation_id}],
            enable_cross_partition_query=True
        ))
        for msg in messages:
            html += f"<div><b>{msg.get('role','')}</b>: {msg.get('content','')}</div>"
    except Exception as ex:
        html += f"<div style='color:red;'>Transcript error: {str(ex)}</div>"
    html += "</div></body></html>"
    return func.HttpResponse(html, status_code=200, mimetype='text/html')
