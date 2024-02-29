#!/bin/bash

echo "$ENV_FILE" | base64 --decode > .env