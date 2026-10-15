import json

from langchain.tools import tool

from agent.tools import (
    list_services,
    get_service_status,
    diagnose_service,
)


# ============================================================
# LANGCHAIN TOOL 1
# LIST ALL SERVICES
# ============================================================

@tool
def sre_list_services() -> str:
    """
    List all microservices configured in the Smart Electricity System.

    Use this tool when you need to know which services are available
    for monitoring or investigation.
    """

    result = list_services()

    return json.dumps(
        result,
        indent=2
    )


# ============================================================
# LANGCHAIN TOOL 2
# CHECK ONE SERVICE
# ============================================================

@tool
def sre_check_service(service_name: str) -> str:
    """
    Check the current HTTP health of one microservice.

    Use the exact service name returned by sre_list_services.

    Example service names:
    - meter-data-service
    - billing-service
    - prediction-service
    - user-service
    """

    result = get_service_status(service_name)

    return json.dumps(
        result,
        indent=2
    )


# ============================================================
# LANGCHAIN TOOL 3
# DIAGNOSE ONE SERVICE
# ============================================================

@tool
def sre_diagnose_service(service_name: str) -> str:
    """
    Perform a basic network diagnosis of one microservice.

    This checks whether the TCP port used by the service is open.

    Use this tool when sre_check_service reports that a service
    is unhealthy or unreachable.

    Example:
    billing-service -> port 3001
    """

    result = diagnose_service(service_name)

    return json.dumps(
        result,
        indent=2
    )


# ============================================================
# LIST OF TOOLS AVAILABLE TO THE FUTURE AI AGENT
# ============================================================

SRE_TOOLS = [
    sre_list_services,
    sre_check_service,
    sre_diagnose_service,
] 