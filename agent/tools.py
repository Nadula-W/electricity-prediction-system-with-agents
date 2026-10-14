import os
import time
import socket

from pathlib import Path
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

ENV_FILE = PROJECT_ROOT / ".env"

load_dotenv(ENV_FILE)


# ============================================================
# SERVICE CONFIGURATION
# ============================================================

SERVICE_CONFIG = {

    "meter-data-service": {
        "url": os.getenv(
            "METER_SERVICE_URL",
            "http://localhost:3000"
        ),
        "check_path": "/health",
    },

    "billing-service": {
        "url": os.getenv(
            "BILLING_SERVICE_URL",
            "http://localhost:3001"
        ),
        "check_path": "/api/bills",
    },

    "prediction-service": {
        "url": os.getenv(
            "PREDICTION_SERVICE_URL",
            "http://localhost:3002"
        ),
        "check_path": "/api/predictions",
    },

    "user-service": {
        "url": os.getenv(
            "USER_SERVICE_URL",
            "http://localhost:8081"
        ),
        "check_path": "/api/users/health",
    },
}


# ============================================================
# TOOL 1
# LIST SERVICES
# ============================================================

def list_services():

    """
    Return all services that the SRE agent knows about.
    """

    return {
        "services": list(SERVICE_CONFIG.keys())
    }


# ============================================================
# TOOL 2
# CHECK SERVICE HEALTH
# ============================================================

def get_service_status(service_name):

    """
    Send an HTTP request to a service.

    Possible results:

    healthy
        HTTP 200

    unhealthy
        Server responded, but response was not HTTP 200

    unreachable
        Could not establish a connection

    error
        Unexpected problem
    """

    # --------------------------------------------------------
    # Check whether service exists in our configuration
    # --------------------------------------------------------

    if service_name not in SERVICE_CONFIG:

        return {
            "service": service_name,
            "status": "unknown",
            "error": "Service is not configured"
        }

    service = SERVICE_CONFIG[service_name]

    base_url = service["url"]
    check_path = service["check_path"]

    url = base_url.rstrip("/") + "/" + check_path.lstrip("/")

    try:

        # ----------------------------------------------------
        # Start timer
        # ----------------------------------------------------

        start_time = time.time()

        # ----------------------------------------------------
        # Send HTTP request
        # ----------------------------------------------------

        response = requests.get(
            url,
            timeout=5
        )

        # ----------------------------------------------------
        # Calculate response time
        # ----------------------------------------------------

        elapsed_time = time.time() - start_time

        response_time_ms = round(
            elapsed_time * 1000,
            2
        )

        # ----------------------------------------------------
        # Decide service status
        # ----------------------------------------------------

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

    # --------------------------------------------------------
    # Connection refused
    # --------------------------------------------------------

    except requests.exceptions.ConnectionError:

        return {
            "service": service_name,
            "status": "unreachable",
            "url": url,
            "error": "Connection refused"
        }

    # --------------------------------------------------------
    # Request took too long
    # --------------------------------------------------------

    except requests.exceptions.Timeout:

        return {
            "service": service_name,
            "status": "unreachable",
            "url": url,
            "error": "Request timed out"
        }

    # --------------------------------------------------------
    # Any other unexpected error
    # --------------------------------------------------------

    except Exception as error:

        return {
            "service": service_name,
            "status": "error",
            "url": url,
            "error": str(error)
        }


# ============================================================
# TOOL 3
# DIAGNOSE SERVICE
# ============================================================

def diagnose_service(service_name):

    """
    Perform a basic investigation of a service.

    Currently this checks whether the TCP port used
    by the service is open.

    Later we will add:
        - log inspection
        - database checking
        - dependency checking
        - configuration checking
    """

    # --------------------------------------------------------
    # Check service exists
    # --------------------------------------------------------

    if service_name not in SERVICE_CONFIG:

        return {
            "service": service_name,
            "diagnosis": "Service is not configured"
        }

    service = SERVICE_CONFIG[service_name]

    base_url = service["url"]

    # --------------------------------------------------------
    # Extract hostname and port
    #
    # Example:
    #
    # http://localhost:3001
    #
    # becomes:
    #
    # host = localhost
    # port = 3001
    # --------------------------------------------------------

    parsed_url = urlparse(base_url)

    host = parsed_url.hostname
    port = parsed_url.port

    if not host or not port:

        return {
            "service": service_name,
            "diagnosis": "Invalid service URL"
        }

    # --------------------------------------------------------
    # Create TCP socket
    # --------------------------------------------------------

    sock = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    sock.settimeout(2)

    try:

        # ----------------------------------------------------
        # Try connecting to the port
        # ----------------------------------------------------

        connection_result = sock.connect_ex(
            (host, port)
        )

        # ----------------------------------------------------
        # Port open
        # ----------------------------------------------------

        if connection_result == 0:

            return {
                "service": service_name,
                "host": host,
                "port": port,
                "port_status": "open",
                "diagnosis":
                    "The service port is open. "
                    "The application is running, but it may be "
                    "returning an application or dependency error."
            }

        # ----------------------------------------------------
        # Port closed
        # ----------------------------------------------------

        return {
            "service": service_name,
            "host": host,
            "port": port,
            "port_status": "closed",
            "diagnosis":
                "Nothing is listening on this port. "
                "The service may be stopped or crashed."
        }

    except Exception as error:

        return {
            "service": service_name,
            "host": host,
            "port": port,
            "diagnosis": str(error)
        }

    finally:

        sock.close()