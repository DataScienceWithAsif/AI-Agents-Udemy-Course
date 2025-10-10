from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
# from langchain_openai import ChatOpenAI
from langchain.agents import Tool
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
# from langchain_google_genai import ChatGoogleGenerativeAI
from sidekick_tools import other_tools
from langchain_groq import ChatGroq

from typing import Annotated, Any, Dict, List, Optional
from IPython.display import Image, display
from typing_extensions import TypedDict
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import gradio as gr
import requests
import os
import asyncio
import uuid
from datetime import datetime

load_dotenv(override=True)

class State(TypedDict):
    messages: Annotated[list[Any], add_messages]
    success_criteria: str
    feedback_on_work: Optional[str]
    success_criteria_met: bool
    user_input_needed: bool

class EvaluatorOutput(BaseModel):
    feedback: str =Field(description="feedback on the assistant`s response")
    success_criteria_met: bool =Field(description="Whether the success criteria have been met")
    user_input_needed: bool =Field(description="True if more input is needed from the user, or clarifications, or the assistant is stuck")

class Sidekick:
    def __init__(self):
        self.worker_llm_with_tools=None
        self.evaluator_llm_with_output=None
        self.tools=None
        self.llm_with_tools=None
        self.graph=None
        self.sidekick_id= str(uuid.uuid4())
        self.memory = MemorySaver()
        

    async def setup(self):
        self.tools=await other_tools()
        worker_llm=ChatGroq(model="openai/gpt-oss-20b")
        self.worker_llm_with_tools=worker_llm.bind_tools(self.tools)
        evaluator_llm=ChatGroq(model="openai/gpt-oss-20b")
        self.evaluator_llm_with_output=evaluator_llm.with_structured_output(EvaluatorOutput)
        await self.build_graph()

    def worker(self, state: State) -> Dict[str, Any]:
        system_message = f"""You are a helpful assistant that can use tools to complete tasks.
        you keep working on a task untill either you have done and success criteria has been met or 
        you have a question for clarification for the user.
        You have many tools to help you, including tool to browse the internet, nevigating and retrieving web pages,
        send push notification and file management tools.
        the Current date and time is {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    
    SUCCESS CRITERIA: {state["success_criteria"]}
    
    Follow these rules:
    1. FIRST attempt to answer the question directly using your knowledge
    2. If you need current information or additional data, use the search_tool tool
    3. Only ask clarifying questions if the request is truly ambiguous or missing key information
    4. Provide complete, helpful answers that meet the success criteria
    5. When you have a final answer, state it clearly without additional questions
    
    Examples:
    - For "what is current USD/GBP exchange rate": Use search tool and provide the rate
    - For "what are trending AI fields": Provide a comprehensive list based on your knowledge
    - Only ask for clarification if the question is unclear like "tell me about it"
    """

        if state.get("feedback_on_work"):
            system_message += f"""
            PREVIOUS FEEDBACK: {state["feedback_on_work"]}
            Use this feedback to improve your response. Address the issues mentioned.
            """

        found_system_message = False
        messages = state["messages"]
    
        for message in messages:
            if isinstance(message, SystemMessage):
                message.content = system_message
                found_system_message = True
            
        if not found_system_message:
            messages = [SystemMessage(content=system_message)] + messages

        response =self.worker_llm_with_tools.invoke(messages)

        return {
            "messages": [response]
        }

    def work_router(self, state: State) -> str:
        last_response=state['messages'][-1]
    
        if hasattr(last_response, "tool_calls") and last_response.tool_calls:
            return "tools"
        else:
            return "evaluator"

    def format_conversation(self, messages: List[Any]) -> str:
        conversation = "Conversation history:\n\n"

        for message in messages:
            if isinstance(message, HumanMessage):
                conversation +=f"User: {message.content}\n"
            elif isinstance(message, AIMessage):
                text=message.content or "[tools use]"
                conversation += f"Assistant: {text}\n"
    
        return conversation


    def evaluator(self, state: State) -> State:
        last_message = state['messages'][-1]
    
        # MODIFIED SYSTEM MESSAGE
        system_message = """You are an expert evaluator. Your job is to determine if the assistant is making progress.
    
    CRITICAL RULE: If the assistant's response is not improving, is repetitive, or seems stuck after receiving feedback,
    it is YOUR RESPONSIBILITY to stop the loop. In this case, you MUST set 'user_input_needed' to True and provide feedback
    explaining that the assistant is stuck and requires clarification from the user.
    
    Consider these as POSITIVE progress:
    - Assistant used tools to gather information.
    - Assistant provided a substantive answer that is closer to the goal.
    
    Only consider user input needed if:
    - The assistant is stuck and repeating itself (as per the CRITICAL RULE).
    - The original question is truly ambiguous and cannot be answered without more information."""

        user_message = f"""
        CONVERSATION HISTORY:
        {self.format_conversation(state["messages"])}
    
        SUCCESS CRITERIA: {state["success_criteria"]}
    
        LAST RESPONSE: {last_message.content}
    
        Evaluate whether:
        1. The response makes progress toward the success criteria.
        2. The assistant needs clarification (especially if it seems stuck).
        3. The success criteria is fully met.

        Respond with your feedback, and decide if the success criteria is met by this response.
        Also, decide if more input is neede from the user, either becuase the assistant has a question ans needs clarification or assistant seems to be stuck.

        Overall, you should give the assistant the benifit of the doubt if they say they have done something. But you should reject if you feel that working is needed.
        """

        if state.get("feedback_on_work"):
            user_message += f"\\nPREVIOUS FEEDBACK: {state['feedback_on_work']}"

        evaluator_message = [SystemMessage(content=system_message), HumanMessage(content=user_message)]
        evaluation_result = self.evaluator_llm_with_output.invoke(evaluator_message)

        new_state = {
            "feedback_on_work": evaluation_result.feedback,
            "success_criteria_met": evaluation_result.success_criteria_met,
            "user_input_needed": evaluation_result.user_input_needed,
            # Adding the feedback to the message history is better for context
            "messages": [AIMessage(content=f"Evaluator feedback: {evaluation_result.feedback}")]
        }

        return new_state

    def router_based_on_evaluation(self, state: State) -> str:
        if state.get('success_criteria_met', False) or state.get('user_input_needed', False):
            return "END"
        else:
            return "worker"  # This was missing the return statement

    async def build_graph(self):
        # setting up Graph Buillder
        graph_builder=StateGraph(State)

        # adding Nodes
        graph_builder.add_node("worker", self.worker)
        graph_builder.add_node("tools", ToolNode(tools=self.tools))
        graph_builder.add_node("evaluator", self.evaluator)

        # adding Edges
        graph_builder.add_edge(START, "worker")
        graph_builder.add_conditional_edges("worker", self.work_router, {"tools":"tools", "evaluator":"evaluator"})
        graph_builder.add_edge("tools","worker")
        graph_builder.add_conditional_edges("evaluator", self.router_based_on_evaluation, {"worker":"worker", "END":END})

        # Compiling the graph
        memory=MemorySaver()
        self.graph=graph_builder.compile(checkpointer=memory)

    async def run_superstep(self, message, success_criteria, history):
        config={"configurable":{"thread_id":self.sidekick_id}}

        state={
            "messages": message,
            "success_criteria": success_criteria or "The answer should be clear and accurate",
            "feedback_on_work": None,
            "success_criteria_met": False,
            "user_input_needed": False
        }

        result = await self.graph.ainvoke(state, config=config)
        user={"role":"user", "content": message}
        reply={"role":"assistant", "content": result["messages"][-2].content}
        feedback={"role":"assistant", "content": result["messages"][-1].content}

        return history + [user, reply, feedback]