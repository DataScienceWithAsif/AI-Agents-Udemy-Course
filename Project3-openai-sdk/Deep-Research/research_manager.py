from agents import Runner, trace, gen_trace_id
from search_agent import search_agent
from planner_agent import planner_agent, websearchitem, websearchplan
from writer_agent import writer_agent, ReportData
from email_agent import email_agent
import asyncio

class ResearchManager:
    
    async def run(self, query:str):
        """Run the Deep research process, yeilding the status updates and final report"""
        trace_id=gen_trace_id()
        
        with trace("Deep-Research trace",trace_id=trace_id):
            print(f"view trace: https://platform.openai.com/traces/{trace_id}")
            yield "view trace: https://platform.openai.com/traces/{trace_id}"
            print("starting Research.....")
            search_plan=await self.plan_searches(query)
            yield "Searches planned, starting search....."
            search_results=await self.perform_searches(search_plan)
            yield "Searches complete, writing report....."
            report=await self.write_report(query, search_results)
            yield "Report written, sending Email....."
            await self.email_sender(report)
            yield "Email sent, research complete"
            yield report.markdown_report
            
    
    async def plan_searches(self,query: str) -> websearchplan :
        """Use the planner agent to plan which searches to run for query"""
        print("Planning Searhes......")
        result=await Runner.run(planner_agent, f"Query: {query}")
        return result.final_output_as(websearchplan)
    
    async def perform_searches(self, search_plan: websearchplan) -> list[str]:
        print("Searching...........")
        num_completed=0
        tasks=[asyncio.create_task(self.search(item)) for item in search_plan.searches] # Iterate over search_plan.searches
        results=[]
        for task in asyncio.as_completed(tasks):
            result=await task
            if result is not None:
                results.append(result)
            num_completed +=1
            print(f"Searching... {num_completed}/{len(tasks)} completed")
        print("Finished Searching.....")
        return results
    
    async def search(self, item: websearchitem) -> str|None:
        """Perform a search for the query"""
        input=f"Search term: {item.query}\n Reason for searching: {item.reason}"
        try:
            result=await Runner.run(
                search_agent,
                input
                )
            return str(result.final_output)
        except Exception:
            return None
        
    async def write_report(self, query: str, search_results: list[str]) -> ReportData:
        print("Thinking about Report......")
        input=f"Original query: {query}\nSummarized search results: {search_results}"
        result=await Runner.run(writer_agent, input)
        print("Finished Writing Report.....")
        return result.final_output_as(ReportData)
    
    async def email_sender(self, report: ReportData) -> None:
        print("Writing Email........")
        result=await Runner.run(email_agent, report.markdown_report)
        print("Email sent....")
        return report
                

    
    
             