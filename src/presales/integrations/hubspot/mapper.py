def normalize_company(company: dict) -> dict:

    properties = company.get("properties", {})

    employees = properties.get("numberofemployees")
    revenue = properties.get("annualrevenue")

    return {
        "hubspot_company_id": company.get("id"),

        "company": {
            "name": properties.get("name"),
            "domain": properties.get("domain"),
            "industry": properties.get("industry"),
            "type": properties.get("type"),
            "city": properties.get("city"),
            "state": properties.get("state"),
            "postal_code": properties.get("zip"),

            "employees": (
                int(employees)
                if employees
                else None
            ),

            "annual_revenue": (
                float(revenue)
                if revenue
                else None
            ),

            "timezone": properties.get("timezone"),
            "description": properties.get("description"),
            "linkedin": properties.get(
                "linkedin_company_page"
            ),
        }
    }