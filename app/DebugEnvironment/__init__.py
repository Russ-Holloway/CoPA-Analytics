import logging
import azure.functions as func
import os
import json

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('DebugEnvironment function processed a request.')
    return func.HttpResponse("Debug info", status_code=200)
