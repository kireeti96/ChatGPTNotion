import json
import requests
import os
def create_page(message,database_id,token,question,answer,bot):
    url = "https://api.notion.com/v1/pages"
    headers = {
    "Authorization" : f"Bearer {token}",
    "Content-Type" : "application/json",
    "Notion-Version":"2022-06-28"
    }
    payload = {
                "parent": { "database_id": f"{database_id}" },
                "properties": {
                    "title": {
                "title": [{ "type": "text", "text": { "content": f"{message.text}" } }]
                    }
                },
                "children": [
                {
                    "object" : "block",
                    "type": "heading_3",
            
                    "heading_3": {
                        "rich_text": [{
                        "type": "text",
                        "text": {
                            "content": f"{question}"
                        }
                        }],
                        "color": "default",
                        "is_toggleable": True,
                        "children" : [
                            {
                                "object" : "block",
                                "type" : "paragraph",
                                "paragraph" : {
                                    "rich_text" : [
                                        {
                                            "type" : "text",
                                            "text": {
                                                "content" : f"{answer}"
                                            }
                                        }
                                    ]
                                }
                            }
                        ]
                    }
                }
            ]
            }

    data = json.dumps(payload,default=str)

    response = requests.post(url, data=data, headers=headers)
    # print(response.json())
    page_id,url = response.json()['id'],response.json()['url']
    bot.send_message(message.chat.id, f"A new page with title {message.text} is created with your Q&A. You can find the page here. {url}\nTo continue your chat, click */continue* or click */squestion* to restart",parse_mode = "Markdown")
    notion_page_id = {"page_id":f"{page_id}"}
    file_saving_location = os.getcwd() + '/project/chats/notion_page_id.json'
    with open(file_saving_location,'w') as f:
        json.dump(notion_page_id,f)

def append_page(block_id,token,question,actual_response,bot,chat_id):
    
    
    url = f"https://api.notion.com/v1/blocks/{block_id}/children"
    headers = {
    "Authorization" : f"Bearer {token}",
    "Content-Type" : "application/json",
    "Notion-Version":"2022-06-28"
    }
    payload = {
        "children": [
                {
                    "object" : "block",
                    "type": "heading_3",
            
                    "heading_3": {
                        "rich_text": [{
                        "type": "text",
                        "text": {
                            "content": f"{question}"
                        }
                        }],
                        "color": "default",
                        "is_toggleable": True,
                        "children" : [
                            {
                                "object" : "block",
                                "type" : "paragraph",
                                "paragraph" : {
                                    "rich_text" : [
                                        {
                                            "type" : "text",
                                            "text": {
                                                "content" : f"{actual_response}"
                                            }
                                        }
                                    ]
                                }
                            }
                        ]
                    }
                }
            ]
    }
    data = json.dumps(payload,default=str)
    response = requests.patch(url, data=data, headers=headers)
    #print(response.json())
    #page_id,url = response.json()['results']['page_id'],response.json()['url']
    bot.send_message(chat_id, f"Your page has been updated with latest Q&A.\nTo continue your chat, click */continue* or click */squestion* to restart",parse_mode = "Markdown")
    
    
    
 