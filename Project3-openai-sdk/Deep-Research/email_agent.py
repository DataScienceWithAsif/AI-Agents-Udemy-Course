from agents import Agent, function_tool
from sendgrid.helpers.mail import Email, To, Content, Mail
import sendgrid
import os
from dotenv import load_dotenv
from typing import Dict

load_dotenv()

@function_tool
def send_email(subject:str, html_body:str)-> Dict[str,str]:
  """Send out an email with given subject and HTML body"""
  sg=sendgrid.SendGridAPIClient(api_key=os.environ.get("SENDGRID_API_KEY"))

  from_email=Email("muasif025@gmail.com")
  to_email=To("as29624041@gmail.com")
  content=Content("text/html",html_body)
  mail=Mail(from_email,to_email,subject,content).get()
  response=sg.client.mail.send.post(request_body=mail)
  print(f"Email status: {response.status_code}")
  return {"status":"success"}


email_agent_inst="""You are able to send a nicely formatted HTML email based on a detailed report.
You will be provided  with a detailed report. You should use your send_email tool to send one email,
providing the report converted into clean, well presented HTML with an appropriate subject line."""

email_agent=Agent(
    name="Email Agent",
    instructions=email_agent_inst,
    tools=[send_email],
    model="gpt-4o-mini"
)