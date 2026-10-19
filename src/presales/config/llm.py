import os
import time

import requests
from crewai import LLM
from dotenv import load_dotenv


load_dotenv()


# Cache the token in memory.
_access_token = None
_token_expires_at = 0


def _get_databricks_token() -> str:
    global _access_token
    global _token_expires_at

    # Reuse token if it is still valid.
    # Refresh 60 seconds before expiry.
    if (
        _access_token
        and time.time() < (_token_expires_at - 60)
    ):
        return _access_token

    host = os.getenv("DATABRICKS_HOST")
    client_id = os.getenv("DATABRICKS_CLIENT_ID")
    client_secret = os.getenv(
        "DATABRICKS_CLIENT_SECRET"
    )

    if not host:
        raise RuntimeError(
            "DATABRICKS_HOST is not set"
        )

    if not client_id:
        raise RuntimeError(
            "DATABRICKS_CLIENT_ID is not set"
        )

    if not client_secret:
        raise RuntimeError(
            "DATABRICKS_CLIENT_SECRET is not set"
        )

    token_url = (
        f"{host.rstrip('/')}/oidc/v1/token"
    )

    response = requests.post(
        token_url,
        auth=(client_id, client_secret),
        data={
            "grant_type": "client_credentials",
            "scope": "all-apis",
        },
        timeout=30,
    )

    response.raise_for_status()

    token_data = response.json()

    _access_token = token_data["access_token"]

    expires_in = token_data.get(
        "expires_in",
        3600,
    )

    _token_expires_at = (
        time.time() + expires_in
    )

    return _access_token


def get_llm():

    provider = os.getenv(
        "LLM_PROVIDER",
        "databricks",
    )

    if provider != "databricks":

        raise ValueError(
            f"Unsupported LLM provider: {provider}"
        )

    token = _get_databricks_token()

    return LLM(
        model=(
            "openai/"
            "system.ai.claude-sonnet-5"
        ),

        api_key=token,

        base_url=(
            "https://adb-4012206601325141.1."
            "azuredatabricks.net/"
            "ai-gateway/mlflow/v1"
        ),

        max_tokens=4096,
    )