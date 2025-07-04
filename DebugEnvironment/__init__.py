import logging
import json
import os
import sys
import azure.functions as func
from datetime import datetime


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Debug Environment function processed a request.')

    try:
        # Get environment information
        debug_info = {
            "timestamp": datetime.now().isoformat(),
            "python_version": sys.version,
            "python_executable": sys.executable,
            "python_path": sys.path,
            "environment_variables": {},
            "installed_packages": [],
            "package_import_tests": {}
        }

        # Get relevant environment variables
        env_vars = ['COSMOS_DB_ENDPOINT', 'COSMOS_DB_KEY', 'COSMOS_DB_DATABASE', 'COSMOS_DB_CONTAINER', 
                   'FORCE_IDENTIFIER', 'FUNCTIONS_WORKER_RUNTIME', 'FUNCTIONS_EXTENSION_VERSION',
                   'WEBSITE_PYTHON_DEFAULT_VERSION', 'SCM_DO_BUILD_DURING_DEPLOYMENT', 'ENABLE_ORYX_BUILD']
        
        for var in env_vars:
            value = os.environ.get(var)
            if var in ['COSMOS_DB_KEY']:
                debug_info["environment_variables"][var] = "SET" if value else "NOT SET"
            else:
                debug_info["environment_variables"][var] = value

        # Try to get installed packages
        try:
            import pkg_resources
            installed_packages = [f"{pkg.project_name}=={pkg.version}" for pkg in pkg_resources.working_set]
            debug_info["installed_packages"] = sorted(installed_packages)
        except:
            debug_info["installed_packages"] = "pkg_resources not available"

        # Test specific package imports
        packages_to_test = [
            'azure',
            'azure.functions',
            'azure.cosmos',
            'azure.identity',
            'requests',
            'json',
            'os',
            'sys',
            'datetime'
        ]

        for package in packages_to_test:
            try:
                __import__(package)
                debug_info["package_import_tests"][package] = "✅ SUCCESS"
            except ImportError as e:
                debug_info["package_import_tests"][package] = f"❌ FAILED: {str(e)}"
            except Exception as e:
                debug_info["package_import_tests"][package] = f"❌ ERROR: {str(e)}"

        # Try to find azure-cosmos specifically
        try:
            import importlib.util
            spec = importlib.util.find_spec('azure.cosmos')
            if spec:
                debug_info["azure_cosmos_spec"] = {
                    "name": spec.name,
                    "origin": spec.origin,
                    "submodule_search_locations": spec.submodule_search_locations
                }
            else:
                debug_info["azure_cosmos_spec"] = "Module spec not found"
        except Exception as e:
            debug_info["azure_cosmos_spec"] = f"Error finding spec: {str(e)}"

        return func.HttpResponse(
            json.dumps(debug_info, indent=2),
            status_code=200,
            headers={"Content-Type": "application/json"}
        )

    except Exception as e:
        logging.error(f"Error in debug function: {str(e)}")
        return func.HttpResponse(
            json.dumps({
                "error": "Debug function error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }),
            status_code=500,
            headers={"Content-Type": "application/json"}
        )
import azure.functions as func
import os
import json

def main(req: func.HttpRequest) -> func.HttpResponse:
    env_info = {k: v for k, v in os.environ.items()}
    request_info = {
        "method": req.method,
        "url": req.url,
        "headers": dict(req.headers),
        "params": dict(req.params)
    }
    return func.HttpResponse(
        json.dumps({
            "environment": env_info,
            "request": request_info
        }, indent=2),
        status_code=200,
        headers={"Content-Type": "application/json"}
    )
