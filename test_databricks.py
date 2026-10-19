from presales.config.llm import get_llm


def main():

    print("Creating Databricks LLM...")

    llm = get_llm()

    print("LLM created successfully")

    response = llm.call(
        "Explain Databricks in one sentence."
    )

    print("\n==============================")
    print("RESPONSE")
    print("==============================")

    print(response)


if __name__ == "__main__":
    main()