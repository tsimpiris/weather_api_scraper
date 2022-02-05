#!/bin/bash

source /home/ioats/dev/prod/weather_api_scraper/venv/bin/activate

cd /home/ioats/dev/prod/weather_api_scraper

yesterday=$(date -d "yesterday 13:00" '+%Y-%m-%d')
apikey="type your api key here"
location="type your location here"

python3 /home/ioats/dev/prod/weather_api_scraper/weather_api_scraper.py -k $apikey -l $location -d $yesterday

deactivate
