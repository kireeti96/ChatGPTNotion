import os
import logging
from datetime import datetime
from dotenv import load_dotenv
import urllib3
from telebot import TeleBot
import json
import logging.config
#Custom packages
import app_start
import app_responses
import app_notion_pages

#Loading the environment variables.
load_dotenv()

#Log file name formattings
now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
logfilename = f'logs/app_{now}.log'
config_dict = {'logfilename':logfilename}

#Importing logging config file from the path and also assigning the logging file name using defaults
logging_file_path = os.getcwd() + "/project/logging.conf"
logging.config.fileConfig(logging_file_path,defaults=config_dict)
#chatNotion is the logger Name that is used for this project. We could use __name__ by default if we choose to use root logger
logger = logging.getLogger('chatNotion')

#Importing the bit token from Environment variable file.
try:
    # Get the bot token from the environment variable
    bot_token = os.getenv('bot_token')
    # Check if the token is None
    if bot_token is None:
        raise ValueError('bot_token environment variable is not set')
    # Use the token
    else:
        logger.debug(f'Bot token is successfully imported')
except ValueError as e:
    logger.error(str(e))
    logger.info("Bot Token is not found, exiting the system")
    os._exit(0)
try:
    #Get Notion Token and Database values
    notion_token = os.getenv('notion_token')
    notion_database = os.getenv('notion_database')
    if (notion_token is None) or (notion_database is None):
        raise ValueError('Notion configuration is not completed. Check environment variables.')
    else:
        logger.info("Successfully imported Notion credentials")
except ValueError as e:
    logger.error(str(e))
    logger.info("Notion credentials are not found, exiting the system")
    os._exit(0)

try:
    #Get Notion Token and Database values
    chat_gpt_token = os.getenv('chat_gpt_token')
    if chat_gpt_token is None:
        raise ValueError('Chat GPT is configuration is not complete') 
    else:
        logger.info('Successfully imported ChatGPT credential.')
except ValueError as e:
    logger.error(str(e))
    logger.info("ChatGPT credential is not found. Check environment variables")
    os._exit(0)

#This will check for the existence of logs folder and creates otherwise.
if not os.path.exists('logs'):
    os.mkdir('logs')

#This will check for the existence of chats folder and creates otherwise.
if not os.path.exists('project/chats'):
    os.mkdir('project/chats')

#Intializing the telegram bot
bot = TeleBot(token=bot_token)

#Initializing a http instance
http = urllib3.PoolManager()

#The Method to handle the start and hello commands of the bot
@bot.message_handler(commands=['start','hello'])
def send_welcome(message):
    """
    This is the function that is used when the bot is sent commands start or hello
    """
    logger.info("Calling the send_welcome_message method from app_start package")
    app_start.send_welcome_message(bot,logger,message.chat.id)

@bot.message_handler(commands=['botCommands'])
def all_commands(message):
    """
    This is the method that is used to send all Bot commands to the user
    """
    app_start.send_all_commands(bot,logger,message.chat.id)

        
@bot.message_handler(commands=['squestion'])
def get_question(message):
    """
    This is the method that gets invoked when squestion command is sent to the bot. 

    The bot will then erase all existing data previously stored.

    This will then send a message to the user asking for the question that they want response for.
    """
    chats_file = os.getcwd() + '/project/chats/squestions.json'
    notion_page_id_file = os.getcwd() + '/project/chats/notion_page_id.json'
    if os.path.isfile(path=chats_file):
        os.remove(chats_file)
        logger.info('Successfully deleted the squestion file to reset the chat')
    
    if os.path.isfile(path=notion_page_id_file):
        os.remove(notion_page_id_file)
        logger.info("Successfully removed the file containing notion page id")
        
    #Navigating to app_responses package to process the Q&A
    app_responses.get_question(bot,logger,message.chat.id,chat_gpt_token,http,save_to_notion,new_page=True)
    
@bot.message_handler(commands=['continue'])
def get_question(message):
    """
    This is the method that gets invoked when squestion command is sent to the bot. 

    The bot will then erase all existing data previously stored.

    This will then send a message to the user asking for the question that they want response for.
    """
    previous_page_id = os.getcwd() + '/project/chats/notion_page_id.json'
    
    if not os.path.isfile(path=previous_page_id):
        bot.send_message(message.chat.id,"Sorry, there is no previous session. Please click */squestion* to get started",parse_mode="Markdown")
    else:
        #Navigating to app_responses package to process the Q&A
        app_responses.get_question(bot,logger,message.chat.id,chat_gpt_token,http,save_to_notion,new_page=False)

def save_to_notion(new_page,question,actual_response,chat_id):
    """
    If new_page flag is True, we need to create a new Notion Page in the database.
    """
    if new_page:
        ask_notion_page_name = bot.send_message(chat_id,"Since this is your question of the session, please enter a page title.")
        bot.register_next_step_handler(ask_notion_page_name,app_notion_pages.create_page,notion_database,notion_token,question,actual_response,bot)
    else:
        
        previous_page_id = os.getcwd() + '/project/chats/notion_page_id.json'
        with open(previous_page_id,'r') as f:
            data = json.load(f)
        notion_page_id = data['page_id']
        app_notion_pages.append_page(notion_page_id,notion_token,question,actual_response,bot,chat_id)


#This line is used to run the code continuouslly. 
bot.infinity_polling()
