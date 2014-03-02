#!/bin/bash

if [ $# -ne 2 ]; then
	echo "Missing/Extra Arguments"
	exit 0
fi

URL=$1
XML_PATH=$2
TMP_PATH="/tmp/$RANDOM.xml"

./scrapeTuneIn.py "$URL" > "$TMP_PATH"
if [ $? -ne 0 ]; then
	echo "scrape Failed"
	exit 1
fi

mv "$TMP_PATH" "$XML_PATH"
