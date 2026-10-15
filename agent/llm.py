import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


# ============================================================
# LOAD PROJECT ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# GET MODEL NAME FROM .ENV
# ============================================================

MODEL_NAME = os.getenv(
    "SRE_MODEL",
    "gpt-5-nano"
)


# ============================================================
# CHECK API KEY EXISTS
# ============================================================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


if not OPENAI_API_KEY:
    raise ValueError(
        "OPENAI_API_KEY is missing. "
        "Please add it to the project's .env file."
    )


# ============================================================
# CREATE THE LANGUAGE MODEL
# ============================================================

llm = ChatOpenAI(
    model=MODEL_NAME,
    temperature=0
)


# ============================================================
# SIMPLE TEST FUNCTION
# ============================================================

def test_llm():
    """
    Send a very small message to the LLM.

    This function only tests whether:
    - .env loads correctly
    - API key works
    - LangChain works
    - OpenAI model responds

    It does NOT use our SRE tools yet.
    """

    response = llm.invoke(
        "Reply with exactly: AI SRE LLM CONNECTED"
    )

    return response.content


# ============================================================
# ALLOW THIS FILE TO BE TESTED DIRECTLY
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("Testing AI SRE LLM Connection")
    print("=" * 60)

    result = test_llm()

    print()
    print(result)