from langchain.agents import create_agent

from agent.llm import llm
from agent.langchain_tools import SRE_TOOLS


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are an AI Site Reliability Engineering (SRE) Incident Agent.

You are responsible for investigating the Smart Electricity System.

The system currently contains these microservices:

- meter-data-service
- billing-service
- prediction-service
- user-service


You have diagnostic tools available.

Your job is to use those tools to investigate the real current
state of the system.


IMPORTANT RULES:

1. Never guess whether a service is healthy.

2. Use the available tools to get real evidence.

3. If the user asks about the whole system,
   first identify or check the available services.

4. If a service is unhealthy or unreachable,
   investigate it further.

5. If a service port is closed, explain that the service
   may be stopped or crashed.

6. If a service port is open but the health endpoint fails,
   explain that the application may have an internal problem
   or dependency problem.

7. Do not claim that you restarted, repaired, stopped,
   or modified a service.

8. The current agent is READ-ONLY.

9. Clearly separate:

   - Evidence
   - Likely cause
   - Recommended next action

10. If there is not enough evidence to determine the exact
    root cause, clearly say so.

11. Do not invent log messages, database errors, HTTP errors,
    ports, or service states.

12. Keep answers clear and concise.
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
# RUN THE AGENT
# ============================================================

def run_sre_agent(user_message: str) -> str:
    """
    Send a user request to the SRE agent.

    LangChain will allow the LLM to decide which tools
    should be called.

    The agent may call multiple tools before producing
    its final answer.
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

        return "The SRE agent returned no response."

    final_message = messages[-1]

    content = final_message.content

    # Usually the final response is a normal string.
    if isinstance(content, str):

        return content

    # Some models may return structured content blocks.
    if isinstance(content, list):

        text_parts = []

        for block in content:

            if isinstance(block, str):

                text_parts.append(block)

            elif isinstance(block, dict):

                text = block.get("text")

                if text:

                    text_parts.append(text)

        if text_parts:

            return "\n".join(text_parts)

    # Fallback
    return str(content)


# ============================================================
# DIRECT TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("AI SRE Incident Agent")
    print("=" * 60)

    print()
    print("The AI now has access to these tools:")

    for tool in SRE_TOOLS:

        print(
            "-",
            tool.name
        )

    print()
    print("=" * 60)
    print("TEST")
    print("=" * 60)

    print()
    print(
        "Request: Investigate the Smart Electricity System "
        "and tell me whether the services are healthy."
    )

    print()
    print("Agent is investigating...")
    print()

    try:

        response = run_sre_agent(
            "Investigate the Smart Electricity System "
            "and tell me whether the services are healthy."
        )

        print("SRE Agent:")
        print()
        print(response)

    except Exception as error:

        print("Agent failed.")
        print()
        print("Error:")
        print(error)