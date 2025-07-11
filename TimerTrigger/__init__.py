import datetime
import logging
import os
import json
import azure.functions as func
from azure.cosmos import CosmosClient

def main(req: func.HttpRequest) -> func.HttpResponse:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()
    logging.info('HTTP-triggered analytics email function called at %s', utc_timestamp)
    force_id = os.environ.get('FORCE_IDENTIFIER', 'unknown')
    try:
        import requests
        import msal
        # Cosmos DB config (same as dashboard/GetAnalytics)
        endpoint = os.environ.get('COSMOS_DB_ENDPOINT')
        key = os.environ.get('COSMOS_DB_KEY')
        database_name = os.environ.get('COSMOS_DB_DATABASE', 'coppa-db')
        container_name = os.environ.get('COSMOS_DB_CONTAINER', 'questions')
        if not endpoint or not key:
            raise Exception('COSMOS_DB_ENDPOINT or COSMOS_DB_KEY environment variable not set')
        client = CosmosClient(endpoint, key)
        db = client.get_database_client(database_name)
        container = db.get_container_client(container_name)

        # Query all items (all-time)
        query = "SELECT * FROM c"
        items = list(container.query_items(query=query, enable_cross_partition_query=True))
        # All-time metrics
        all_time_total_questions = sum(1 for item in items if item.get('role') == 'user')
        all_time_unique_users = len(set(item.get('userId') for item in items if item.get('role') == 'user' and item.get('userId')))

        # Date range: last 7 days
        from datetime import datetime, timedelta
        now = datetime.utcnow()
        start_dt = now - timedelta(days=7)
        end_dt = now
        def in_range(item):
            ts = item.get('createdAt') or item.get('timestamp')
            if not ts:
                return False
            try:
                dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                return start_dt <= dt <= end_dt
            except Exception:
                return False
        filtered_items = [item for item in items if in_range(item)]

        # Metrics for selected date range
        total_user_questions = sum(1 for item in filtered_items if item.get('role') == 'user')
        unique_users = len(set(item.get('userId') for item in filtered_items if item.get('role') == 'user' and item.get('userId')))

        # Top themes (by keyword in title)
        from collections import Counter
        theme_keywords = [
            'stalking', 'domestic abuse', 'warrant', 'warrants', 'theft', 'burglary', 'assault',
            'missing', 'runaway', 'violence', 'abuse', 'drugs', 'alcohol', 'mental health',
            'child', 'safeguarding', 'investigation', 'arrest', 'bail', 'custody', 'suicide',
            'complaint', 'noise', 'property', 'traffic', 'crime', 'enquiry', 'lost', 'report',
        ]
        themes = Counter()
        for item in filtered_items:
            title = (item.get('title') or '').lower()
            found_themes = [kw for kw in theme_keywords if kw in title]
            for theme in found_themes:
                themes[theme] += 1
        top_themes = [{'theme': k, 'count': v} for k, v in themes.most_common(5)]
        themes_html = "<ul style='margin:0 0 0 28px;'>" + "".join([
            f"<li><span style='color:#1e3a8a;font-weight:bold;'>{t['theme'].title()}</span>: <span style='color:#2563eb;font-weight:bold;'>{t['count']}</span></li>" for t in top_themes
        ]) + "</ul>"

        # Recent conversations by theme
        recent_by_theme = {}
        for t in top_themes:
            theme = t['theme']
            for item in filtered_items:
                title = (item.get('title') or '').lower()
                if theme in title:
                    recent_by_theme[theme] = {
                        "title": item.get('title'),
                        "createdAt": item.get('createdAt')
                    }
                    break
        by_theme_html = "<ul class='by-theme-list' style='margin:0 0 0 28px;'>" + "".join([
            f"<li><strong style='color:#1e3a8a;'>{theme.title()}</strong>: {info['title']} <span style='color:#888;font-size:0.95em;'>({info['createdAt']})</span></li>" for theme, info in recent_by_theme.items()
        ]) + "</ul>"

        # Hourly distribution
        hourly_distribution = [0]*24
        for item in filtered_items:
            ts = item.get('createdAt') or item.get('timestamp')
            if ts:
                try:
                    dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                    hourly_distribution[dt.hour] += 1
                except Exception:
                    pass
        hours = [f"{h}:00" for h in range(24)]
        hourly_html = "<table style='width:100%;border-collapse:separate;border-spacing:0;margin-bottom:24px;background:#f0f4ff;border-radius:10px;overflow:hidden;box-shadow:0 1px 4px #e0e7ff33;'><tr>" + "".join([
            f"<th style='padding:8px 10px;background:#dbeafe;color:#1e3a8a;font-weight:bold;'>{hour}</th>" for hour in hours
        ]) + "</tr><tr style='background:#fff;'>" + "".join([
            f"<td style='padding:8px 10px;text-align:center;font-size:1em;'>{count}</td>" for count in hourly_distribution
        ]) + "</tr></table>"

        # Recent conversations list
        recent_questions = [
            {
                "title": item.get('title') or item.get('question'),
                "category": item.get('category') or '',
                "createdAt": item.get('createdAt')
            }
            for item in sorted(filtered_items, key=lambda x: x.get('createdAt') or '', reverse=True)[:5]
        ]
        questions_html = "<ul class='recent-list' style='margin:0;padding:0;list-style:none;'>" + "".join([
            f"<li class='recent-item' style='border-bottom:1px solid #e0e7ff;padding:14px 0;'><a href='#' style='color:#1e3a8a;text-decoration:none;font-weight:bold;'>{q['title']}</a> <span class='recent-meta' style='color:#666;font-size:0.98em;margin-left:8px;'>[{q['category'].title()} | {q['createdAt']}]</span></li>" for q in recent_questions
        ]) + "</ul>"

        processed_data = {
            "timestamp": utc_timestamp,
            "forceId": force_id,
            "status": "completed"
        }

        graph_client_id = os.environ.get('GRAPH_CLIENT_ID')
        graph_tenant_id = os.environ.get('GRAPH_TENANT_ID')
        graph_client_secret = os.environ.get('GRAPH_CLIENT_SECRET')
        email_from = os.environ.get('EMAIL_FROM')
        email_to = os.environ.get('EMAIL_TO') or os.environ.get('ADMIN_EMAIL')
        if not all([graph_client_id, graph_tenant_id, graph_client_secret, email_from, email_to]):
            logging.error('Missing Graph API or email environment variables. Email not sent.')
            return func.HttpResponse('Missing Graph API or email environment variables.', status_code=500)
        subject = f"CoPPA Analytics Daily Report - {force_id} - {utc_timestamp[:10]}"
        body = f"""
        <html>
        <head>
        <style>
            body {{ font-family: 'Inter', 'Segoe UI', Arial, sans-serif; background: #f6f8fb; color: #232946; margin: 0; padding: 32px; }}
            .report-title {{ font-size: 2.2em; font-weight: bold; margin-bottom: 24px; color: #1e3a8a; letter-spacing: 0.5px; }}
            .metrics-table {{ width: 100%; border-collapse: separate; border-spacing: 0; margin-bottom: 24px; background: #f8fbff; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px #e0e7ff55; }}
            .metrics-table th, .metrics-table td {{ border: none; padding: 16px 24px; text-align: center; font-size: 1.1em; }}
            .metrics-table th {{ background: #e0e7ff; color: #1e3a8a; font-weight: bold; }}
            .metrics-table tr:not(:last-child) td {{ border-bottom: 1px solid #e0e7ff; }}
            .metric-key {{ color: #1e3a8a; font-weight: bold; font-size: 1.2em; }}
            .metric-value {{ color: #2563eb; font-size: 1.4em; font-weight: bold; }}
            .section-title {{ font-size: 1.25em; font-weight: bold; margin: 36px 0 14px 0; color: #1e3a8a; letter-spacing: 0.2px; }}
            ul {{ margin: 0 0 0 28px; }}
            .by-theme-list {{ margin-bottom: 0; }}
            .by-theme-list strong {{ color: #1e3a8a; }}
            .hourly-table {{ width: 100%; border-collapse: separate; border-spacing: 0; margin-bottom: 24px; background: #f0f4ff; border-radius: 10px; overflow: hidden; box-shadow: 0 1px 4px #e0e7ff33; }}
            .hourly-table th, .hourly-table td {{ border: none; padding: 8px 10px; text-align: center; font-size: 1em; }}
            .hourly-table th {{ background: #dbeafe; color: #1e3a8a; font-weight: bold; }}
            .hourly-table tr:not(:last-child) td {{ border-bottom: 1px solid #e0e7ff; }}
            .recent-list {{ margin: 0; padding: 0; list-style: none; }}
            .recent-item {{ border-bottom: 1px solid #e0e7ff; padding: 14px 0; transition: background 0.15s; }}
            .recent-item:last-child {{ border-bottom: none; }}
            .recent-item a {{ color: #1e3a8a; text-decoration: none; font-weight: bold; transition: color 0.15s; }}
            .recent-item a:hover {{ text-decoration: underline; color: #2563eb; }}
            .recent-meta {{ color: #666; font-size: 0.98em; margin-left: 8px; }}
        </style>
        </head>
        <body>
            <div class='report-title'>CoPPA Analytics Daily Report for {force_id}</div>
            <table class='metrics-table'>
                <tr><th class='metric-key'>Total Questions (All-Time)</th><th class='metric-key'>Unique Users (All-Time)</th></tr>
                <tr><td class='metric-value'>{all_time_total_questions}</td><td class='metric-value'>{all_time_unique_users}</td></tr>
            </table>
            <table class='metrics-table'>
                <tr><th class='metric-key'>Questions in Selected Date Range</th><th class='metric-key'>New Unique Users in Selected Date Range</th></tr>
                <tr><td class='metric-value'>{total_user_questions}</td><td class='metric-value'>{unique_users}</td></tr>
            </table>
            <div class='section-title'>Top Conversation Themes</div>
            {themes_html}
            <div class='section-title'>Recent Conversations by Theme</div>
            {by_theme_html}
            <div class='section-title'>Hourly Distribution</div>
            {hourly_html}
            <div class='section-title'>Recent Conversations</div>
            {questions_html}
            <p style='margin-top:32px;'>Timestamp: {processed_data['timestamp']}</p>
            <p>Status: {processed_data['status']}</p>
            <p style='color:#888;font-size:0.9em;'>This is an automated message. Please do not reply.</p>
        </body>
        </html>
        """
        authority = f"https://login.microsoftonline.com/{graph_tenant_id}"
        app = msal.ConfidentialClientApplication(
            graph_client_id,
            authority=authority,
            client_credential=graph_client_secret
        )
        scopes = ["https://graph.microsoft.com/.default"]
        result = app.acquire_token_for_client(scopes=scopes)
        if "access_token" not in result:
            logging.error(f"Failed to obtain access token: {result.get('error_description')}")
            return func.HttpResponse(f"Failed to obtain access token: {result.get('error_description')}", status_code=500)
        access_token = result["access_token"]
        graph_url = f"https://graph.microsoft.com/v1.0/users/{email_from}/sendMail"
        email_payload = {
            "message": {
                "subject": subject,
                "body": {
                    "contentType": "HTML",
                    "content": body
                },
                "toRecipients": [
                    {"emailAddress": {"address": email_to}}
                ]
            },
            "saveToSentItems": "true"
        }
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        response = requests.post(graph_url, headers=headers, json=email_payload)
        if response.status_code == 202:
            logging.info(f"Analytics email sent to {email_to} via Microsoft Graph API.")
            return func.HttpResponse(f"Analytics email sent to {email_to} via Microsoft Graph API.", status_code=200)
        else:
            logging.error(f"Failed to send email: {response.text}")
            return func.HttpResponse(f"Failed to send email: {response.text}", status_code=500)
    except Exception as e:
        logging.error(f"Error in analytics email function: {str(e)}")
        return func.HttpResponse(f"Error in analytics email function: {str(e)}", status_code=500)

