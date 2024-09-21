import os
import dotenv
import logging
import requests
from telegram.ext import CommandHandler, MessageHandler, filters, Application
from logtail import LogtailHandler

#Load local environment variables
dotenv.load_dotenv()
bot_token = os.getenv("TELEGRAM_API_TOKEN")
betterstack_token = os.getenv("BETTERSTACK_TOKEN")
server_url = os.getenv("SERVER_URL")

#BetterStack logger if token is provided
if betterstack_token:
  handler = LogtailHandler(source_token=betterstack_token)
  logger = logging.getLogger(__name__)
  logger.setLevel(logging.INFO)
  logger.handlers = []
  logger.addHandler(handler)
  logger.info('bot_start')
  print("betterstack is ready")

print("TELEGRAM BOT IS READY")

async def start_command(update, context):
  # Implement the start response
    user = update.message.from_user
    if betterstack_token: logger.info('start', extra={
        'user': user['username'],
    }) 
    await update.message.reply_text('Welcome to the AI-powered Virtuozzo Hybrid Infrastructure Support Bot!\nExample:\nHow to configure Kubernetes storage class?')

async def product_command(update, context):
  # Implement the product response
    user = update.message.from_user
    if betterstack_token: logger.info('product', extra={
        'user': user['username'],
    }) 
    await update.message.reply_html(
        "<a href='https://www.youtube.com/watch?v=n5jH82nOyF8&list=PL86FC0XuGZPJ-EDDSwT-MoSyYHTG5cjeb'>Product Demo</a>\n"
        "<a href='https://www.virtuozzo.com/hybrid-infrastructure/'>Product Page</a>\n",
    )

async def wiki_command(update, context):
  # Implement the wiki response
    user = update.message.from_user
    if betterstack_token: logger.info('wiki', extra={
        'user': user['username'],
    }) 
    await update.message.reply_html(
        "The list of how-to, integration examples and troubleshooting guides\n"
        "<a href='https://www.virtuozzo.com/hybrid-infrastructure-docs/tutorials/'>Wiki Pages</a>\n"
        "<a href='https://support.virtuozzo.com/hc/en-us/categories/11946726813841-Virtuozzo-Hybrid-Infrastructure'>Knowledge Base</a>\n",
    )

async def docs_command(update, context):
  # Implement the docs response
    user = update.message.from_user
    if betterstack_token: logger.info('docs', extra={
        'user': user['username'],
    }) 
    await update.message.reply_html(
        "<a href='https://docs.virtuozzo.com/virtuozzo_hybrid_infrastructure_6_0_admins_guide/index.html'>Administrator's Guide</a>\n"
        "<a href='https://docs.virtuozzo.com/virtuozzo_hybrid_infrastructure_6_0_self_service_guide/index.html'>Self-service Guide</a>\n"
        "<a href='https://docs.virtuozzo.com/virtuozzo_hybrid_infrastructure_6_0_compute_api_reference/index.html'>Compute API Reference</a>\n"
        "<a href='https://docs.virtuozzo.com/virtuozzo_integrations_acronis_cyber_cloud_migration_from_vmware/index.html'>VMware Migration with Acronis Cyber Cloud</a>\n"
        "<a href='https://docs.virtuozzo.com/virtuozzo_integrations_hystax_migration_from_vmware/index.html'>VMware Migration with Hystax</a>\n"
        "<a href='https://docs.virtuozzo.com/virtuozzo_advisory_archive/virtuozzo-hybrid-infrastructure/index.html#virtuozzo-hybrid-infrastructure'>Release Notes</a>\n"
        "<a href='https://www.virtuozzo.com/hybrid-infrastructure-docs/'>All documentation</a>",
    )

async def support_command(update, context):
  # Implement the support response
    user = update.message.from_user
    if betterstack_token: logger.info('support', extra={
        'user': user['username'],
    }) 
    await update.message.reply_html(
        "<a href='https://virtuozzo.zendesk.com/auth/v2/login/signin'>Create Ticket</a>\n"
        "<a href='https://www.virtuozzo.com/all-supported-products/'>Support Portal</a>\n"
        "<a href='https://www.virtuozzo.com/all-supported-products/severity-level-definitions/'>Priority Definitions</a>",
    )

# Handling chat message with OpenAI
async def handle_message(update, context):
  message = update.message.text
  chat_id = update.message.chat_id
  user = update.message.from_user
  first_name = user.first_name

  data = {
    'message': message
  }
  # Send the POST request
  response = requests.post(server_url, json=data)

  # Check if the request was successful
  if response.status_code == 200:
      # Parse the JSON response
      answer = response.json()
      
      # Print the reply from the server
      print("Server replies successfully")
      #print(answer['reply'])
  else:
      print(f"Error: Received status code {response.status_code}")
      #print(response.text)

  #send logs to BetterStack
  if betterstack_token: logger.info('question', extra={
    'user': user['username'],
    'prompt': message,
    'answer': answer['reply'],
  })

  answer_formatted = answer["reply"].replace("<", "&lt;").replace(">", "&gt;")
  #await update.message.reply_text("Question:\n" + message + "\n" + "Answer:\n" + answer.get('result'))
  await update.message.reply_html(answer_formatted)

#Polling Telegram bot
def main() -> None:
    
    application = Application.builder().token(bot_token).build()
    application.add_handler(CommandHandler('start', start_command))
    application.add_handler(CommandHandler('product', product_command))
    application.add_handler(CommandHandler('wiki', wiki_command))
    application.add_handler(CommandHandler('docs', docs_command))
    application.add_handler(CommandHandler('support', support_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling()

    # Run the bot until you press Ctrl-C
    application.idle()

if __name__ == '__main__':
    main()