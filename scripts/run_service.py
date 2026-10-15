import argparse
import subprocess
import sys
from pathlib import Path


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

SERVICES_ROOT = (
    PROJECT_ROOT
    / "sources"
    / "smart-electricity-system"
)

LOGS_ROOT = PROJECT_ROOT / "logs"


# ============================================================
# SERVICE CONFIGURATION
# ============================================================

SERVICE_CONFIG = {

    "meter": {
        "name": "meter-data-service",
        "directory": SERVICES_ROOT / "meter-data-service",
        "command": ["node", "server.js"],
    },

    "billing": {
        "name": "billing-service",
        "directory": SERVICES_ROOT / "billing-service",
        "command": ["node", "app.js"],
    },

    "prediction": {
        "name": "prediction-service",
        "directory": (
            SERVICES_ROOT
            / "prediciton-service"
            / "prediction-service"
        ),
        "command": ["node", "app.js"],
    },

    "user": {
        "name": "user-service",
        "directory": SERVICES_ROOT / "user-service",
        "command": [
            "mvn",
            "spring-boot:run",
        ],
    },
}


# ============================================================
# RUN SERVICE AND SAVE OUTPUT
# ============================================================

def run_service(service_key):

    if service_key not in SERVICE_CONFIG:

        print(
            f"Unknown service: {service_key}"
        )

        print(
            "Available services:",
            ", ".join(SERVICE_CONFIG.keys())
        )

        sys.exit(1)

    service = SERVICE_CONFIG[service_key]

    service_name = service["name"]

    service_directory = service["directory"]

    command = service["command"]


    # --------------------------------------------------------
    # CHECK SERVICE DIRECTORY
    # --------------------------------------------------------

    if not service_directory.exists():

        print(
            f"Service directory not found:"
        )

        print(
            service_directory
        )

        sys.exit(1)


    # --------------------------------------------------------
    # CREATE LOGS DIRECTORY
    # --------------------------------------------------------

    LOGS_ROOT.mkdir(
        parents=True,
        exist_ok=True
    )


    # --------------------------------------------------------
    # LOG FILE
    # --------------------------------------------------------

    log_file = (
        LOGS_ROOT
        / f"{service_name}.log"
    )


    print("=" * 60)
    print(
        f"Starting {service_name}"
    )
    print("=" * 60)

    print(
        f"Directory: {service_directory}"
    )

    print(
        "Command:",
        " ".join(command)
    )

    print(
        f"Log file: {log_file}"
    )

    print("=" * 60)
    print()


    # --------------------------------------------------------
    # START SERVICE
    # --------------------------------------------------------

    try:

        process = subprocess.Popen(
            command,
            cwd=service_directory,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            shell=False,
        )

    except FileNotFoundError as error:

        print(
            "Could not start service."
        )

        print(
            f"Command not found: {command[0]}"
        )

        print(
            error
        )

        sys.exit(1)

    except Exception as error:

        print(
            "Could not start service."
        )

        print(
            error
        )

        sys.exit(1)


    # --------------------------------------------------------
    # READ OUTPUT
    #
    # Every line is:
    #
    # 1. displayed in the CMD window
    # 2. written to the log file
    # --------------------------------------------------------

    try:

        with open(
            log_file,
            "a",
            encoding="utf-8",
            errors="replace"
        ) as log:

            log.write(
                "\n"
                + "=" * 60
                + "\n"
            )

            log.write(
                f"STARTING {service_name}\n"
            )

            log.write(
                "=" * 60
                + "\n"
            )

            log.flush()


            for line in process.stdout:

                # Display live output
                print(
                    line,
                    end=""
                )

                # Save same output
                log.write(
                    line
                )

                log.flush()


    except KeyboardInterrupt:

        print()
        print(
            f"Stopping {service_name}..."
        )

        process.terminate()


    finally:

        try:

            process.wait(
                timeout=5
            )

        except subprocess.TimeoutExpired:

            process.kill()


    print()

    print(
        f"{service_name} stopped."
    )

    print(
        f"Exit code: {process.returncode}"
    )


# ============================================================
# COMMAND-LINE ARGUMENT
# ============================================================

def main():

    parser = argparse.ArgumentParser(
        description=(
            "Start one Smart Electricity service "
            "and save its console output."
        )
    )

    parser.add_argument(
        "service",
        choices=[
            "meter",
            "billing",
            "prediction",
            "user",
        ],
        help="Service to start"
    )

    args = parser.parse_args()

    run_service(
        args.service
    )


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()