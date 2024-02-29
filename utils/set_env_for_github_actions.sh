#!/bin/bash

ENCODED="$(cat ./.env | base64)"
if [[ "$1" == "--dry-run" ]]; then
    echo "$ENCODED" | base64 --decode
    exit 0
fi
echo "$ENCODED" | gh secret set ENV_FILE -R hyphen/hyphen-python