# --- Cosmos DB connection setup (step 1: do not use for metrics yet) ---
cosmos_endpoint = os.environ.get('COSMOS_DB_ENDPOINT')
cosmos_key = os.environ.get('COSMOS_DB_KEY')
database_name = os.environ.get('COSMOS_DB_DATABASE', 'coppa-db')
container_name = os.environ.get('COSMOS_DB_CONTAINER', 'questions')
cosmos_connected = False
if cosmos_endpoint and cosmos_key:
    try:
        cosmos_client = CosmosClient(cosmos_endpoint, cosmos_key)
        db = cosmos_client.get_database_client(database_name)
        container = db.get_container_client(container_name)
        cosmos_connected = True
        logging.info('Successfully connected to Cosmos DB.')
    except Exception as e:
        logging.error(f'Cosmos DB connection failed: {e}')
else:
    logging.warning('Cosmos DB endpoint/key not set in environment.')
# --- End Cosmos DB connection setup ---

# --- Step 2: Count all documents in Cosmos DB and log the result (do not use in email) ---
if cosmos_connected:
    try:
        query = "SELECT VALUE COUNT(1) FROM c"
        count_result = list(container.query_items(query=query, enable_cross_partition_query=True))
        total_docs = count_result[0] if count_result else 0
        logging.info(f"Cosmos DB: Total documents in container: {total_docs}")
    except Exception as e:
        logging.error(f"Cosmos DB count query failed: {e}")
