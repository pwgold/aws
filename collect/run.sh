#!/bin/bash

SCRAPER=$1

DATE=$(date +%Y%m%d)
OUTPUT_DIR=/home/ubuntu/aws/data/$SCRAPER/$DATE
python $SCRAPER.py $OUTPUT_DIR
echo "$OUTPUT_DIR:"
ls $OUTPUT_DIR
