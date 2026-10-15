import json

from langchain.tools import tool

from agent.tools import (
    list_services,
    get_service_status,
    diagnose_service,
    get_service_logs,
    check_service_dependencies,
    check_mysql_database,
)

from agent.actions import (
    start_service,
)


# ============================================================
# LANGCHAIN TOOL 1
# LIST SERVICES
# ============================================================

@tool
def sre_list_services() -> str:
    """
    List all Smart Electricity microservices
    configured for monitoring.
    """

    result = list_services()

    return json.dumps(
        result,
        indent=2
    )


# ============================================================
# LANGCHAIN TOOL 2
# CHECK SERVICE HEALTH
# ============================================================

@tool
def sre_check_service(
    service_name: str
) -> str:
    """
    Check the current HTTP health of one
    Smart Electricity microservice.

    Example service names:

    - meter-data-service
    - billing-service
    - prediction-service
    - user-service
    """

    result = get_service_status(
        service_name
    )

    return json.dumps(
        result,
        indent=2
    )


# ============================================================
# LANGCHAIN TOOL 3
# DIAGNOSE SERVICE PORT
# ============================================================

@tool
def sre_diagnose_service(
    service_name: str
) -> str:
    """
    Check whether the TCP port of a microservice
    is currently open or closed.

    Use this when a service is unhealthy
    or unreachable.
    """

    result = diagnose_service(
        service_name
    )

    return json.dumps(
        result,
        indent=2
    )


# ============================================================
# LANGCHAIN TOOL 4
# READ SERVICE LOGS
# ============================================================

@tool
def sre_get_service_logs(
    service_name: str,
    lines: int = 80
) -> str:
    """
    Read recent sanitized application logs.

    Use this when a service is:

    - unhealthy
    - unreachable
    - crashed
    - suspicious
    - failing during startup

    The tool returns only recent log lines
    and attempts to remove sensitive values.
    """

    result = get_service_logs(
        service_name,
        lines
    )

    return json.dumps(
        result,
        indent=2
    )


# ============================================================
# LANGCHAIN TOOL 5
# CHECK DEPENDENCIES
# ============================================================

@tool
def sre_check_dependencies(
    service_name: str
) -> str:
    """
    Check known required and optional dependencies
    for one service.

    Possible dependencies include:

    - MySQL
    - MongoDB
    - RabbitMQ
    - another microservice

    Required and optional failures are reported
    separately.
    """

    result = check_service_dependencies(
        service_name
    )

    return json.dumps(
        result,
        indent=2
    )


# ============================================================
# LANGCHAIN TOOL 6
# REAL MYSQL TEST
# ============================================================

@tool
def sre_check_mysql_database(
    service_name: str
) -> str:
    """
    Perform a real MySQL connection test for a
    MySQL-backed service.

    This checks:

    - MySQL network connectivity
    - username/password authentication
    - target database access
    - SELECT 1 execution

    Use this when:

    - database problems are suspected
    - MySQL port is reachable but the app fails
    - logs contain database errors
    - the affected service uses MySQL

    The database password is never returned.
    """

    result = check_mysql_database(
        service_name
    )

    return json.dumps(
        result,
        indent=2
    )


# ============================================================
# LANGCHAIN TOOL 7
# START / RECOVER SERVICE
# ============================================================

@tool
def sre_start_service(
    service_name: str
) -> str:
    """
    Start one approved Smart Electricity microservice.

    This is a CONTROLLED recovery action.

    Allowed services:

    - meter-data-service
    - billing-service
    - prediction-service
    - user-service

    Use this only when investigation shows that:

    - the service is unhealthy or unreachable
    - its service port is closed
    - the process appears to be stopped
    - required dependencies are available

    The action automatically:

    - prevents duplicate service processes
    - starts the service using run_service.py
    - preserves application logging
    - waits for startup
    - performs a health check
    - returns whether recovery succeeded
    """

    result = start_service(
        service_name
    )

    return json.dumps(
        result,
        indent=2
    )


# ============================================================
# TOOLS AVAILABLE TO THE AI AGENT
# ============================================================

SRE_TOOLS = [

    sre_list_services,

    sre_check_service,

    sre_diagnose_service,

    sre_get_service_logs,

    sre_check_dependencies,

    sre_check_mysql_database,

    sre_start_service,
]