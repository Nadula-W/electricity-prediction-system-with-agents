import json

from agent.tools import (
    list_services,
    get_service_status
)


def main():

    print("\nAI SRE Incident Agent")
    print("=" * 50)

    services = list_services()

    print("\nConfigured Services:")
    print(
        json.dumps(
            services,
            indent=2
        )
    )

    print("\nService Health")
    print("=" * 50)

    for service in services["services"]:

        result = get_service_status(service)

        print(
            json.dumps(
                result,
                indent=2
            )
        )


if __name__ == "__main__":
    main()