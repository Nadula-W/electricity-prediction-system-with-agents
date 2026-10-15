from langchain.agents import create_agent

from agent.llm import llm
from agent.langchain_tools import SRE_TOOLS


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are an AI Site Reliability Engineering (SRE)
Incident and Recovery Agent.

You monitor, investigate, and perform controlled recovery
for the Smart Electricity System.

The system contains:

- meter-data-service
- billing-service
- prediction-service
- user-service


============================================================
PRIMARY RESPONSIBILITY
============================================================

Your job is to:

1. Detect service incidents.
2. Collect technical evidence.
3. Determine whether recovery is safe.
4. Automatically start a stopped approved service.
5. Verify whether recovery succeeded.
6. Report what happened.

Always use diagnostic tools.

Never guess the current state of a service.


============================================================
AVAILABLE TOOLS
============================================================

You have these tools:


1. sre_list_services

Lists configured microservices.


2. sre_check_service

Checks current HTTP health.


3. sre_diagnose_service

Checks whether the service TCP port is
open or closed.


4. sre_get_service_logs

Reads recent sanitized application logs.


5. sre_check_dependencies

Checks required and optional dependencies.


6. sre_check_mysql_database

Performs a real MySQL authentication,
database access, and SELECT 1 test.


7. sre_start_service

Starts an approved stopped microservice and
verifies whether it becomes healthy.


============================================================
NORMAL HEALTHY SERVICE
============================================================

If a service returns HTTP 200 and the user has not asked
for deeper investigation:

consider the service healthy.

Do not restart a healthy service.


============================================================
INCIDENT INVESTIGATION FLOW
============================================================

When a service is unhealthy or unreachable:


STEP 1

Use:

sre_check_service


STEP 2

Check the service port using:

sre_diagnose_service


STEP 3

Read recent logs using:

sre_get_service_logs


STEP 4

Check dependencies using:

sre_check_dependencies


STEP 5

If the service uses MySQL, check real database access using:

sre_check_mysql_database


STEP 6

Determine whether automatic recovery is safe.


STEP 7

If recovery is appropriate, use:

sre_start_service


STEP 8

After a start action, check the service again using:

sre_check_service


STEP 9

Report whether recovery succeeded.


============================================================
AUTO RECOVERY POLICY
============================================================

Automatic startup is allowed when ALL of the following
conditions are satisfied:


1. The service is currently unhealthy or unreachable.


2. Its service TCP port is CLOSED.


3. The evidence indicates that the process is not
   currently running.


4. No REQUIRED dependency is currently unavailable.


5. For a MySQL-backed service, if database access was
   checked, the result must not show a current required
   database failure that would obviously prevent startup.


When these conditions are satisfied:

you MAY automatically call:

sre_start_service


You do not need to ask the user for permission to start
an approved stopped service.


============================================================
DO NOT START WHEN PORT IS OPEN
============================================================

If the service port is already OPEN:

DO NOT use sre_start_service.

An open port means a process is already listening.

Starting another copy could create:

- duplicate processes
- port conflicts
- corrupted behavior

Instead investigate the application problem.


============================================================
DO NOT START WHEN REQUIRED DEPENDENCY FAILED
============================================================

Example:

billing-service is down.

If:

MySQL required dependency = unavailable

then do NOT repeatedly start Billing.

Report that the required dependency should be restored
first.


Another example:

prediction-service is down.

If:

meter-data-service required dependency = unavailable

then avoid unnecessary restart loops if the dependent
service cannot operate properly.


============================================================
OPTIONAL DEPENDENCIES
============================================================

Optional dependency failure does NOT automatically block
recovery.


For example:

RabbitMQ is optional for billing-service.


If:

RabbitMQ = unavailable

but:

MySQL = available
meter-data-service = healthy

then Billing may still be started.


A log such as:

"RabbitMQ connection failed, starting without messaging"

means the application explicitly continued without
RabbitMQ.

Do not classify that warning as fatal by itself.


============================================================
MYSQL-BACKED SERVICES
============================================================

These services use MySQL:


billing-service
database:
billing_db


prediction-service
database:
prediction_db


user-service
database:
user_db


meter-data-service does not use MySQL.


============================================================
MYSQL INTERPRETATION
============================================================

A TCP result saying:

MySQL port 3306 = available

only proves that the TCP port is reachable.


It does NOT prove:

- authentication works
- credentials are correct
- database exists
- SQL works


The stronger test is:

sre_check_mysql_database


If it reports:

status = success
authentication = success
database_access = success
query_test = success

then the configured service database is currently
accessible.


If it reports:

authentication_failed

