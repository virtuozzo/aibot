#!/bin/bash
#build docker images for arm and x86
docker build --platform linux/amd64,linux/arm64 -t vporokhov/vzbot-server ./vzbot-server
docker build --platform linux/amd64,linux/arm64 -t vporokhov/vzbot-telegram ./vzbot-telegram
docker build --platform linux/amd64,linux/arm64 -t vporokhov/vzbot-slack ./vzbot-slack

#push docker images
docker image push vporokhov/vzbot-server
docker image push vporokhov/vzbot-telegram
docker image push vporokhov/vzbot-slack

echo "Done"

