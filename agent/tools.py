import os
import re
import socket
import time

from pathlib import Path
from urllib.parse import urlparse

import mysql.connector
import requests

from dotenv import load_dotenv
from mysql.connector import Error as MySQLError


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

ENV_FILE = PROJECT_ROOT / ".env"

LOGS_ROOT = PROJECT_ROOT / "logs"


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv(ENV_FILE)


# ============================================================
# MYSQL CONFIGURATION
# ============================================================

MYSQL_HOST = os.getenv(
    "MYSQL_HOST",
    "localhost"
)

MYSQL_PORT = int(
    os.getenv(
        "MYSQL_PORT",
        "3306"
    )
)

MYSQL_USER = os.getenv(
    "MYSQL_USER",
    "meteruser"
)

MYSQL_PASSWORD = os.getenv(
    "MYSQL_PASSWORD",
    ""
)


# ============================================================
# MONGODB CONFIGURATION
# ============================================================

MONGODB_HOST = os.getenv(
    "MONGODB_HOST",
    "localhost"
)

MONGODB_PORT = int(
    os.getenv(
        "MONGODB_PORT",
        "27017"
    )
)


# ============================================================
# RABBITMQ CONFIGURATION
# ============================================================

RABBITMQ_HOST = os.getenv(
    "RABBITMQ_HOST",
    "localhost"
)

RABBITMQ_PORT = int(
    os.getenv(
        "RABBITMQ_PORT",
        "5672"
    )
)


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

        "log_file": "meter-data-service.log",

        "database_type": "mongodb",

        "dependencies": [

            {
                "name": "mongodb",
                "type": "tcp",
                "host": MONGODB_HOST,
                "port": MONGODB_PORT,
                "required": True,
            }

        ],
    },


    "billing-service": {

        "url": os.getenv(
            "BILLING_SERVICE_URL",
            "http://localhost:3001"
        ),

        "check_path": "/api/bills",

        "log_file": "billing-service.log",

        "database_type": "mysql",

        "database_name": "billing_db",

        "dependencies": [

            {
                "name": "mysql",
                "type": "tcp",
                "host": MYSQL_HOST,
                "port": MYSQL_PORT,
                "required": True,
            },

            {
                "name": "meter-data-service",
                "type": "service",
                "service_name": "meter-data-service",
                "required": True,
            },

            {
                "name": "rabbitmq",
                "type": "tcp",
                "host": RABBITMQ_HOST,
                "port": RABBITMQ_PORT,
                "required": False,
            },

        ],
    },


    "prediction-service": {

        "url": os.getenv(
            "PREDICTION_SERVICE_URL",
            "http://localhost:3002"
        ),

        "check_path": "/api/predictions",

        "log_file": "prediction-service.log",

        "database_type": "mysql",

        "database_name": "prediction_db",

        "dependencies": [

            {
                "name": "mysql",
                "type": "tcp",
                "host": MYSQL_HOST,
                "port": MYSQL_PORT,
                "required": True,
            },

            {
                "name": "meter-data-service",
                "type": "service",
                "service_name": "meter-data-service",
                "required": True,
            },

        ],
    },


    "user-service": {

        "url": os.getenv(
            "USER_SERVICE_URL",
            "http://localhost:8081"
        ),

        "check_path": "/api/users/health",

        "log_file": "user-service.log",

        "database_type": "mysql",

        "database_name": "user_db",

        "dependencies": [

            {
                "name": "mysql",
                "type": "tcp",
                "host": MYSQL_HOST,
                "port": MYSQL_PORT,
                "required": True,
            }

        ],
    },
}


# ============================================================
# TOOL 1
# LIST SERVICES
# ============================================================

def list_services():

    return {
        "services": list(
            SERVICE_CONFIG.keys()
        )
    }


# ============================================================
# TOOL 2
# CHECK SERVICE HEALTH
# ============================================================

def get_service_status(service_name):

    if service_name not in SERVICE_CONFIG:

        return {
            "service": service_name,
            "status": "unknown",
            "error": "Service is not configured"
        }


    service = SERVICE_CONFIG[
        service_name
    ]

    base_url = service[
        "url"
    ].rstrip("/")

    check_path = service[
        "check_path"
    ].lstrip("/")

    url = (
        base_url
        + "/"
        + check_path
    )


    try:

        start_time = time.perf_counter()

        response = requests.get(
            url,
            timeout=5
        )

        response_time_ms = round(
            (
                time.perf_counter()
                - start_time
            )
            * 1000,
            2
        )


        status = (
            "healthy"
            if response.status_code == 200
            else "unhealthy"
        )


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
            "error": (
                "Connection refused "
                "or host unreachable"
            )
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


# ============================================================
# GENERIC TCP PORT CHECK
# ============================================================

def check_tcp_port(
    host,
    port,
    timeout=2
):

    sock = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    sock.settimeout(
        timeout
    )


    try:

        result = sock.connect_ex(
            (
                host,
                port
            )
        )

        return result == 0


    except Exception:

        return False


    finally:

        sock.close()


