AGENT_REGISTRY = [

    {
        "name": "company_researcher",
        "description": (
            "Researches company business, "
            "products, customers and opportunities."
        ),
        "inputs": [
            "company_profile"
        ],
        "outputs": [
            "company_research"
        ],
    },

    {
        "name": "technology_analyst",
        "description": (
            "Analyzes technology stack, "
            "cloud, AI and engineering maturity."
        ),
        "inputs": [
            "company_profile"
        ],
        "outputs": [
            "technology_analysis"
        ],
    },
    
    {
        "name": "solution_architect",

        "description": (
            "Designs a technical solution based "
            "on company research and technology analysis."
        ),

        "inputs": [
            "company_research",
            "technology_analysis"
        ],

        "outputs": [
            "solution_design"
        ],
    },

    {
        "name": "presales_strategist",
        "description": (
            "Creates final presales strategy."
        ),
        "inputs": [
            "solution_design"
        ],
        "outputs": [
            "presales_strategy"
        ],
    },
]