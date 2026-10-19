import os
import requests

from dotenv import load_dotenv


load_dotenv()


class HubSpotClient:

    BASE_URL = "https://api.hubapi.com"

    def __init__(self):

        self.access_token = os.getenv(
            "HUBSPOT_ACCESS_TOKEN"
        )

        if not self.access_token:
            raise ValueError(
                "HUBSPOT_ACCESS_TOKEN is not configured in .env"
            )

        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    def list_companies(self, limit: int = 100):

        url = (
            f"{self.BASE_URL}"
            "/crm/objects/2026-03/companies"
        )

        params = {
            "limit": limit,
            "properties": (
                "name,"
                "domain,"
                "industry,"
                "type,"
                "city,"
                "state,"
                "zip,"
                "numberofemployees,"
                "annualrevenue,"
                "timezone,"
                "description,"
                "linkedin_company_page"
            ),
        }

        response = requests.get(
            url,
            headers=self.headers,
            params=params,
            timeout=30,
        )

        response.raise_for_status()

        return response.json()

    def get_company(self, company_id: str):

        url = (
            f"{self.BASE_URL}"
            f"/crm/objects/2026-03/companies/{company_id}"
        )

        params = {
            "properties": (
                "name,"
                "domain,"
                "industry,"
                "type,"
                "city,"
                "state,"
                "zip,"
                "numberofemployees,"
                "annualrevenue,"
                "timezone,"
                "description,"
                "linkedin_company_page"
            )
        }

        response = requests.get(
            url,
            headers=self.headers,
            params=params,
            timeout=30,
        )

        response.raise_for_status()

        return response.json()