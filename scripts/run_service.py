import os
import sys
import subprocess
from pathlib import Path

import psutil


PROJECT_ROOT = Path(__file__).resolve().parent.parent

LOG_DIR = PROJECT_ROOT / "logs"
RUNTIME_DIR = PROJECT_ROOT / "runtime"

LOG_DIR.mkdir(exist_ok=True)
RUNTIME_DIR.mkdir(exist_ok=True)


SERVICE_CONFIG = {

    "meter": {
        "service_name": "meter-data-service",
        "cwd": (
            PROJECT_ROOT
            / "sources"
            / "smart-electricity-system"
            / "meter-data-service"
        ),
        "command": [
            "node",
            "server.js",
        ],
    },

    "billing": {
        "service_name": "billing-service",
        "cwd": (
            PROJECT_ROOT
            / "sources"
            / "smart-electricity-system"
            / "billing-service"
        ),
        "command": [
            "node",
            "app.js",
        ],
    },

    "prediction": {
        "service_name": "prediction-service",
        "cwd": (
            PROJECT_ROOT
            / "sources"
            / "smart-electricity-system"
            / "prediciton-service"
            / "prediction-service"
        ),
        "command": [
            "node",
            "app.js",
        ],
    },

    "user": {
        "service_name": "user-service",
        "cwd": (
            PROJECT_ROOT
            / "sources"
            / "smart-electricity-system"
            / "user-service"
        ),
        "command": [
            "cmd",
            "/c",
            "mvn",
            "spring-boot:run",
        ],
    },
}


def terminate_tree(pid):

    try:
        process = psutil.Process(pid)

    except psutil.NoSuchProcess:
        return

    children = process.children(
        recursive=True
    )

    for child in children:

        try:
            child.terminate()

        except psutil.Error:
            pass

    psutil.wait_procs(
        children,
        timeout=3
    )

    for child in children:

        try:

            if child.is_running():
                child.kill()

        except psutil.Error:
            pass

    try:
        process.terminate()

    except psutil.Error:
        pass


def run_service(key):

    if key not in SERVICE_CONFIG:

        print(
            f"Unknown service: {key}"
        )

        sys.exit(1)

    config = SERVICE_CONFIG[key]

    service_name = config[
        "service_name"
    ]

    cwd = config[
        "cwd"
    ]

    command = config[
        "command"
    ]

    log_path = (
        LOG_DIR
        / f"{service_name}.log"
    )

    pid_path = (
        RUNTIME_DIR
        / f"{service_name}.pid"
    )

    pid_path.write_text(
        str(os.getpid()),
        encoding="utf-8",
    )

    child = None

    try:

        with open(
            log_path,
            "a",
            encoding="utf-8",
            errors="replace",
        ) as log_file:

            header = (
                "\n"
                + "=" * 60
                + "\n"
                + f"STARTING {service_name}"
                + "\n"
                + "=" * 60
                + "\n"
            )

            print(
                header,
                end=""
            )

            log_file.write(
                header
            )

            log_file.flush()

            child = subprocess.Popen(
                command,
                cwd=str(cwd),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
                env=os.environ.copy(),
            )

            for line in child.stdout:

                print(
                    line,
                    end=""
                )

                log_file.write(
                    line
                )

                log_file.flush()

            child.wait()

    except KeyboardInterrupt:

        print(
            f"\nStopping {service_name}..."
        )

    finally:

        if child is not None:

            try:
                terminate_tree(
                    child.pid
                )

            except Exception:
                pass

        try:

            if pid_path.exists():

                stored_pid = (
                    pid_path
                    .read_text()
                    .strip()
                )

                if stored_pid == str(
                    os.getpid()
                ):
                    pid_path.unlink()

        except Exception:
            pass


if __name__ == "__main__":

    if len(sys.argv) != 2:

        print(
            "Usage: python scripts/run_service.py "
            "<meter|billing|prediction|user>"
        )

        sys.exit(1)

    run_service(
        sys.argv[1]
    )