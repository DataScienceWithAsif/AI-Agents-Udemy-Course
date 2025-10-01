from crewai.tools import BaseTool
from typing import Type, Union
from pydantic import BaseModel, Field
import os
import requests

class PushNotificationInput(BaseModel):
    """A message to be sent to the user"""
    message: Union[str, dict] = Field(..., description="A message to be sent to the user")

class PushNotificationTool(BaseTool):
    name: str = "Send a push notification"
    description: str = (
        "This tool is used to send a push notification to the user"
    )
    args_schema: Type[BaseModel] = PushNotificationInput

    def _run(self, message) -> str:
        pushover_url="https://api.pushover.net/1/messages.json"
        pushover_user=os.getenv("PUSHOVER_USER")
        pushover_token=os.getenv("PUSHOVER_TOKEN")

        # Handle both string and dictionary inputs
        if isinstance(message, dict):
            # Extract the message from dictionary if it has a 'message' key
            if 'message' in message:
                message = message['message']
            elif 'description' in message:
                message = message['description']
            else:
                message = str(message)
        else:
            message = str(message)

        print(f"push: {message}")
        payload={"user":pushover_user, "token":pushover_token, "message":message}
        requests.post(pushover_url, data=payload)
        return {"notification":"ok"}

