import os
import time
import requests
from dotenv import load_dotenv
load_dotenv()
SERVICE_CONFIG = {
    "prediction-service": {
        "url": os.getenv("PREDICTION_SERVICE_URL"),
        "check_path": "/api/predictions",
    },

    "billing-service": {
        "url": os.getenv("BILLING_SERVICE_URL"),
        "check_path": "/api/bills",
    },
}


def list_services() -> dict:
    """
    Return all services currently configured
    for investigation.
    """

    return {
        "services": list(SERVICE_CONFIG.keys())
    }


def get_service_status(service_name: str) -> dict:
    """
    Check whether a configured service is reachable
    and responding correctly.
    """

    if service_name not in SERVICE_CONFIG:
        return {
            "service": service_name,
            "status": "unknown",
            "error": "Service is not configured",
        }

    service = SERVICE_CONFIG[service_name]

    base_url = service["url"]
    check_path = service["check_path"]

    if not base_url:
        return {
            "service": service_name,
            "status": "configuration_error",
            "error": "Service URL is missing",
        }

    url = f"{base_url.rstrip('/')}{check_path}"

    try:

        start_time = time.perf_counter()

        response = requests.get(
            url,
            timeout=5
        )

        response_time_ms = round(
            (time.perf_counter() - start_time) * 1000,
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
            "response_time_ms": response_time_ms,
        }

    except requests.exceptions.ConnectionError:

        return {
            "service": service_name,
            "status": "unreachable",
            "url": url,
            "error": "Connection refused",
        }

    except requests.exceptions.Timeout:

        return {
            "service": service_name,
            "status": "unreachable",
            "url": url,
            "error": "Request timed out",
        }

    except requests.exceptions.RequestException as error:

        return {
            "service": service_name,
            "status": "error",
            "url": url,
            "error": str(error),
        }