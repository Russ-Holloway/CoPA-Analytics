import datetime
import logging
import os
import json
import azure.functions as func
from azure.cosmos import CosmosClient, exceptions

def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    logging.info('Python timer trigger function ran at %s', utc_timestamp)
    logging.info('TimerTrigger function ran at %s', mytimer.schedule_status.last)

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

        # Send daily analytics email using Office365 SMTP
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        smtp_server = os.environ.get('SMTP_SERVER', 'smtp.office365.com')
        smtp_port = int(os.environ.get('SMTP_PORT', '587'))
        smtp_user = os.environ.get('EMAIL_USERNAME')
        smtp_pass = os.environ.get('EMAIL_PASSWORD')
        email_to = os.environ.get('EMAIL_TO', os.environ.get('ADMIN_EMAIL'))
        email_from = os.environ.get('EMAIL_FROM', smtp_user)

        if not all([smtp_user, smtp_pass, email_to, email_from]):
            logging.error('Missing SMTP or email environment variables. Email not sent.')
            return

        subject = f"CoPPA Analytics Daily Report - {force_id} - {utc_timestamp[:10]}"
        body = f"""
Hello,

This is your automated CoPPA Analytics daily report for {force_id}.

Summary:
- New Interactions: {processed_data['summary']['newInteractions']}
- Metrics Updated: {processed_data['summary']['updatedMetrics']}
- Trends Calculated: {processed_data['summary']['trendsCalculated']}
- Processed Records: {processed_data['processedRecords']}
- Timestamp: {processed_data['timestamp']}

Status: {processed_data['status']}

This is an automated message. Please do not reply.
"""
        msg = MIMEMultipart()
        msg['From'] = email_from
        msg['To'] = email_to
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        try:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_pass)
                server.sendmail(email_from, email_to.split(','), msg.as_string())
            logging.info(f"Daily analytics email sent to {email_to}")
        except Exception as mailerr:
            logging.error(f"Failed to send analytics email: {mailerr}")

    except Exception as e:
        logging.error(f'Error in timer trigger: {str(e)}')
        raise

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function completed successfully')
