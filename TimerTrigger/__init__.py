import datetime
import logging
import os
import json
import azure.functions as func

def main(req: func.HttpRequest) -> func.HttpResponse:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()
    logging.info('HTTP-triggered analytics email function called at %s', utc_timestamp)
    force_id = os.environ.get('FORCE_IDENTIFIER', 'unknown')
    try:
        # Simulate analytics processing (as before)
        processed_data = {
            "timestamp": utc_timestamp,
            "forceId": force_id,
            "processedRecords": 1250,
            "summary": {
                "newInteractions": 85,
                "updatedMetrics": True,
                "trendsCalculated": True
            },
            "status": "completed"
        }
        logging.info(f'Analytics processing completed for force: {force_id}')
        logging.info(f'Processed data: {json.dumps(processed_data, indent=2)}')

        # Send daily analytics email using Microsoft Graph API (application permissions)
        import requests
        import msal

        graph_client_id = os.environ.get('GRAPH_CLIENT_ID')
        graph_tenant_id = os.environ.get('GRAPH_TENANT_ID')
        graph_client_secret = os.environ.get('GRAPH_CLIENT_SECRET')
        email_from = os.environ.get('EMAIL_FROM')
        email_to = os.environ.get('EMAIL_TO') or os.environ.get('ADMIN_EMAIL')

        if not all([graph_client_id, graph_tenant_id, graph_client_secret, email_from, email_to]):
            logging.error('Missing Graph API or email environment variables. Email not sent.')
            return func.HttpResponse('Missing Graph API or email environment variables.', status_code=500)

        subject = f"CoPPA Analytics Daily Report - {force_id} - {utc_timestamp[:10]}"
        # Step 6: Add recent conversations list to HTML email (dummy values for now)
        all_time_total_questions = processed_data['processedRecords']  # Placeholder for dashboard metric
        all_time_unique_users = 42  # Placeholder for dashboard metric
        total_user_questions = 17  # Dummy value for selected date range
        unique_users = 5  # Dummy value for selected date range
        top_themes = [
            {"theme": "domestic abuse", "count": 8},
            {"theme": "theft", "count": 6},
            {"theme": "mental health", "count": 5},
            {"theme": "drugs", "count": 4},
            {"theme": "violence", "count": 3}
        ]  # Dummy values for now
        themes_html = "<ul style='margin-top:12px;'>" + "".join([
            f"<li><strong>{t['theme'].title()}</strong>: {t['count']}</li>" for t in top_themes
        ]) + "</ul>"
        recent_by_theme = {
            "domestic abuse": {"title": "Domestic Abuse Support", "createdAt": "2025-07-10T14:22:00"},
            "theft": {"title": "Theft in City Center", "createdAt": "2025-07-10T13:10:00"},
            "mental health": {"title": "Mental Health Resources", "createdAt": "2025-07-09T17:45:00"},
            "drugs": {"title": "Drug Awareness", "createdAt": "2025-07-09T09:30:00"},
            "violence": {"title": "Violence Prevention", "createdAt": "2025-07-08T20:05:00"}
        }
        by_theme_html = "<ul style='margin-top:12px;'>" + "".join([
            f"<li><strong>{theme.title()}</strong>: {info['title']} <span style='color:#888;font-size:0.9em;'>({info['createdAt']})</span></li>" for theme, info in recent_by_theme.items()
        ]) + "</ul>"
        hourly_distribution = [2, 1, 0, 0, 0, 0, 0, 1, 3, 5, 7, 8, 6, 4, 2, 1, 0, 0, 0, 0, 0, 1, 2, 3]
        hours = [f"{h}:00" for h in range(24)]
        hourly_html = "<table style='border-collapse:collapse;margin-top:12px;'><tr>" + "".join([
            f"<th style='padding:4px 8px;background:#e0e7ff;'>{hour}</th>" for hour in hours
        ]) + "</tr><tr>" + "".join([
            f"<td style='padding:4px 8px;text-align:center;'>{count}</td>" for count in hourly_distribution
        ]) + "</tr></table>"
        # Dummy recent conversations list
        recent_questions = [
            {"title": "Domestic Abuse Support", "category": "domestic abuse", "createdAt": "2025-07-10T14:22:00"},
            {"title": "Theft in City Center", "category": "theft", "createdAt": "2025-07-10T13:10:00"},
            {"title": "Mental Health Resources", "category": "mental health", "createdAt": "2025-07-09T17:45:00"},
            {"title": "Drug Awareness", "category": "drugs", "createdAt": "2025-07-09T09:30:00"},
            {"title": "Violence Prevention", "category": "violence", "createdAt": "2025-07-08T20:05:00"}
        ]
        questions_html = "<div style='margin-top:12px;'>" + "".join([
            f"<div style='border-bottom:1px solid #eee;padding:8px 0;'><span style='font-weight:bold;'>{q['title']}</span> <span style='color:#888;font-size:0.9em;'>({q['category'].title()} | {q['createdAt']})</span></div>" for q in recent_questions
        ]) + "</div>"
        body = f"""
        <html>
        <body style='font-family:Segoe UI,Arial,sans-serif;font-size:18px;color:#232946;'>
            <h2>CoPPA Analytics Daily Report for {force_id}</h2>
            <table style='border-collapse:collapse;margin-top:20px;'>
                <tr>
                    <th style='padding:8px 16px;background:#f0f8ff;border-radius:8px 0 0 8px;'>Total Questions (All-Time)</th>
                    <th style='padding:8px 16px;background:#f0f8ff;border-radius:0 8px 8px 0;'>Unique Users (All-Time)</th>
                </tr>
                <tr>
                    <td style='padding:8px 16px;text-align:center;font-weight:bold;'>{all_time_total_questions}</td>
                    <td style='padding:8px 16px;text-align:center;font-weight:bold;'>{all_time_unique_users}</td>
                </tr>
                <tr>
                    <th style='padding:8px 16px;background:#f9fafb;border-radius:8px 0 0 8px;'>Questions in Selected Date Range</th>
                    <th style='padding:8px 16px;background:#f9fafb;border-radius:0 8px 8px 0;'>New Unique Users in Selected Date Range</th>
                </tr>
                <tr>
                    <td style='padding:8px 16px;text-align:center;font-weight:bold;'>{total_user_questions}</td>
                    <td style='padding:8px 16px;text-align:center;font-weight:bold;'>{unique_users}</td>
                </tr>
            </table>
            <h3 style='margin-top:36px;'>Top Conversation Themes</h3>
            {themes_html}
            <h3 style='margin-top:36px;'>Recent Conversations by Theme</h3>
            {by_theme_html}
            <h3 style='margin-top:36px;'>Hourly Distribution</h3>
            {hourly_html}
            <h3 style='margin-top:36px;'>Recent Conversations</h3>
            {questions_html}
            <p style='margin-top:32px;'>Timestamp: {processed_data['timestamp']}</p>
            <p>Status: {processed_data['status']}</p>
            <p style='color:#888;font-size:0.9em;'>This is an automated message. Please do not reply.</p>
        </body>
        </html>
        """

        # Authenticate with Microsoft Graph using client credentials (application permissions)
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
