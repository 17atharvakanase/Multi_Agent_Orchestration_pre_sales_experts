import os

from crewai import LLM


def get_llm():

    provider = os.getenv(
        "LLM_PROVIDER",
        "databricks",
    )

    if provider != "databricks":

        raise ValueError(
            f"Unsupported LLM provider: {provider}"
        )

    return LLM(
        model=(
            "openai/"
            "system.ai.claude-sonnet-5"
        ),

        api_key=os.getenv(
            "DATABRICKS_TOKEN"
        ),

        base_url=(
            "https://adb-4012206601325141.1."
            "azuredatabricks.net/"
            "ai-gateway/mlflow/v1"
        ),
    )