#!/usr/bin/env python
import sys
import warnings
from datetime import datetime
import os

docker_path = r"C:\Program Files\Docker\Docker\resources\bin"
if docker_path not in os.environ["PATH"]:
    os.environ["PATH"] += os.pathsep + docker_path

from coder_agent.crew import CoderAgent

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")


def run():
    """
    Run the crew.
    """
    assignment = (
        "Write a python program to calculate the first 1000 terms "
        "of Fibonacci series and save it to a file"
    )

    inputs = {
        "assignment": assignment,
        "current_year": str(datetime.now().year),
    }

    try:
        result = CoderAgent().crew().kickoff(inputs=inputs)
        print(result.raw)  # <-- show result in console
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


if __name__ == "__main__":
    run()
