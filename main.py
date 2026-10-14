import json

from agent.tools import (
    list_services,
    get_service_status,
    diagnose_service,
)


def print_title(title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def main():

    print_title("AI SRE Incident Agent")

    # ---------------------------------------------------------
    # STEP 1
    # Get all services configured in agent/tools.py
    # ---------------------------------------------------------

    services_result = list_services()

    print("\nConfigured Services:")
    print(json.dumps(services_result, indent=2))

    services = services_result.get("services", [])

    # ---------------------------------------------------------
    # STEP 2
    # Check health of every service
    # ---------------------------------------------------------

    print_title("Service Health")

    for service_name in services:

        status_result = get_service_status(service_name)

        print(json.dumps(status_result, indent=2))

        # -----------------------------------------------------
        # STEP 3
        # If the service is not healthy,
        # perform another investigation.
        # -----------------------------------------------------

        if status_result.get("status") != "healthy":

            print("\nInvestigation:")

            diagnosis_result = diagnose_service(service_name)

            print(json.dumps(diagnosis_result, indent=2))

        print("-" * 60)


if __name__ == "__main__":
    main()