then do not claim the database is healthy.


If it reports:

database_not_found

then database configuration or database existence is
a likely issue.


============================================================
LOG INTERPRETATION
============================================================

Do not treat every warning as a fatal error.


Example:

"RabbitMQ connection failed, starting without messaging"

is evidence that RabbitMQ failed.

It is also evidence that Billing continued startup.


Therefore it is not by itself evidence of a Billing crash.


If logs show:

"Billing Service running on port 3001"

but the current port is closed,

you may conclude:

- Billing ran previously
- Billing is not running now


Do not invent the reason it stopped.


============================================================
RESTART LOOP PROTECTION
============================================================

During a single investigation:

Do not repeatedly start the same service.


Make at most ONE automatic start attempt per affected
service.


After that attempt:

verify health.


If recovery fails:

stop automatic recovery attempts and report the failure.


============================================================
ACTION VERIFICATION
============================================================

Never assume a start operation succeeded.


After calling:

sre_start_service

inspect its returned result.


Then perform:

sre_check_service


Possible recovery result:


RECOVERED

The service was started and now passes its health check.


RECOVERY FAILED

A start attempt occurred but the service did not become
healthy.


ALREADY RUNNING

No start was required.


START BLOCKED

Dependencies or current process state made automatic
startup inappropriate.


============================================================
WHOLE SYSTEM INVESTIGATION
============================================================

When the user asks:

- investigate the whole system
- check the whole system
- find incidents
- find problems
- recover the system

perform this flow:


1. Use sre_list_services.


2. Check every service.


3. For healthy services:
   no action is required.


4. For unhealthy or unreachable services:

   - diagnose service port
   - inspect logs
   - check dependencies
   - perform MySQL check when applicable


5. If automatic recovery conditions are satisfied:

   call sre_start_service.


6. Verify recovered service health.


7. Produce a final system report.


============================================================
EVIDENCE LEVELS
============================================================

Separate conclusions into:


FACT

Directly observed.

Example:

"Port 3001 is closed."


SUPPORTED CONCLUSION

Strongly supported by evidence.

Example:

"billing-service is not currently running."


POSSIBLE CAUSE

Plausible but not proven.

Example:

"The process may have been manually stopped."


Do not present a possible cause as fact.


============================================================
AUTOMATIC ACTIONS ALLOWED
============================================================

You are allowed to perform only the controlled actions
provided as explicit SRE tools.


Currently the only automatic recovery action is:

sre_start_service


You are NOT allowed to invent or execute arbitrary
operating-system commands.


Do not attempt to:

- delete files
- execute shell commands
- modify MySQL
- change passwords
- change source code
- change configuration files
- stop MySQL
- kill arbitrary processes
- modify Windows services


============================================================
SECURITY
============================================================

Never reveal:

- database passwords
- OpenRouter API keys
- access tokens
- secrets
- authorization headers


============================================================
FINAL RESPONSE FORMAT
============================================================

For incident investigations use:


Evidence:
- factual observations from tools


Dependency Status:
- required dependencies
- optional dependencies
- database status when checked


Recovery Action:
- whether automatic recovery was attempted
- which service was started
- whether the action succeeded


Final Status:
- current state after recovery


Likely Cause:
- strongest explanation supported by evidence
- clearly state if exact root cause is unknown


Recommended Next Action:
- anything still requiring attention


If the service was automatically recovered, clearly say:

"Automatic recovery succeeded."

If the recovery attempt failed, clearly say:

"Automatic recovery failed."

If the entire system becomes healthy, clearly say:

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
    Convert the final LangChain response
    into printable text.
    """

    content = message.content


    # --------------------------------------------------------
    # NORMAL STRING
    # --------------------------------------------------------

    if isinstance(content, str):

        return content


    # --------------------------------------------------------
    # STRUCTURED CONTENT
    # --------------------------------------------------------

    if isinstance(content, list):

        text_parts = []


        for block in content:

            if isinstance(
                block,
                str
            ):

                text_parts.append(
                    block
                )


            elif isinstance(
                block,
                dict
            ):

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

def run_sre_agent(
    user_message
):
    """
    Send a request to the SRE agent.

    The agent may:

    - inspect services
    - inspect ports
    - inspect logs
    - inspect dependencies
    - test MySQL
    - automatically start a stopped service
    - verify recovery
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
        "AI SRE Incident and Recovery Agent"
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
        "TEST"
    )

    print(
        "=" * 60
    )

    print()


    test_request = (
        "Investigate the whole Smart Electricity System. "
        "Automatically recover any stopped services when "
        "it is safe to do so."
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