from pydantic import BaseModel
from agents import Agent

writer_agent_inst="You are a senior researcher agent tasked with writing a cohesive report for research query. \
You will be given with original query and some intial research done by a research asstant. \
You should first come up with an outline for the report that describes the structure and \
flow of the report.Then, generate the report and return that as your final report. \
The final report should be in markdoen format, and it should be lengthy and detailed. \
Aim for 5-10 pages of content, at least 1000 words."

class ReportData(BaseModel):
  short_summary:str
  """A short 2-3 sentences summary of the findings."""
  markdown_report:str
  """The final Markdown format Report"""
  follow_up_questions:list[str]
  """Suggested Topics to research further."""

writer_agent=Agent(
    name="WriterAgent",
    instructions=writer_agent_inst,
    model="gpt-4o-mini",
    output_type=ReportData
)