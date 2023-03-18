from textwrap import dedent
def send_welcome_message(bot,logger,chat_id):
    try:
        bot.send_message(chat_id,"Hey there! How are you?\nIf you are new here, select \n*/botCommands* to get this bot commands.", parse_mode="Markdown")
        logger.info(f'Successfully sent message to the user with id {chat_id}')
    except Exception as e:
        logger.error(f'Unable to send message to the user with id {chat_id} with error {str(e)}')
    
def send_all_commands(bot,logger,chat_id):
    commands = """\
        1. To get response to your question and save the responses to Notion, click */squestion*. \nBy using this command, you will be clearing the previous session history.
        2. To continue your previous session i.e., continue your chat with ChatGPT, click */continue*. 
        """
    try:
        bot.send_message(chat_id,dedent(commands).strip('\n'),parse_mode="Markdown")
        logger.info(f'Successfully sent all Commands to the user with id {chat_id}')
    except Exception as e:
        logger.error(f'Unable to send message to the user with id {chat_id} with error {str(e)}')