from crewai import Agent, Crew, Task, Process
from crewai.project import CrewBase, agent, task, crew

from presales.config.llm import get_llm

@CrewBase
class SynthesisCrew:

    agents_config = "agents.yaml"
    tasks_config = "tasks.yaml"

    @agent
    def presales_strategist(self) -> Agent:

        return Agent(
            config=self.agents_config["presales_strategist"],
            llm=get_llm(),
        )

    @task
    def synthesize_analysis(self) -> Task:

        return Task(
            config=self.tasks_config["synthesize_analysis"],
            agent=self.presales_strategist(),
        )

    @crew
    def crew(self) -> Crew:

        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )