import os

from databricks.sdk import WorkspaceClient


def configure_databricks_auth():

    client = WorkspaceClient(
        host=os.environ[
            "DATABRICKS_HOST"
        ],

        client_id=os.environ[
            "DATABRICKS_CLIENT_ID"
        ],

        client_secret=os.environ[
            "DATABRICKS_CLIENT_SECRET"
        ],
    )

    token = (
        client
        .config
        .oauth_token()
    )

    if not token:

        raise RuntimeError(
            "Could not obtain Databricks OAuth token"
        )

    os.environ[
        "DATABRICKS_TOKEN"
    ] = token

    return token