# ============================================================
# TOOL 3
# DIAGNOSE SERVICE PORT
# ============================================================

def diagnose_service(service_name):

    if service_name not in SERVICE_CONFIG:

        return {
            "service": service_name,
            "diagnosis": (
                "Service is not configured"
            )
        }


    base_url = SERVICE_CONFIG[
        service_name
    ]["url"]

    parsed_url = urlparse(
        base_url
    )

    host = parsed_url.hostname

    port = parsed_url.port


    if not host or not port:

        return {
            "service": service_name,
            "diagnosis": (
                "Invalid service URL"
            ),
            "url": base_url
        }


    is_open = check_tcp_port(
        host,
        port
    )


    if is_open:

        return {
            "service": service_name,
            "host": host,
            "port": port,
            "port_status": "open",
            "diagnosis": (
                "The service port is open. "
                "The process appears to be running."
            )
        }


    return {
        "service": service_name,
        "host": host,
        "port": port,
        "port_status": "closed",
        "diagnosis": (
            "Nothing is listening on this port. "
            "The service may be stopped or crashed."
        )
    }


# ============================================================
# LOG SANITIZATION
# ============================================================

def sanitize_text(text):

    if not isinstance(
        text,
        str
    ):

        return text


    patterns = [

        (
            r'(?i)(password\s*[=:]\s*)[^\s]+',
            r'\1***REDACTED***'
        ),

        (
            r'(?i)(api[_-]?key\s*[=:]\s*)[^\s]+',
            r'\1***REDACTED***'
        ),

        (
            r'(?i)(authorization\s*[=:]\s*)[^\s]+',
            r'\1***REDACTED***'
        ),

        (
            r'(?i)(token\s*[=:]\s*)[^\s]+',
            r'\1***REDACTED***'
        ),
    ]


    sanitized = text


    for pattern, replacement in patterns:

        sanitized = re.sub(
            pattern,
            replacement,
            sanitized
        )


    if MYSQL_PASSWORD:

        sanitized = sanitized.replace(
            MYSQL_PASSWORD,
            "***REDACTED***"
        )


    return sanitized


# ============================================================
# TOOL 4
# READ SERVICE LOGS
# ============================================================

def get_service_logs(
    service_name,
    lines=80
):

    if service_name not in SERVICE_CONFIG:

        return {
            "service": service_name,
            "status": "error",
            "error": (
                "Service is not configured"
            )
        }


    try:

        lines = int(
            lines
        )

    except (
        TypeError,
        ValueError
    ):

        lines = 80


    lines = max(
        1,
        min(
            lines,
            150
        )
    )


    log_filename = SERVICE_CONFIG[
        service_name
    ]["log_file"]


    log_path = (
        LOGS_ROOT
        / log_filename
    )


    if not log_path.exists():

        return {
            "service": service_name,
            "status": "log_not_found",
            "log_file": str(
                log_path
            ),
            "error": (
                "Log file does not exist yet."
            )
        }


    try:

        with open(
            log_path,
            "r",
            encoding="utf-8",
            errors="replace"
        ) as log_file:

            all_lines = (
                log_file.readlines()
            )


        recent_lines = (
            all_lines[-lines:]
        )


        safe_lines = [

            sanitize_text(
                line
            )

            for line
            in recent_lines
        ]


        return {
            "service": service_name,
            "status": "success",
            "log_file": str(
                log_path
            ),
            "lines_requested": lines,
            "lines_returned": len(
                safe_lines
            ),
            "logs": "".join(
                safe_lines
            )
        }


    except Exception as error:

        return {
            "service": service_name,
            "status": "error",
            "log_file": str(
                log_path
            ),
            "error": sanitize_text(
                str(error)
            )
        }


# ============================================================
# CHECK ONE DEPENDENCY
# ============================================================

def check_dependency(
    dependency
):

    dependency_type = dependency.get(
        "type"
    )

    dependency_name = dependency.get(
        "name"
    )

    required = dependency.get(
        "required",
        True
    )


    if dependency_type == "tcp":

        host = dependency.get(
            "host"
        )

        port = dependency.get(
            "port"
        )


        is_open = check_tcp_port(
            host,
            port
        )


        return {
            "dependency": dependency_name,
            "type": "tcp",
            "host": host,
            "port": port,
            "required": required,
            "status": (
                "available"
                if is_open
                else "unavailable"
            )
        }


    if dependency_type == "service":

        target_service = dependency.get(
            "service_name"
        )


        result = get_service_status(
            target_service
        )


        dependency_status = (
            "available"
            if result.get(
                "status"
            ) == "healthy"
            else "unavailable"
        )


        return {
            "dependency": dependency_name,
            "type": "service",
            "service_name": target_service,
            "required": required,
            "status": dependency_status,
            "service_status": result
        }


    return {
        "dependency": dependency_name,
        "type": dependency_type,
        "required": required,
        "status": "unknown"
    }


