from crewai import Agent, Crew, Task, Process
from crewai.project import CrewBase, agent, task, crew

from presales.config.llm import get_llm

@CrewBase
class SolutionArchitectCrew:

    agents_config = "agents.yaml"
    tasks_config = "tasks.yaml"

    # ==========================================
    # AGENT
    # ==========================================

    @agent
    def solution_architect(self) -> Agent:

        return Agent(
            config=self.agents_config[
                "solution_architect"
            ],
            llm = get_llm(),
            verbose=True,
        )

    # ==========================================
    # TASK
    # ==========================================

    @task
    def design_solution(self) -> Task:

        return Task(
            config=self.tasks_config[
                "design_solution"
            ],
            agent=self.solution_architect(),
        )

    # ==========================================
    # CREW
    # ==========================================

    @crew
    def crew(self) -> Crew:

        return Crew(
            agents=[
                self.solution_architect()
            ],

            tasks=[
                self.design_solution()
            ],

            process=Process.sequential,

            verbose=True,
        )