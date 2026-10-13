import os
import time
import requests

from dotenv import load_dotenv


# Load variables from the project's .env file
load_dotenv()


SERVICE_CONFIG = {

    "meter-data-service": {
        "url": os.getenv("METER_SERVICE_URL", "http://localhost:3000"),
        "check_path": "/health",
    },

    "billing-service": {
        "url": os.getenv("BILLING_SERVICE_URL", "http://localhost:3001"),
        "check_path": "/api/bills",
    },

    "prediction-service": {
        "url": os.getenv("PREDICTION_SERVICE_URL", "http://localhost:3002"),
        "check_path": "/api/predictions",
    },

    "user-service": {
        "url": os.getenv("USER_SERVICE_URL", "http://localhost:8081"),
        "check_path": "/api/users/health",
    },
}


def list_services():
    """
    Return all services known by the SRE agent.
    """

    return {
        "services": list(SERVICE_CONFIG.keys())
    }


def get_service_status(service_name):
    """
    Check whether a service is healthy.
    """

    if service_name not in SERVICE_CONFIG:

        return {
            "service": service_name,
            "status": "unknown",
            "error": "Service is not configured"
        }

    service = SERVICE_CONFIG[service_name]

    url = service["url"] + service["check_path"]

    try:

        start_time = time.time()

        response = requests.get(
            url,
            timeout=5
        )

        elapsed_time = time.time() - start_time

        response_time_ms = round(
            elapsed_time * 1000,
            2
        )

        if response.status_code == 200:

            status = "healthy"

        else:

            status = "unhealthy"

        return {
            "service": service_name,
            "status": status,
            "url": url,
            "http_status": response.status_code,
            "response_time_ms": response_time_ms
        }

    except requests.exceptions.ConnectionError:

        return {
            "service": service_name,
            "status": "unreachable",
            "url": url,
            "error": "Connection refused"
        }

    except requests.exceptions.Timeout:

        return {
            "service": service_name,
            "status": "unreachable",
            "url": url,
            "error": "Request timed out"
        }

    except Exception as error:

        return {
            "service": service_name,
            "status": "error",
            "url": url,
            "error": str(error)
        }