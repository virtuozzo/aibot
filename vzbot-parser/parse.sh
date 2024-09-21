#!/bin/bash
#create list of links
python vzbot_create_links.py
#create FAISS DB
python vzbot-parser.py

echo "Done"

