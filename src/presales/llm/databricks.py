import os

from openai import OpenAI
from databricks.sdk import WorkspaceClient
from dotenv import load_dotenv


load_dotenv()


DATABRICKS_BASE_URL = (
    "https://adb-4012206601325141.1."
    "azuredatabricks.net/"
    "ai-gateway/mlflow/v1"
)


def get_databricks_token() -> str:

    host = os.environ["DATABRICKS_HOST"]

    client_id = os.environ[
        "DATABRICKS_CLIENT_ID"
    ]

    client_secret = os.environ[
        "DATABRICKS_CLIENT_SECRET"
    ]

    workspace_client = WorkspaceClient(
        host=host,
        client_id=client_id,
        client_secret=client_secret,
    )

    token = (
        workspace_client
        .config
        .oauth_token()
    )

    if not token:
        raise RuntimeError(
            "Unable to obtain Databricks OAuth token"
        )

    return token


def get_databricks_client() -> OpenAI:

    token = get_databricks_token()

    return OpenAI(
        api_key=token,
        base_url=DATABRICKS_BASE_URL,
    )