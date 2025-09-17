from openai import OpenAI
from dotenv import load_dotenv
import gradio as gr
import json
import os
import requests
from PyPDF2 import PdfReader
from dotenv import load_dotenv
from ast import arguments
from pathlib import Path

load_dotenv(override=True)
groq_api_key=os.getenv("GROQ_API_KEY")
groq_base_url="https://api.groq.com/openai/v1"
groq=OpenAI(api_key=groq_api_key, base_url=groq_base_url)
groq_model="openai/gpt-oss-20b"

pushover_user=os.getenv("PUSHOVER_USER")
pushover_token=os.getenv("PUSHOVER_TOKEN")
pushover_url="https://api.pushover.net/1/messages.json"

def push(message):
  print(f"push: {message}")
  payload={"user":pushover_user,"token":pushover_token, "message":message}
  requests.post(pushover_url,data=payload)

#tools
def record_user_details(email, name="Name not provied",notes="Notes not provided"):
  push(f"Recording {name} with email {email} and notes {notes}")
  return {"recorded":"ok"}

def record_unkown_question(question):
  push(f"Recording {question} asked that I couldn't answer")
  return {"recorded":"ok"}

record_user_details_json={
    "name":"record_user_details",
    "description":"Use this tool to record that a user is interested in being in touch and provided an email address",
    "parameters":{
        "type":"object",
        "properties":{
            "email":{
                "type":"string",
                "description":"the email address of user"
            },
            "name":{
                "type":"string",
                "description":"name of the user"
            },
            "notes":{
                "type":"string",
                "description":"any additional information about the conversation that is worth recording to give context"
            }
        },
        "required":["email"],
        "additionalProperties":False
    }
}
record_unkown_question_json={
    "name":"record_unkown_question",
    "description":"Always use this tool to record any question that couldn't be answered as you didn't know the anwser",
    "parameters":{
        "type":"object",
        "properties":{
            "question":{
                "type":"string",
                "description":"The question that couldn't be answered"
            }
        },
        "required":["question"],
        "additionalProperties":False
    }
}

tools=[{"type":"function","function":record_user_details_json},
       {"type":"function","function":record_unkown_question_json}]

class me:
    def __init__(self):
        self.groq=groq
        self.name="M Asif"
        base_dir = Path(__file__).resolve().parent
        linkedin_pdf = base_dir / "linkedin.pdf"
        summary_txt = base_dir / "summary.txt"
        reader=PdfReader(str(linkedin_pdf))
       
        self.linkedin=""
        for page in reader.pages:
            text=page.extract_text()
            if text:
                self.linkedin+=text
        with open("E:\\udemy\\projects\\agents\\1_foundations\\me\\summary.txt","r",encoding="utf-8") as f:
            self.summary=f.read()
        
        # Refine handle_tool_calls function using globals instead of if-statement
   
    def handle_tool_calls(self,tool_calls):
        results=[]
        for tool_call in tool_calls:
            tool_name=tool_call.function.name
            arguments=json.loads(tool_call.function.arguments)
            print(f"tool called: {tool_name}",flush=True)

            tool=globals().get(tool_name)
            result=tool(**arguments) if tool else {}

            results.append({"role":"tool","content":json.dumps(result),"tool_call_id":tool_call.id})

        return results
    
    def system_prompt(self):
        system_prompt=f"You are acting as {self.name}.You are answering questions on {self.name}`s website, \
particularly questions related to {self.name}`s career, background, skills,education and experience. \
your responsibility is to represent {self.name} for interactions on the website as faithfully as possible. \
You are given summary of {self.name}`s background and LinkedIn profile which you can use to answer the questions. \
Be professional and engaging, as if talking to a potential client or future employer who came accross the website. \
If you do not know the answer to any question, use your record_unkown_question tool to record the question that you couldn`t answer \
If the user is engaging in discussion,try to steer them towards getting in touch via email: ask for thier email and record it using your record_user_details tool."

        system_prompt +=f"\n\n## Summary: {self.summary}\n\n LinkedIn Profile: {self.linkedin}\n\n"
        system_prompt +=f"with this context, please chat with user, always staying in character as {self.name}"
        return system_prompt

    def chat(self,message, histoy):
        messages=[{"role":"system","content":self.system_prompt()}]
        if histoy:
            for turn in histoy:
                if len(turn)==2:
                    human,assistant=turn
                    messages.append({"role":"user","content":human})
                    messages.append({"role":"assistant","content":assistant})
        messages.append({"role":"user","content":message})

        done=False
        while not done:
            response=self.groq.chat.completions.create(model=groq_model, messages=messages, tools=tools)
            finish_reason=response.choices[0].finish_reason

            if finish_reason=="tool_calls":
                message=response.choices[0].message
                tool_calls=message.tool_calls
                result=self.handle_tool_calls(tool_calls=tool_calls)

                messages.append(message)
                messages.extend(result)
            else:
                done=True

        return response.choices[0].message.content

if __name__=="__main__":
    me=me()
    gr.ChatInterface(me.chat, type="messages").launch(share=True,debug=True)
       

