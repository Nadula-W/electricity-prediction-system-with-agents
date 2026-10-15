import json

from agent.tools import (
    list_services,
    get_service_status,
    diagnose_service,
)

from agent.sre_agent import run_sre_agent


# ============================================================
# DISPLAY TITLE
# ============================================================

def print_title(title):

    print()
    print("=" * 60)
    print(title)
    print("=" * 60)
    print()


# ============================================================
# NORMAL NON-AI HEALTH CHECK
# ============================================================

def run_manual_health_check():
    """
    Run the original deterministic health check.

    This does NOT use the LLM.

    It directly calls our Python monitoring tools.
    """

    print_title(
        "Smart Electricity System - Manual Health Check"
    )

    services_result = list_services()

    services = services_result.get(
        "services",
        []
    )

    for service_name in services:

        result = get_service_status(
            service_name
        )

        print(
            json.dumps(
                result,
                indent=2
            )
        )

        # If something is wrong,
        # perform our normal port diagnosis.

        if result.get("status") != "healthy":

            print()
            print("Investigation:")

            diagnosis = diagnose_service(
                service_name
            )

            print(
                json.dumps(
                    diagnosis,
                    indent=2
                )
            )

        print("-" * 60)


# ============================================================
# AI SRE INTERACTIVE MODE
# ============================================================

def run_ai_mode():
    """
    Start an interactive command-line conversation
    with the LangChain SRE agent.
    """

    print_title(
        "AI SRE Incident Agent"
    )

    print(
        "The AI can investigate the Smart Electricity System."
    )

    print()

    print(
        "Example commands:"
    )

    print(
        "  Investigate the whole system"
    )

    print(
        "  Check billing-service"
    )

    print(
        "  Is prediction-service healthy?"
    )

    print(
        "  Investigate why billing-service is unavailable"
    )

    print()

    print(
        "Type 'health' for the normal non-AI health check."
    )

    print(
        "Type 'exit' to close the program."
    )

    print()

    # --------------------------------------------------------
    # INTERACTIVE LOOP
    # --------------------------------------------------------

    while True:

        try:

            user_input = input(
                "You: "
            ).strip()

        except KeyboardInterrupt:

            print()
            print("Exiting AI SRE Agent.")
            break

        # ----------------------------------------------------
        # EMPTY INPUT
        # ----------------------------------------------------

        if not user_input:

            continue

        # ----------------------------------------------------
        # EXIT
        # ----------------------------------------------------

        if user_input.lower() in [
            "exit",
            "quit",
            "bye"
        ]:

            print()
            print(
                "AI SRE Agent stopped."
            )

            break

        # ----------------------------------------------------
        # MANUAL HEALTH CHECK
        # ----------------------------------------------------

        if user_input.lower() == "health":

            run_manual_health_check()

            print()

            continue

        # ----------------------------------------------------
        # SEND REQUEST TO LANGCHAIN AGENT
        # ----------------------------------------------------

        print()
        print(
            "SRE Agent is investigating..."
        )
        print()

        try:

            response = run_sre_agent(
                user_input
            )

            print(
                "SRE Agent:"
            )

            print()

            print(
                response
            )

            print()

        except Exception as error:

            print(
                "The SRE Agent encountered an error."
            )

            print()

            print(
                error
            )

            print()


# ============================================================
# MAIN PROGRAM
# ============================================================

def main():

    run_ai_mode()


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()