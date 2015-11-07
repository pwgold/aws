#!/bin/bash

#  python Ameritrade.py --tickers $(python list_ib_tickers.py ../data/InteractiveBrokers/20151106/usa.txt)

# Usage: bash run.sh InteractiveBrokers
SCRAPER=$1

DATE=$(date +%Y%m%d)
OUTPUT_DIR=/home/ubuntu/aws/data/$SCRAPER/$DATE
python $SCRAPER.py $OUTPUT_DIR
echo "$OUTPUT_DIR:"
ls $OUTPUT_DIR
