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
    database_name = os.environ.get('COSMOS_DB_DATABASE', 'db_conversation_history')
    container_name = os.environ.get('COSMOS_DB_CONTAINER', 'Conversations')
    client = CosmosClient(endpoint, key)
    db = client.get_database_client(database_name)
    container = db.get_container_client(container_name)
    query = "SELECT * FROM c WHERE LOWER(c.title) = @title"
    items = list(container.query_items(
        query=query,
        parameters=[{"name": "@title", "value": title.lower()}],
        enable_cross_partition_query=True
    ))
    if not items:
        return func.HttpResponse("<html><body><h2>Conversation not found</h2><p>No conversation found with title: <b>" + title + "</b></p></body></html>", status_code=404, mimetype='text/html')
    conv = items[0]
    html = "<html><head><title>" + (conv.get('title') or '') + "</title>" + \
        "<style>body { font-family: 'Segoe UI', Arial, sans-serif; background: #f8fafc; color: #232946; margin: 0; padding: 32px; }" + \
        ".container { max-width: 700px; margin: 0 auto; background: #fff; border-radius: 14px; box-shadow: 0 4px 24px #1e3a8a22; padding: 32px; }" + \
        "h2 { color: #1e3a8a; margin-top: 0; }" + \
        ".meta { color: #555; font-size: 1em; margin-bottom: 18px; }" + \
        ".section { margin-bottom: 18px; }" + \
        "label { font-weight: bold; }" + \
        "</style></head><body>" + \
        "<div class='container'>" + \
        "<h2>" + (conv.get('title') or '') + "</h2>" + \
        "<div class='meta'><b>Date:</b> " + (conv.get('createdAt') or '') + "</div>" + \
        "<div class='section'><label>Question:</label><br>" + (conv.get('question') or '') + "</div>" + \
        "<div class='section'><label>Answer:</label><br>" + (conv.get('answer') or '') + "</div>" + \
        "<div class='section'><label>Citation:</label><br>" + (conv.get('citation') or '') + "</div>" + \
        "<a href='/api/dashboard'>&larr; Back to Dashboard</a>" + \
        "</div></body></html>"
    return func.HttpResponse(html, status_code=200, mimetype='text/html')
