import os
import subprocess
import sys
import time
from pathlib import Path

import psutil

from agent.tools import (
    diagnose_service,
    get_service_status,
)


PROJECT_ROOT = Path(__file__).resolve().parent.parent

SERVICE_RUNNER = (
    PROJECT_ROOT
    / "scripts"
    / "run_service.py"
)

RUNTIME_DIR = (
    PROJECT_ROOT
    / "runtime"
)

RUNTIME_DIR.mkdir(
    exist_ok=True
)


SERVICE_ACTION_CONFIG = {

    "meter-data-service": {
        "runner": "meter",
    },

    "billing-service": {
        "runner": "billing",
    },

    "prediction-service": {
        "runner": "prediction",
    },

    "user-service": {
        "runner": "user",
    },
}


def get_pid_file(
    service_name
):

    return (
        RUNTIME_DIR
        / f"{service_name}.pid"
    )


def start_service(
    service_name
):

    if service_name not in SERVICE_ACTION_CONFIG:

        return {
            "service": service_name,
            "status": "denied",
            "error": "Service is not approved.",
        }

    current = get_service_status(
        service_name
    )

    if current.get(
        "status"
    ) == "healthy":

        return {
            "service": service_name,
            "status": "already_running",
            "message": "Service is already healthy.",
        }

    port = diagnose_service(
        service_name
    )

    if port.get(
        "port_status"
    ) == "open":

        return {
            "service": service_name,
            "status": "blocked",
            "message": (
                "Service port is already open. "
                "A duplicate process will not be started."
            ),
        }

    pid_file = get_pid_file(
        service_name
    )

    if pid_file.exists():

        try:
            old_pid = int(
                pid_file
                .read_text()
                .strip()
            )

            if not psutil.pid_exists(
                old_pid
            ):
                pid_file.unlink()

        except Exception:

            try:
                pid_file.unlink()
            except Exception:
                pass

    runner = (
        SERVICE_ACTION_CONFIG[
            service_name
        ]["runner"]
    )

    command = [
        sys.executable,
        str(
            SERVICE_RUNNER
        ),
        runner,
    ]

    creation_flags = 0

    if os.name == "nt":

        creation_flags = (
            subprocess.CREATE_NEW_CONSOLE
        )

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

    # Wait up to 20 seconds
    for _ in range(20):

        time.sleep(1)

        status = get_service_status(
            service_name
        )

        if status.get(
            "status"
        ) == "healthy":

            return {
                "service": service_name,
                "status": "started",
                "process_id": process.pid,
                "health": status,
            }

    return {
        "service": service_name,
        "status": "start_attempt_failed",
        "process_id": process.pid,
        "health": get_service_status(
            service_name
        ),
    }


def stop_service(
    service_name
):

    if service_name not in SERVICE_ACTION_CONFIG:

        return {
            "service": service_name,
            "status": "denied",
            "error": "Service is not approved.",
        }

    pid_file = get_pid_file(
        service_name
    )

    if not pid_file.exists():

        current = get_service_status(
            service_name
        )

        if current.get(
            "status"
        ) != "healthy":

            return {
                "service": service_name,
                "status": "already_stopped",
                "message": (
                    "Service is already stopped."
                ),
            }

        return {
            "service": service_name,
            "status": "not_managed",
            "message": (
                "The service is running, but it was not "
                "started by the SRE service runner. "
                "It will not be terminated for safety."
            ),
        }

    try:

        pid = int(
            pid_file
            .read_text()
            .strip()
        )

    except Exception:

        return {
            "service": service_name,
            "status": "failed",
            "error": "Invalid PID file.",
        }

    try:

        parent = psutil.Process(
            pid
        )

    except psutil.NoSuchProcess:

        try:
            pid_file.unlink()
        except Exception:
            pass

        return {
            "service": service_name,
            "status": "already_stopped",
        }

    children = parent.children(
        recursive=True
    )

    # Stop child processes first.
    for child in reversed(
        children
    ):

        try:
            child.terminate()

        except psutil.Error:
            pass

    _, alive = psutil.wait_procs(
        children,
        timeout=4,
    )

    for child in alive:

        try:
            child.kill()

        except psutil.Error:
            pass

    try:
        parent.terminate()
        parent.wait(
            timeout=3
        )

    except psutil.TimeoutExpired:

        try:
            parent.kill()
        except psutil.Error:
            pass

    except psutil.Error:
        pass

    try:

        if pid_file.exists():
            pid_file.unlink()

    except Exception:
        pass

    # Verify service actually went down.
    for _ in range(8):

        time.sleep(
            0.5
        )

        status = get_service_status(
            service_name
        )

        port = diagnose_service(
            service_name
        )

        if (
            status.get("status")
            != "healthy"
            and
            port.get("port_status")
            == "closed"
        ):

            return {
                "service": service_name,
                "status": "stopped",
                "message": (
                    "Service stopped successfully."
                ),
            }

    return {
        "service": service_name,
        "status": "stop_incomplete",
        "health": get_service_status(
            service_name
        ),
        "port": diagnose_service(
            service_name
        ),
    }