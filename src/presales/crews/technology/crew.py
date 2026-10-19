from crewai import Agent, Crew, Task, Process
from crewai.project import CrewBase, agent, task, crew

from presales.config.llm import get_llm

@CrewBase
class TechnologyCrew:

    agents_config = "agents.yaml"
    tasks_config = "tasks.yaml"

    @agent
    def technology_analyst(self) -> Agent:

        return Agent(
            config=self.agents_config["technology_analyst"],
            llm=get_llm(),
        )

    @task
    def analyze_technology(self) -> Task:

        return Task(
            config=self.tasks_config["analyze_technology"],
            agent=self.technology_analyst(),
        )

    @crew
    def crew(self) -> Crew:

        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
