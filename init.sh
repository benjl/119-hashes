#!/bin/bash

BESTS_FILE="/usr/119rust/resume/bests.txt"
PROGRESS_FILE="/usr/119rust/resume/savedprogress.txt"
COLLECTION_FILE="/usr/119rust/resume/collection.txt"

mkdir -p "$(dirname "$BESTS_FILE")"

if [ ! -f "$BESTS_FILE" ]; then
    touch "$BESTS_FILE"
    echo "Created: $BESTS_FILE"
fi

if [ ! -f "$PROGRESS_FILE" ]; then
    touch "$PROGRESS_FILE"
    echo "Created: $PROGRESS_FILE"
fi

if [ ! -f "$COLLECTION_FILE" ]; then
    touch "$COLLECTION_FILE"
    echo "Created: $COLLECTION_FILE"
fi

ln -s /usr/119rust/resume/savedprogress.txt /usr/119rust/savedprogress.txt
ln -s /usr/119rust/resume/bests.txt /usr/119rust/bests.txt
ln -s /usr/119rust/resume/collection.txt /usr/119rust/collection.txt

exec "$@"