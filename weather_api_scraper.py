import sys
import json
import time
import argparse
import datetime

import requests
import pandas as pd
import sqlalchemy


def main():
    # Read user's arguments and store them in a dictionary
    settings_dict = user_args()

    # Read db settings.json
    db_settings = load_settings('db_settings.json')

    # Check if date already exists in db
    check_date_in_db(settings_dict['DATE'], db_settings)

    # Call API and store the weather data in a dictionary
    weather_data_dict = request_weather_data(settings_dict)

    # Convert the weather data dictionary to a dataframe
    weather_data_df = weather_data_to_df(weather_data_dict)

    # Save the data in a postgres database
    weather_data_to_db(weather_data_df, db_settings)


def user_args() -> dict:
    """[Handle user args]

    Returns:
        dict: [settings_dict contains all the user args e.g. api key, location and forecast's date]
    """

    parser = argparse.ArgumentParser()

    parser.add_argument('-k', '--key', dest='api_key',
                        help='Type API key', required=True)
    parser.add_argument('-l', '--location', dest='location',
                        help='Type location', required=True)
    parser.add_argument('-d', '--date', dest='date',
                        help='Type forecast date [YYYY-MM-DD]', required=True)

    args = parser.parse_args()

    # Store args in dictionary
    settings_dict = {}
    settings_dict['API_KEY'] = args.api_key
    settings_dict['LOCATION'] = args.location

    # Validate date - YYYY-MM-DD
    success = validate_date_format(args.date)

    if success:
        settings_dict['DATE'] = args.date
    else:
        sys.exit(1)

    return settings_dict


def validate_date_format(date: str) -> bool:
    """[Validates the given date's format]

    Args:
        date (str): [The date given by the user - It should be in YYYY-MM-DD]

    Returns:
        bool: [True is the date format is acceptable, False if it's not]
    """

    try:
        datetime.datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        print('\nERROR: Incorrect forecast date format, should be YYYY-MM-DD')
        return False

    return True


def request_weather_data(settings_dict: dict) -> dict:
    """[Request data from the WeatherAPI]

    Args:
        settings_dict (dict): [It contains all the user args e.g. api key, location and forecast's date]

    Returns:
        dict: [weather_data_dict contains all the necessary weather data]
    """

    api_url = f'https://api.weatherapi.com/v1/history.json?key={settings_dict["API_KEY"]}&q={settings_dict["LOCATION"]}&dt={settings_dict["DATE"]}'

    counter = 0
    while True:
        if counter <= 5:
            try:
                response = requests.get(api_url)
                if response.status_code == 200:
                    print('Weather data recieved from the API successfully')
                    break
                else:
                    print(
                        f'ERROR: Status Code: {response.status_code} - Retry in 1 hr')
                    time.sleep(3600)
                    counter += 1
                    continue
            except Exception as e:
                print(e)
                print('Retry in 1 hr')
                time.sleep(3600)
                counter += 1
                continue
        else:
            print('Unable to get data from the API - Aborting...')
            sys.exit(1)

    # Filter the response/weather data
    weather_data = response.json()['forecast']['forecastday'][0]
    weather_data_dict = weather_data['day']

    # Remove not needed data/dict keys
    keys_lst = ['mintemp_f', 'maxtemp_f', 'avgtemp_f',
                'maxwind_mph', 'totalprecip_in', 'avgvis_miles']
    weather_data_dict = {key: value for (
        key, value) in weather_data_dict.items() if not key in keys_lst}

    # Add more keys/data
    weather_data_dict['condition'] = weather_data_dict['condition']['text']
    weather_data_dict['date'] = settings_dict['DATE']
    weather_data_dict['date_epoch'] = weather_data['date_epoch']

    return weather_data_dict


def weather_data_to_df(weather_data_dict: dict) -> pd.DataFrame:
    # Values need to be in lists in order the df to be created having the keys as column names
    for key, value in weather_data_dict.items():
        weather_data_dict[key] = [value]

    return pd.DataFrame(weather_data_dict)


def weather_data_to_db(weather_data_df: pd.DataFrame, db_settings: dict) -> None:
    """[Stores the weather data to a postgres database]

    Args:
        weather_data_df (pd.DataFrame): [It contains the weather data for the given date]
    """
    counter = 0
    while True:
        if counter <= 5:
            try:

                # Create engine/connection for the postgres database
                engine = sqlalchemy.create_engine(
                    f'postgresql://{db_settings["username"]}:{db_settings["password"]}@{db_settings["hostname"]}:{db_settings["port"]}/{db_settings["database"]}')
                if not engine.dialect.has_schema(engine, db_settings['schema']):
                    engine.execute(sqlalchemy.schema.CreateSchema(
                        db_settings['schema']))
                # Store the data to the database
                weather_data_df.to_sql(
                    f'{db_settings["table"]}', engine, schema=db_settings['schema'], if_exists='append', index=False)

                print(
                    f'Data for {weather_data_df["date"].iloc[0]} appended in the database')

                break
            except Exception as e:
                print(e)
                print(
                    f'Unable to save the data for {weather_data_df["date"].iloc[0]} to the database - Retry in 30 mins')
                time.sleep(1800)
                counter += 1
                continue
        else:
            print(
                f'Unable to save the data for {weather_data_df["date"].iloc[0]} to the database - Aborting...')
            sys.exit(1)


def check_date_in_db(date_to_check, db_settings: dict) -> None:
    # Create engine/connection for the postgres database
    engine = sqlalchemy.create_engine(
        f'postgresql://{db_settings["username"]}:{db_settings["password"]}@{db_settings["hostname"]}:{db_settings["port"]}/{db_settings["database"]}')

    # Check if table exists in db
    insp = sqlalchemy.inspect(engine)
    table_exists = insp.has_table(
        db_settings['table'], schema=db_settings['schema'])

    if table_exists:
        try:
            # Read sql table - use chunks instead of whole table
            for chunk in pd.read_sql_table(db_settings['table'], con=engine, schema=db_settings['schema'], columns=['date'], chunksize=500):
                # Dates already scraped and stored in the db
                dates_lst = chunk.date.unique()
                # Exit if date is already in the db
                if date_to_check in dates_lst:
                    print(
                        f'Weather data for {date_to_check} already in the database - Aborting...')
                    sys.exit(0)
        except Exception as e:
            print(f'Error while reading table {db_settings["table"]}')
            raise Exception


def load_settings(jsonpath: str) -> dict:
    """[It parses the given json settings file]

    Args:
        jsonpath (str): [It contains settings]

    Returns:
        dict: [The settings in a dictionary]
    """
    try:
        with open(jsonpath) as jsonfile:
            settings = json.load(jsonfile)
    except Exception as e:
        print(e)
        print(f'Error while loading {jsonpath}')
        sys.exit(1)

    return settings


if __name__ == '__main__':
    main()
