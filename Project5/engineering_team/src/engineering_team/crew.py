from crewai_tools import CodeInterpreterTool
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List


@CrewBase
class EngineeringTeam():
    """EngineeringTeam crew"""

    agents: List[BaseAgent]
    tasks: List[Task]
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    # my_code_tool = CodeInterpreterTool(
    # docker_command_path="C:\\Program Files\\Docker\\Docker\\resources\\bin\\docker.exe"
    # )

    
    @agent
    def engineering_lead(self) -> Agent:
        return Agent(
            config=self.agents_config['engineering_lead'], # type: ignore[index]
            verbose=True
        )

    @agent
    def backend_engineer(self) -> Agent:
        return Agent(
            config=self.agents_config['backend_engineer'], # type: ignore[index]
            verbose=True,
            # allow_code_execution=True, # This is needed for code execution. But there is docker compatible issue in my pc
            # code_execution_mode="safe",
            # tools=[self.my_code_tool],
            # max_execution_time=500,
            # max_retry_limit=5
            allow_code_execution=False
        )

    @agent
    def frontend_engineer(self) -> Agent:
        return Agent(
            config=self.agents_config['frontend_engineer'], # type: ignore[index]
            verbose=True
        )

    @agent
    def evaluation_engineer(self) -> Agent:
        return Agent(
            config=self.agents_config['evaluation_engineer'], # type: ignore[index]
            verbose=True
        )

    @agent
    def test_engineer(self) -> Agent:
        return Agent(
            config=self.agents_config['test_engineer'], # type: ignore[index]
            verbose=True,
            # allow_code_execution=True,
            # tools=[self.my_code_tool],
            # code_execution_mode="safe",
            # max_execution_time=500,
            # max_retry_limit=5
            allow_code_execution=False
        )

    @task
    def design_task(self) -> Task:
        return Task(
            config=self.tasks_config['design_task'], # type: ignore[index]
        )

    @task
    def code_task(self) -> Task:
        return Task(
            config=self.tasks_config['code_task'], # type: ignore[index]
        )
    
    @task
    def frontend_task(self) -> Task:
        return Task(
            config=self.tasks_config['frontend_task'], # type: ignore[index]
        )
    
    @task
    def evaluation_task(self) -> Task:
        return Task(
            config=self.tasks_config['evaluation_task'], # type: ignore[index]
        )

    @task
    def test_task(self) -> Task:
        return Task(
            config=self.tasks_config['test_task'], # type: ignore[index]
        )

    @crew
    def crew(self) -> Crew:
        """Creates the EngineeringTeam crew"""

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
