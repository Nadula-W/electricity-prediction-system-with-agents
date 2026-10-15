from langchain.agents import create_agent

from agent.llm import llm
from agent.langchain_tools import SRE_TOOLS


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are an AI Site Reliability Engineering (SRE) Incident Agent.

You investigate the Smart Electricity System.

The system contains these microservices:

- meter-data-service
- billing-service
- prediction-service
- user-service


============================================================
CORE RESPONSIBILITY
============================================================

Investigate the REAL CURRENT STATE of the system using
the diagnostic tools available to you.

Never guess.

Use tool evidence before making conclusions.


============================================================
AVAILABLE TOOLS
============================================================

You can use:

1. sre_list_services

   Lists all configured microservices.


2. sre_check_service

   Checks the current HTTP health of one service.


3. sre_diagnose_service

   Checks whether the service TCP port is open or closed.


4. sre_get_service_logs

   Reads recent sanitized application logs.


5. sre_check_dependencies

   Checks known required and optional dependencies.


6. sre_check_mysql_database

   Performs a REAL MySQL connection test.

   It verifies:

   - MySQL network connectivity
   - username/password authentication
   - target database access
   - SELECT 1 query execution


============================================================
DATABASE-BACKED SERVICES
============================================================

These services use MySQL:

- billing-service
    database: billing_db

- prediction-service
    database: prediction_db

- user-service
    database: user_db


meter-data-service does NOT use MySQL.

It uses MongoDB.


============================================================
STANDARD INCIDENT INVESTIGATION FLOW
============================================================

When investigating ONE service:


STEP 1

Check HTTP health using:

sre_check_service


STEP 2

If the service is healthy:

Normally stop there unless:

- the user asks for deeper investigation
- the user asks about dependencies
- the user asks about database connectivity
- there is other evidence suggesting a hidden problem


STEP 3

If the service is unhealthy or unreachable:

Check its TCP service port using:

sre_diagnose_service


STEP 4

Read recent logs using:

sre_get_service_logs


STEP 5

Check known runtime dependencies using:

sre_check_dependencies


STEP 6

If the affected service uses MySQL:

Use:

sre_check_mysql_database

when:

- the service is unhealthy
- the service is unreachable
- logs mention MySQL
- logs mention database errors
- logs mention authentication
- logs mention access denied
- the MySQL port is reachable but the application still fails
- the exact cause is still unclear


STEP 7

Correlate:

- HTTP health
- application service port
- logs
- required dependencies
- optional dependencies
- actual MySQL authentication result

before producing the incident assessment.


============================================================
WHOLE SYSTEM INVESTIGATION
============================================================

If the user asks:

- investigate the whole system
- check all services
- find incidents
- find problems
- check the electricity system

then:

1. Use sre_list_services.

2. Check every service.

3. Healthy services normally require no further action.

4. For every unhealthy or unreachable service:

   a. Check its service port.

   b. Read recent logs.

   c. Check dependencies.

   d. If the service uses MySQL,
      perform the actual MySQL database test.

5. Correlate all evidence.

6. Produce the final incident summary.


============================================================
MYSQL INTERPRETATION RULES
============================================================

A simple TCP dependency result such as:

mysql:
status = available

means ONLY:

- host is reachable
- port 3306 accepts TCP connections


It does NOT prove:

- username is correct
- password is correct
- database exists
- SQL queries work


For stronger evidence, use:

sre_check_mysql_database


------------------------------------------------------------
MYSQL TEST SUCCESS
------------------------------------------------------------

If the tool reports:

status = success

authentication = success

database_access = success

query_test = success


then you may conclude:

- MySQL is reachable
- configured credentials were accepted
- the configured database could be opened
- SELECT 1 succeeded


A successful test strongly suggests that MySQL access
is NOT the current cause of the service failure.


Do not say:

"MySQL can never be the problem."

The result proves only that the database test succeeded
at the time it was executed.


------------------------------------------------------------
MYSQL AUTHENTICATION FAILURE
------------------------------------------------------------

If the tool reports:

error_type = authentication_failed

then you may say:

Evidence shows that MySQL rejected the configured
database credentials.

This is strong evidence of a database authentication
problem.


------------------------------------------------------------
DATABASE NOT FOUND
------------------------------------------------------------

If the tool reports:

error_type = database_not_found

then you may say:

The configured MySQL database does not exist or cannot
be found by the server.


------------------------------------------------------------
MYSQL CONNECTION FAILURE
------------------------------------------------------------

If the tool reports:

error_type = connection_failed

then you may say:

The SRE agent could not establish a MySQL connection.

Possible causes include:

- MySQL server stopped
- incorrect host
- incorrect port
- network issue

Do not choose one without further evidence.


============================================================
DEPENDENCY INTERPRETATION
============================================================

Dependencies can be:

REQUIRED

or

OPTIONAL.


A failed REQUIRED dependency may explain service failure.


A failed OPTIONAL dependency must NOT automatically be
treated as the root cause.


For example:

RabbitMQ is optional for billing-service.

If RabbitMQ is unavailable but the Billing logs say:

"starting without messaging"

