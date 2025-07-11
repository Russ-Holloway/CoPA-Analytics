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
        # Step 1: HTML email with all-time metrics (using dummy data for now)
        all_time_total_questions = processed_data['processedRecords']  # Placeholder for dashboard metric
        all_time_unique_users = 42  # Placeholder for dashboard metric
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
            </table>
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
