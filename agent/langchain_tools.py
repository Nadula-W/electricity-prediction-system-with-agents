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

    return json.dumps(
        list_services(),
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
    """

    return json.dumps(
        get_service_status(
            service_name
        ),
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
    Check whether the TCP port of a service
    is currently open or closed.
    """

    return json.dumps(
        diagnose_service(
            service_name
        ),
        indent=2
    )


# ============================================================
# LANGCHAIN TOOL 4
# READ LOGS
# ============================================================

@tool
def sre_get_service_logs(
    service_name: str,
    lines: int = 80
) -> str:
    """
    Read recent sanitized logs for a service.

    Useful when a service is unhealthy,
    unreachable, crashed, or suspicious.
    """

    return json.dumps(
        get_service_logs(
            service_name,
            lines
        ),
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
    Check known required and optional runtime
    dependencies for one service.

    This includes infrastructure TCP checks
    and dependent microservice health checks.
    """

    return json.dumps(
        check_service_dependencies(
            service_name
        ),
        indent=2
    )


# ============================================================
# LANGCHAIN TOOL 6
# REAL MYSQL CHECK
# ============================================================

@tool
def sre_check_mysql_database(
    service_name: str
) -> str:
    """
    Perform a real MySQL authentication and query test
    for a MySQL-backed service.

    This verifies:

    - MySQL server connectivity
    - username/password authentication
    - target database access
    - execution of SELECT 1

    Use this when:

    - logs indicate a database problem
    - MySQL port is reachable but the application fails
    - database authentication is suspected
    - the user asks whether a service can actually use MySQL

    No password is returned by this tool.
    """

    return json.dumps(
        check_mysql_database(
            service_name
        ),
        indent=2
    )


# ============================================================
# TOOLS AVAILABLE TO AI
# ============================================================

SRE_TOOLS = [

    sre_list_services,

    sre_check_service,

    sre_diagnose_service,

    sre_get_service_logs,

    sre_check_dependencies,

    sre_check_mysql_database,
]