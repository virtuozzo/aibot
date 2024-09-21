# Virtuozzo Hybrid Infrastructure Bot
### Purpose
The initial purpose is to answer technical questions about Virtuozzo Hybrid Infrastructure based on its documentation. 
In general, this is general purpose bot, as you can add any documentation to its database. If you add links to VAP docs - it will answer to VAP questions as well. If you add links to business docs - it will answer.

This bot uses the OpenAI GPT model together with the Retrieval-augmented generation (RAG) approach. You can read more about RAG here https://blogs.nvidia.com/blog/what-is-retrieval-augmented-generation/

### Parse a documentation
Go to vzbot-parser, add documentation links to config.json and run parse.sh. The script will create a list of links first, than the json database, and FAISS database finally in the root folder.

### Create Telegram Bot
Find @BotFather on Telegram and follow the guide. Your main goal is to obtain an API Token.

### Create OpenAI Account
Go to OpenAI https://openai.com/, create an account, go to API, and get the API Key.

### Create Slack App
Go to OpenAI https://slack.com/, go to Apps.
Slack App requires your bot to have the proper SSL certificate. You need to create it using Let's Encrypt for example, and put to the ssl folder.
Slack App serves on the port TCP 3000!

### Security
The following ports must be open for inbound connection:

TCP 3000

TCP 443 (HTTPS)

### Run the bot
Run docker compose:

    docker compose pull && docker compose up -d

Enjoy.
