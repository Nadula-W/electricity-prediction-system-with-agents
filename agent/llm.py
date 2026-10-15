import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_openrouter import ChatOpenRouter


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

ENV_FILE = PROJECT_ROOT / ".env"


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv(ENV_FILE)


# ============================================================
# READ OPENROUTER SETTINGS
# ============================================================

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

MODEL_NAME = os.getenv(
    "SRE_MODEL",
    "openrouter/free"
)


# ============================================================
# CHECK API KEY
# ============================================================

if not OPENROUTER_API_KEY:

    raise ValueError(
        "OPENROUTER_API_KEY is missing.\n"
        "Please add your OpenRouter API key to the .env file."
    )


# ============================================================
# CREATE OPENROUTER LLM
# ============================================================

llm = ChatOpenRouter(
    model=MODEL_NAME,
    api_key=OPENROUTER_API_KEY,
    temperature=0,
    max_retries=2,
)


# ============================================================
# TEST FUNCTION
# ============================================================

def test_llm():
    """
    Test whether:

    1. .env is loading
    2. OpenRouter API key is valid
    3. LangChain can connect to OpenRouter
    4. A free model can return a response

    No SRE tools are used yet.
    """

    response = llm.invoke(
        "Reply with exactly these words: AI SRE LLM CONNECTED"
    )

    return response.content


# ============================================================
# RUN DIRECT TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("Testing AI SRE OpenRouter Connection")
    print("=" * 60)

    print()
    print("Model:", MODEL_NAME)

    try:

        result = test_llm()

        print()
        print("Response:")
        print(result)

    except Exception as error:

        print()
        print("OpenRouter connection failed.")
        print()
        print("Error:")
        print(error)