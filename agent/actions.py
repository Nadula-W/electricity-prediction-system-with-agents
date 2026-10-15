import os
import subprocess
import sys
import time
from pathlib import Path

from agent.tools import (
    diagnose_service,
    get_service_status,
)


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

SERVICE_RUNNER = (
    PROJECT_ROOT
    / "scripts"
    / "run_service.py"
)


# ============================================================
# SERVICES THE AI IS ALLOWED TO START
# ============================================================

SERVICE_START_CONFIG = {

    "meter-data-service": {
        "runner_name": "meter",
        "port": 3000,
    },

    "billing-service": {
        "runner_name": "billing",
        "port": 3001,
    },

    "prediction-service": {
        "runner_name": "prediction",
        "port": 3002,
    },

    "user-service": {
        "runner_name": "user",
        "port": 8081,
    },
}


# ============================================================
# START ONE SERVICE
# ============================================================

def start_service(service_name):
    """
    Start one approved Smart Electricity microservice.

    Safety rules:

    - only predefined services may be started
    - do not start a service that is already healthy
    - do not start another process if its port is already open
    - use the existing run_service.py logger
    - verify health after starting
    """

    # --------------------------------------------------------
    # VALIDATE SERVICE
    # --------------------------------------------------------

    if service_name not in SERVICE_START_CONFIG:

        return {
            "service": service_name,
            "status": "denied",
            "error": (
                "This service is not approved "
                "for automatic startup."
            ),
        }


    # --------------------------------------------------------
    # MAKE SURE OUR SERVICE RUNNER EXISTS
    # --------------------------------------------------------

    if not SERVICE_RUNNER.exists():

        return {
            "service": service_name,
            "status": "failed",
            "error": (
                "scripts/run_service.py was not found."
            ),
        }


    # --------------------------------------------------------
    # CHECK CURRENT HTTP HEALTH
    # --------------------------------------------------------

    current_status = get_service_status(
        service_name
    )


    if current_status.get("status") == "healthy":

        return {
            "service": service_name,
            "status": "already_running",
            "message": (
                "Service is already healthy. "
                "No start action was performed."
            ),
            "health": current_status,
        }


    # --------------------------------------------------------
    # CHECK CURRENT PORT
    # --------------------------------------------------------

    port_status = diagnose_service(
        service_name
    )


    if port_status.get("port_status") == "open":

        return {
            "service": service_name,
            "status": "not_started",
            "message": (
                "The service port is already open. "
                "Automatic startup was not performed "
                "to avoid creating a duplicate process."
            ),
            "health": current_status,
            "port_diagnosis": port_status,
        }


    # --------------------------------------------------------
    # GET APPROVED RUNNER NAME
    # --------------------------------------------------------

    config = SERVICE_START_CONFIG[
        service_name
    ]

    runner_name = config[
        "runner_name"
    ]


    # --------------------------------------------------------
    # BUILD COMMAND
    #
    # sys.executable means:
    #
    # use the same Python interpreter that is
    # currently running the SRE agent.
    #
    # If .venv is active, it uses that Python.
    # --------------------------------------------------------

    command = [

        sys.executable,

        str(
            SERVICE_RUNNER
        ),

        runner_name,
    ]


    # --------------------------------------------------------
    # WINDOWS PROCESS SETTINGS
    # --------------------------------------------------------

    creation_flags = 0


    if os.name == "nt":

        creation_flags = (
            subprocess.CREATE_NEW_CONSOLE
        )


    # --------------------------------------------------------
    # START SERVICE
    # --------------------------------------------------------

    try:

        process = subprocess.Popen(
            command,
            cwd=str(
                PROJECT_ROOT
            ),
            creationflags=creation_flags,
        )


    except Exception as error:

        return {
            "service": service_name,
            "status": "failed",
            "error": str(
                error
            ),
        }


    # --------------------------------------------------------
    # GIVE SERVICE TIME TO START
    # --------------------------------------------------------

    time.sleep(
        5
    )


    # --------------------------------------------------------
    # VERIFY SERVICE AFTER START
    # --------------------------------------------------------

    new_status = get_service_status(
        service_name
    )


    new_port_status = diagnose_service(
        service_name
    )


    # --------------------------------------------------------
    # SUCCESS
    # --------------------------------------------------------

    if new_status.get("status") == "healthy":

        return {
            "service": service_name,
            "status": "started",
            "process_id": process.pid,
            "message": (
                "Service was started successfully "
                "and passed the health check."
            ),
            "health": new_status,
            "port_diagnosis": new_port_status,
        }


    # --------------------------------------------------------
    # PROCESS STARTED BUT SERVICE NOT HEALTHY
    # --------------------------------------------------------

    return {
        "service": service_name,
        "status": "start_attempt_failed",
        "process_id": process.pid,
        "message": (
            "A start attempt was made, but the "
            "service did not become healthy."
        ),
        "health": new_status,
        "port_diagnosis": new_port_status,
    }


# ============================================================
# DIRECT COMMAND-LINE TEST
# ============================================================

if __name__ == "__main__":

    print(
        "=" * 60
    )

    print(
        "Controlled Service Startup Test"
    )

    print(
        "=" * 60
    )

    print()

    service = input(
        "Service name: "
    ).strip()


    result = start_service(
        service
    )


    print()

    print(
        result
    )