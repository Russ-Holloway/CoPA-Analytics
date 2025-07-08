import os
import azure.functions as func

def main(req: func.HttpRequest) -> func.HttpResponse:
    logo_url = os.environ.get('FORCE_LOGO_URL')
    if not logo_url:
        # Return a 404 or a default image if FORCE_LOGO_URL is not set
        return func.HttpResponse(
            "Logo not configured.",
            status_code=404,
            headers={"Content-Type": "text/plain"}
        )
    # Option 1: Redirect to the logo URL (recommended for external blobs)
    return func.HttpResponse(
        status_code=302,
        headers={"Location": logo_url}
    )
    # Option 2: (Advanced) Download and stream the image directly (not shown here)
