import json

from agent.tools import list_services, get_service_status


def print_title(title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def main():

    print_title("AI SRE Incident Agent")

    # ---------------------------------------------------------
    # 1. Show all services configured in agent/tools.py
    # ---------------------------------------------------------

    services_result = list_services()

    print("\nConfigured Services:")
    print(json.dumps(services_result, indent=2))

    services = services_result.get("services", [])

    # ---------------------------------------------------------
    # 2. Check every service
    # ---------------------------------------------------------

    print_title("Service Health")

    for service_name in services:

        result = get_service_status(service_name)

        print(json.dumps(result, indent=2))
        print("-" * 60)


if __name__ == "__main__":
    main()