from agents import Agent, WebSearchTool, ModelSettings

search_agent_inst="You are a research assistant agent.Given a search term, you search the web for that term and \
produces a concise summary of results.summary must be of 2-3 paragraphs and less than 300 words. \
Capture the main points. Write Succintly, no need to have complete sentences or good grammer. \
This will be used by someone synthesizing a report, so it's vital you capture the essence and ignore any fluff. \
Do not include any additional commentary other than the summary itself."

search_agent=Agent(
    name="search agent",
    instructions=search_agent_inst,
    tools=[WebSearchTool(search_context_size='low')],
    model="gpt-4o-mini", 
    model_settings=ModelSettings(tool_choice="required")
)