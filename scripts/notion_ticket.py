import requests 
import os
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

def create_notion_ticket(query):
    NOTION_API_KEY = os.environ.get("NOTION_API_KEY")
    NOTION_DATABASE_ID = os.environ.get("NOTION_DATABASE_ID")
    response = requests.post(
        "https://api.notion.com/v1/pages",
        headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
        },
        json = {
            "parent": {"database_id": NOTION_DATABASE_ID},
            "properties": {
                "Question": {
                    "title": [{"text": {"content": query}}]
                },
                "Status": {
                    "status": {"name": "Open"}
                },
                "Timestamp": {
                    "date": {"start": datetime.now().isoformat()}
                }
            }
        })
    return response