# --- End step 2 ---

# Use live Cosmos DB count for all_time_total_questions (step 3)
if cosmos_connected:
    try:
        all_time_total_questions = total_docs
    except Exception as e:
        logging.error(f'Failed to set all_time_total_questions from Cosmos DB: {e}')
        all_time_total_questions = 1250  # fallback dummy value
else:
    all_time_total_questions = 1250  # fallback dummy value

# --- Step 4: Update the email body to use the live count (modify the body HTML) ---
        body = f"""
        <html>
        <head>
        <style>
            body {{ font-family: 'Inter', 'Segoe UI', Arial, sans-serif; background: #f6f8fb; color: #232946; margin: 0; padding: 32px; }}
            .report-title {{ font-size: 2.2em; font-weight: bold; margin-bottom: 24px; color: #1e3a8a; letter-spacing: 0.5px; }}
            .metrics-table {{ width: 100%; border-collapse: separate; border-spacing: 0; margin-bottom: 24px; background: #f8fbff; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px #e0e7ff55; }}
            .metrics-table th, .metrics-table td {{ border: none; padding: 16px 24px; text-align: center; font-size: 1.1em; }}
            .metrics-table th {{ background: #e0e7ff; color: #1e3a8a; font-weight: bold; }}
            .metrics-table tr:not(:last-child) td {{ border-bottom: 1px solid #e0e7ff; }}
            .metric-key {{ color: #1e3a8a; font-weight: bold; font-size: 1.2em; }}
            .metric-value {{ color: #2563eb; font-size: 1.4em; font-weight: bold; }}
            .section-title {{ font-size: 1.25em; font-weight: bold; margin: 36px 0 14px 0; color: #1e3a8a; letter-spacing: 0.2px; }}
            ul {{ margin: 0 0 0 28px; }}
            .by-theme-list {{ margin-bottom: 0; }}
            .by-theme-list strong {{ color: #1e3a8a; }}
            .hourly-table {{ width: 100%; border-collapse: separate; border-spacing: 0; margin-bottom: 24px; background: #f0f4ff; border-radius: 10px; overflow: hidden; box-shadow: 0 1px 4px #e0e7ff33; }}
            .hourly-table th, .hourly-table td {{ border: none; padding: 8px 10px; text-align: center; font-size: 1em; }}
            .hourly-table th {{ background: #dbeafe; color: #1e3a8a; font-weight: bold; }}
            .hourly-table tr:not(:last-child) td {{ border-bottom: 1px solid #e0e7ff; }}
            .recent-list {{ margin: 0; padding: 0; list-style: none; }}
            .recent-item {{ border-bottom: 1px solid #e0e7ff; padding: 14px 0; transition: background 0.15s; }}
            .recent-item:last-child {{ border-bottom: none; }}
            .recent-item a {{ color: #1e3a8a; text-decoration: none; font-weight: bold; transition: color 0.15s; }}
            .recent-item a:hover {{ text-decoration: underline; color: #2563eb; }}
            .recent-meta {{ color: #666; font-size: 0.98em; margin-left: 8px; }}
        </style>
        </head>
        <body>
            <div class='report-title'>CoPPA Analytics Daily Report for {force_id}</div>
            <table class='metrics-table'>
                <tr><th class='metric-key'>Total Questions (All-Time)</th><th class='metric-key'>Unique Users (All-Time)</th></tr>
                <tr><td class='metric-value'>{all_time_total_questions}</td><td class='metric-value'>{all_time_unique_users}</td></tr>
            </table>
            <table class='metrics-table'>
                <tr><th class='metric-key'>Questions in Selected Date Range</th><th class='metric-key'>New Unique Users in Selected Date Range</th></tr>
                <tr><td class='metric-value'>{total_user_questions}</td><td class='metric-value'>{unique_users}</td></tr>
            </table>
            <div class='section-title'>Top Conversation Themes</div>
            {themes_html}
            <div class='section-title'>Recent Conversations by Theme</div>
            {by_theme_html}
            <div class='section-title'>Hourly Distribution</div>
            {hourly_html}
            <div class='section-title'>Recent Conversations</div>
            {questions_html}
            <p style='margin-top:32px;'>Timestamp: {processed_data['timestamp']}</p>
            <p>Status: {processed_data['status']}</p>
            <p style='color:#888;font-size:0.9em;'>This is an automated message. Please do not reply.</p>
        </body>
        </html>
        """
