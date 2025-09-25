from pydantic import BaseModel
from agents import Agent

no_of_search_terms=10

planner_inst=f"You are a helpful research assistant agent. Given a query, come up with a set of web searches \
to perform to get best answer of query. output {no_of_search_terms} terms to query for."

class websearchitem(BaseModel):
  reason:str
  "Your reasoning for why this search is important to query."

  query:str
  "the search term to use for web search."

class websearchplan(BaseModel):
  searches:list[websearchitem]
  "A list of web searches to perform to best answer the query"

planner_agent=Agent(
    name="Planner Agent",
    instructions=planner_inst,
    model="gpt-4o-mini",
    output_type=websearchplan
)