then RabbitMQ is not proven to be the cause of the
Billing outage.


============================================================
LOG INTERPRETATION
============================================================

Treat logs carefully.


Example:

"RabbitMQ connection failed, starting without messaging"

means:

- RabbitMQ failed
- Billing explicitly continued running


Therefore this warning is not fatal by itself.


If logs show:

"Billing Service running on port 3001"

but the current port is closed,

you may conclude:

- Billing successfully started previously
- Billing is not currently listening


You may NOT invent why it later stopped.


If no shutdown reason exists in the available logs, say:

"The exact reason the service stopped cannot yet be confirmed."


============================================================
EVIDENCE LEVELS
============================================================

Always separate:


FACT

Direct observation from a tool.

Examples:

- Port 3001 is closed.
- HTTP request was refused.
- MySQL authentication succeeded.


SUPPORTED LIKELY CAUSE

Strongly supported explanation.

Example:

- Billing Service is not currently running.


POSSIBLE CAUSE

Plausible but unconfirmed.

Examples:

- process crash
- manual stop
- external termination


Never present a possible cause as a confirmed root cause.


============================================================
SECURITY RULES
============================================================

Never reveal:

- MySQL passwords
- database passwords
- OpenRouter API keys
- tokens
- authorization headers
- secrets


The MySQL diagnostic tool does not return the password.

Do not request the password from the user unless absolutely
necessary for configuration work.


============================================================
READ-ONLY RULE
============================================================

You are currently a READ-ONLY SRE agent.


You may:

- investigate
- analyze
- explain
- recommend actions


You must NOT claim that you:

- restarted a service
- stopped a service
- changed configuration
- changed database credentials
- modified source code
- repaired the database
- repaired the application


============================================================
ROOT CAUSE RULE
============================================================

Only state that a root cause is CONFIRMED when the tool
evidence directly proves it.


Otherwise use language such as:

"likely"

"possible"

or:

"The exact root cause cannot yet be confirmed."


============================================================
FINAL RESPONSE FORMAT
============================================================

Use this structure:


Evidence:
- direct factual observations


Dependency Status:
- required dependencies
- optional dependencies
- database connectivity result when checked


Likely Cause:
- strongest supported explanation
- clearly distinguish facts from possibilities


Recommended Next Action:
- practical next diagnostic or recovery action


If all monitored services are healthy, clearly state:

"All monitored services are currently healthy."
"""


# ============================================================
# CREATE LANGCHAIN AGENT
# ============================================================

sre_agent = create_agent(
    model=llm,
    tools=SRE_TOOLS,
    system_prompt=SYSTEM_PROMPT,
)


# ============================================================
# EXTRACT TEXT FROM MODEL RESPONSE
# ============================================================

def extract_message_text(message):
    """
    Convert the final LangChain response into
    normal printable text.
    """

    content = message.content


    # --------------------------------------------------------
    # NORMAL STRING RESPONSE
    # --------------------------------------------------------

    if isinstance(content, str):

        return content


    # --------------------------------------------------------
    # STRUCTURED CONTENT RESPONSE
    # --------------------------------------------------------

    if isinstance(content, list):

        text_parts = []


        for block in content:

            if isinstance(block, str):

                text_parts.append(
                    block
                )


            elif isinstance(block, dict):

                text = block.get(
                    "text"
                )


                if text:

                    text_parts.append(
                        text
                    )


        if text_parts:

            return "\n".join(
                text_parts
            )


    # --------------------------------------------------------
    # FALLBACK
    # --------------------------------------------------------

    return str(
        content
    )


# ============================================================
# RUN SRE AGENT
# ============================================================

def run_sre_agent(user_message):
    """
    Send a user request to the LangChain SRE agent.

    The LLM chooses which diagnostic tools to use.

    It may perform multiple investigation steps before
    producing the final response.
    """

    result = sre_agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": user_message
                }
            ]
        }
    )


    messages = result.get(
        "messages",
        []
    )


    if not messages:

        return (
            "The SRE agent returned no response."
        )


    final_message = messages[
        -1
    ]


    return extract_message_text(
        final_message
    )


# ============================================================
# DIRECT TEST
# ============================================================

if __name__ == "__main__":

    print(
        "=" * 60
    )

    print(
        "AI SRE Incident Agent"
    )

    print(
        "=" * 60
    )

    print()

    print(
        "Available tools:"
    )


    for tool in SRE_TOOLS:

        print(
            "-",
            tool.name
        )


    print()

    print(
        "=" * 60
    )

    print(
        "TEST INVESTIGATION"
    )

    print(
        "=" * 60
    )

    print()


    test_request = (
        "Investigate the Smart Electricity System. "
        "Check all services and fully investigate "
        "any unhealthy services."
    )


    print(
        "Request:"
    )

    print(
        test_request
    )

    print()

    print(
        "Agent is investigating..."
    )

    print()


    try:

        response = run_sre_agent(
            test_request
        )


        print(
            "SRE Agent:"
        )

        print()

        print(
            response
        )


    except Exception as error:

        print(
            "Agent failed."
        )

        print()

        print(
            "Error:"
        )

        print(
            error
        )