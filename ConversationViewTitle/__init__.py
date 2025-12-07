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
        ".transcript { margin-top: 32px; }" + \
        ".msg-q { background: #e0e7ff; padding: 14px; border-radius: 8px; margin-bottom: 8px; }" + \
        ".msg-a { background: #f0fdf4; padding: 14px; border-radius: 8px; margin-bottom: 8px; }" + \
        ".msg-tool { background: #fef9c3; padding: 14px; border-radius: 8px; margin-bottom: 8px; font-size: 0.97em; color: #7c4700; cursor: pointer; transition: all 0.2s; }" + \
        ".msg-tool:hover { background: #fef08a; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }" + \
        ".msg-role { font-weight: bold; margin-right: 8px; }" + \
        ".citation-title { color: #1e3a8a; font-weight: bold; }" + \
        ".citation-name { color: #1e3a8a; font-weight: bold; }" + \
        ".citation-content { display: block; margin-top: 4px; font-size: 0.97em; color: #333; }" + \
        "</style>" + \
        "<script>" + \
        "async function trackCitationClick(conversationId, citationTitle) {" + \
        "  try {" + \
        "    await fetch('/api/TrackCitationClick', {" + \
        "      method: 'POST'," + \
        "      headers: { 'Content-Type': 'application/json' }," + \
        "      body: JSON.stringify({" + \
        "        conversationId: conversationId," + \
        "        citationTitle: citationTitle," + \
        "        citationUrl: ''," + \
        "        userId: 'viewer'," + \
        "        timestamp: new Date().toISOString()" + \
        "      })" + \
        "    });" + \
        "  } catch (e) { console.error('Citation tracking failed:', e); }" + \
        "}" + \
        "</script></head><body>" + \
        "<div class='container'>" + \
        "<h2>" + (conv.get('title') or '') + "</h2>" + \
        "<div class='meta'><b>Date:</b> " + (conv.get('createdAt') or '') + "</div>" + \
        "<div class='transcript'><h3>Transcript</h3>"

    conversation_id = conv.get('id')
    try:
        messages_query = "SELECT * FROM c WHERE c.conversationId = @cid ORDER BY c.createdAt ASC"
        messages = list(container.query_items(
            query=messages_query,
            parameters=[{"name": "@cid", "value": conversation_id}],
            enable_cross_partition_query=True
        ))
        i = 0
        while i < len(messages):
            msg = messages[i]
            role = msg.get('role', '')
            content = msg.get('content', '')
            if role == 'user':
                html += "<div class='msg-q'><span class='msg-role'>Q:</span> " + content + "</div>"
                next_idx = i + 1
                a_content = None
                citation_htmls = []
                j = next_idx
                while j < len(messages):
                    next_role = messages[j].get('role', '')
                    if next_role == 'assistant' and a_content is None:
                        a_content = messages[j].get('content', '')
                    elif next_role == 'tool':
                        t_content = messages[j].get('content', '')
                        try:
                            tool_data = json.loads(t_content) if isinstance(t_content, str) else t_content
                            citations = tool_data.get('citations') if isinstance(tool_data, dict) else None
                            if citations and isinstance(citations, list):
                                for c in citations:
                                    title = c.get('title', '(citation)')
                                    c_content = c.get('content', '')
                                    title_escaped = title.replace("'", "\\'")
                                    citation_htmls.append("<div class='msg-tool' onclick=\"trackCitationClick('" + conversation_id + "', '" + title_escaped + "')\"><span class='citation-title'>Citation:</span> <span class='citation-name'>" + title + "</span><span class='citation-content'>" + c_content + "</span></div>")
                            else:
                                citation_htmls.append("<div class='msg-tool'>" + t_content + "</div>")
                        except Exception:
                            citation_htmls.append("<div class='msg-tool'>" + t_content + "</div>")
                    elif next_role == 'user':
                        break
                    j += 1
                if a_content is not None:
                    html += "<div class='msg-a'><span class='msg-role'>A:</span> " + a_content + "</div>"
                for c_html in citation_htmls:
                    html += c_html
                i = j
                continue
            elif role == 'assistant':
                html += "<div class='msg-a'><span class='msg-role'>A:</span> " + content + "</div>"
            elif role == 'tool':
                try:
                    tool_data = json.loads(content) if isinstance(content, str) else content
                    citations = tool_data.get('citations') if isinstance(tool_data, dict) else None
                    if citations and isinstance(citations, list):
                        for c in citations:
                            title = c.get('title', '(citation)')
                            c_content = c.get('content', '')
                            title_escaped = title.replace("'", "\\'")
                            html += "<div class='msg-tool' onclick=\"trackCitationClick('" + conversation_id + "', '" + title_escaped + "')\"><span class='citation-title'>Citation:</span> <span class='citation-name'>" + title + "</span><span class='citation-content'>" + c_content + "</span></div>"
                    else:
                        html += "<div class='msg-tool'>" + content + "</div>"
                except Exception:
                    html += "<div class='msg-tool'>" + content + "</div>"
            else:
                html += "<div><span class='msg-role'>" + role + ":</span> " + content + "</div>"
            i += 1
    except Exception as ex:
        html += "<div style='color:red;'>Transcript error: " + str(ex) + "</div>"
    html += "</div></div></body></html>"
    return func.HttpResponse(html, status_code=200, mimetype='text/html')
