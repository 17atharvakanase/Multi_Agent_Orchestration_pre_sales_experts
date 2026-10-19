from presales.flows.presales_flow import PresalesFlow


def main():

    flow = PresalesFlow()

    result = flow.kickoff()

    print("\n==============================")
    print("WORKFLOW COMPLETED")
    print("==============================")

    print(result)


if __name__ == "__main__":
    main()