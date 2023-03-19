import os
import json

def get_question(bot,logger,chat_id,chat_gpt_token,http,return_to_main,new_page):
    logger.info("Inside app_responses.get_question method")
    get_question_message = bot.send_message(chat_id,"Enter Your question")
    logger.info('Successfully sent a message to the user to get the question')
    bot.register_next_step_handler(get_question_message,get_chat_response,chat_gpt_token,http,bot,return_to_main,new_page,logger)
    
def get_chat_response(message,chat_gpt_token,http,bot,return_to_main,new_page,logger):
    """
    This is the function that can be used to get response from ChatGPT based on the question asked by the user.

    Steps:
    1. This will check if there are any previous conversations that need to be send to the chat API to get response. 
    2. If yes, we will import those Q&A history and send it to the chat along with new question
    3. Obtain response from chat.
    """
    logger.info("Received question input from the user.")
    question = message.text
    chats_file = os.getcwd() + '/project/chats/squestions.json'
    #Initializing a dictionary to get all previous chats from json file
    previous_chats = []
    #Validating if there is a session history. If yes, the history is sent along with new question so that the assistant will have previous context.
    if os.path.isfile(path=chats_file):
        with open(chats_file,'r') as f:
            logger.info("Previous session history is found, reading the list.")
            previous_chats = json.load(f)
    
    #The new question here represents the new question asked by the user. This is the dictionary format in which the user input need to be sent to API.
    new_question = {"role":"user","content":f"{question}"}
    
    #Appending the new question dictionary with previous chats list.
    previous_chats.append(new_question)
    logger.info("New question dictionary is created and appended to the previous session history as applicable.")
    
    url = "https://api.openai.com/v1/chat/completions"

    headers = {
        "Authorization" : f"Bearer {chat_gpt_token}",
        "Content-Type": "application/json"
    }
    #The messages in the payload should be in a list format.
    payload = {
        "model" : "gpt-3.5-turbo",
        "messages" : previous_chats
    }
    body = json.dumps(payload)
    logger.info("Sending a http request to ChatGPT API to get response.")
    chat_results = http.request("POST",url=url,headers=headers,body=body)
    logger.info("Sent a request to ChatGPT with the question and results are obtained.")
    results = (json.loads(chat_results.data.decode('utf-8')))
    if 'error' in results:
        logger.info("There was an error when chatGPT responded")
        logger.info(f"{results}")
        bot.send_message(message.chat.id,"There was an issue with getting the response. Try Again.")
        previous_chats = previous_chats[:-1]
    else:
        logger.info("Successfully received chatGPT response")
        logger.info(f"{results}")
        actual_response = results['choices'][0]['message']['content'] #This can be used to save the response to notion
        bot.send_message(message.chat.id,f"Here is your response \n{actual_response}",parse_mode="Markdown")
        new_response = {"role":"assistant","content":f"{actual_response}"}
        previous_chats.append(new_response)
        
        with open(chats_file,'w') as f:
            logger.info("Response is received and chats session history is updated")
            json.dump(previous_chats,f)
        
        return_to_main(new_page,question,actual_response,message.chat.id)
    #Once the response is received we are updating the json file with the new Q&A set.

    