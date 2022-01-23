# Weather API Scraper

### Overview
A CLI application that scrapes weather data from WeatherAPI.com, developed as an API consumption demonstration, and stores it to the given postgres database/table.

### Version
1.0.0
### Dependencies
+ Python: 3.10.1
+ see requirements.txt

### Inputs
+ API Key (from WeatherAPI.com)
+ Location (It could be: lat,long (in decimal degrees) / city name / US zip / UK postcode / iata / IP address)
+ Date (in YYYY-MM-DD format)

### Outputs
+ Weather data for the given date in the given postgres database/table

### Usage
Type the following in the command line:
```shell
> python weather_api_scraper.py -k <api_key> -l <location> -d <date>
```

### Required Postgres table structure
maxtemp_c: double precision
mintemp_c: double precision
avgtemp_c: double precision
maxwind_kph: double precision
totalprecip_mm: double precision
avgvis_km: double precision
avghumidity: double precision
condition: text
uv: double precision
date: text
date_epoch: bigint
id: bigint (PK, BIGSERIAL)