# ============================================================
# TOOL 5
# CHECK SERVICE DEPENDENCIES
# ============================================================

def check_service_dependencies(
    service_name
):

    if service_name not in SERVICE_CONFIG:

        return {
            "service": service_name,
            "status": "error",
            "error": (
                "Service is not configured"
            )
        }


    dependencies = SERVICE_CONFIG[
        service_name
    ].get(
        "dependencies",
        []
    )


    results = []


    for dependency in dependencies:

        results.append(
            check_dependency(
                dependency
            )
        )


    required_failures = [

        item

        for item
        in results

        if (
            item.get(
                "required"
            ) is True
            and
            item.get(
                "status"
            ) != "available"
        )
    ]


    optional_failures = [

        item

        for item
        in results

        if (
            item.get(
                "required"
            ) is False
            and
            item.get(
                "status"
            ) != "available"
        )
    ]


    if required_failures:

        overall_status = (
            "dependency_failure"
        )

    elif optional_failures:

        overall_status = (
            "available_with_optional_issues"
        )

    else:

        overall_status = (
            "all_dependencies_available"
        )


    return {
        "service": service_name,
        "status": overall_status,
        "dependencies": results,
        "required_failures": len(
            required_failures
        ),
        "optional_failures": len(
            optional_failures
        )
    }


# ============================================================
# TOOL 6
# CHECK ACTUAL MYSQL DATABASE ACCESS
# ============================================================

def check_mysql_database(
    service_name
):
    """
    Perform a real MySQL login and SELECT 1 test.

    This verifies more than TCP reachability.

    It checks:

    - server reachable
    - username/password accepted
    - configured database exists
    - simple SQL query succeeds

    Passwords are never returned.
    """

    if service_name not in SERVICE_CONFIG:

        return {
            "service": service_name,
            "status": "error",
            "error": (
                "Service is not configured"
            )
        }


    service = SERVICE_CONFIG[
        service_name
    ]


    if service.get(
        "database_type"
    ) != "mysql":

        return {
            "service": service_name,
            "status": "not_applicable",
            "message": (
                "This service does not use MySQL."
            )
        }


    database_name = service.get(
        "database_name"
    )


    connection = None

    cursor = None


    try:

        start_time = (
            time.perf_counter()
        )


        connection = (
            mysql.connector.connect(
                host=MYSQL_HOST,
                port=MYSQL_PORT,
                user=MYSQL_USER,
                password=MYSQL_PASSWORD,
                database=database_name,
                connection_timeout=5,
            )
        )


        cursor = (
            connection.cursor()
        )


        cursor.execute(
            "SELECT 1"
        )


        query_result = (
            cursor.fetchone()
        )


        response_time_ms = round(
            (
                time.perf_counter()
                - start_time
            )
            * 1000,
            2
        )


        if (
            connection.is_connected()
            and
            query_result
            and
            query_result[0] == 1
        ):

            return {
                "service": service_name,
                "database_type": "mysql",
                "database": database_name,
                "host": MYSQL_HOST,
                "port": MYSQL_PORT,
                "status": "success",
                "authentication": "success",
                "database_access": "success",
                "query_test": "success",
                "response_time_ms": response_time_ms
            }


        return {
            "service": service_name,
            "database_type": "mysql",
            "database": database_name,
            "host": MYSQL_HOST,
            "port": MYSQL_PORT,
            "status": "failed",
            "authentication": "unknown",
            "database_access": "unknown",
            "query_test": "failed"
        }


    except MySQLError as error:

        error_number = getattr(
            error,
            "errno",
            None
        )

        sql_state = getattr(
            error,
            "sqlstate",
            None
        )


        if error_number == 1045:

            error_type = (
                "authentication_failed"
            )

        elif error_number == 1049:

            error_type = (
                "database_not_found"
            )

        elif error_number in [
            2002,
            2003
        ]:

            error_type = (
                "connection_failed"
            )

        else:

            error_type = (
                "mysql_error"
            )


        return {
            "service": service_name,
            "database_type": "mysql",
            "database": database_name,
            "host": MYSQL_HOST,
            "port": MYSQL_PORT,
            "status": "failed",
            "error_type": error_type,
            "mysql_error_number": error_number,
            "sql_state": sql_state,
            "error": sanitize_text(
                str(error)
            )
        }


    except Exception as error:

        return {
            "service": service_name,
            "database_type": "mysql",
            "database": database_name,
            "host": MYSQL_HOST,
            "port": MYSQL_PORT,
            "status": "error",
            "error": sanitize_text(
                str(error)
            )
        }


    finally:

        if cursor is not None:

            try:

                cursor.close()

            except Exception:

                pass


        if connection is not None:

            try:

                if connection.is_connected():

                    connection.close()

            except Exception:

                pass