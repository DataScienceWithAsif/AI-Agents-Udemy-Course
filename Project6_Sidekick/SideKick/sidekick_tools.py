from langchain.agents import Tool
from langchain_community.agent_toolkits import FileManagementToolkit
from langchain_community.agent_toolkits.connery import toolkit
from langchain_community.tools.wikipedia.tool import WikipediaQueryRun
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_community.utilities.wikipedia import WikipediaAPIWrapper

from dotenv import load_dotenv
import requests
import os


load_dotenv(override=True)
PUSHOVER_USER=os.getenv("PUSHOVER_USER")
PUSHOVER_TOKEN=os.getenv("PUSHOVER_TOKEN")
PUSHOVER_URL=" https://api.pushover.net/1/messages.json"
serper=GoogleSerperAPIWrapper()

def push(text: str):
    """Send a push notification to the user"""
    requests.post(PUSHOVER_URL, data={"token":PUSHOVER_TOKEN, "user":PUSHOVER_USER, "message":text})
    return "success"

def get_file_tools():
    toolkit=FileManagementToolkit(root_dir="sandbox")
    return toolkit.get_tools()

async def other_tools():
    push_tool=Tool(
        name="send_push_notification",
        func=push,
        description="Use this tool when you want to send a push notification"
    )
    file_tools=get_file_tools()
    search_tool=Tool(
        name="search",
        func=serper.run,
        description="Use this tool when you want to get the results of an online we search"
    )
    wikipedia=WikipediaAPIWrapper()
    wiki_tool=WikipediaQueryRun(api_wrapper=wikipedia)

    return file_tools + [push_tool, search_tool, wiki_tool]