from crewai import Agent, Crew, Task, Process
from crewai.project import CrewBase, agent, task, crew

from presales.config.llm import get_llm


@CrewBase
class ResearchCrew:

    agents_config = "agents.yaml"
    tasks_config = "tasks.yaml"

    @agent
    def company_researcher(self) -> Agent:

        return Agent(
            config=self.agents_config["company_researcher"],
            llm=get_llm(),
        )

    @task
    def research_company(self) -> Task:

        return Task(
            config=self.tasks_config["research_company"],
            agent=self.company_researcher(),
        )

    @crew
    def crew(self) -> Crew:

        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
