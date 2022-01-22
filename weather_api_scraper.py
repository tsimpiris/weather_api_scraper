import sys
import argparse
import datetime
import requests


def main():
    settings_dict = user_args()

    # 3. api request
    request_weather_data(settings_dict)

    # 4. prepare api data to df

    # 5. store in postgres

def user_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('-k', '--key', dest='api_key', help='Type API key', required=True)
    parser.add_argument('-l', '--location', dest='location', help='Type location', required=True)
    parser.add_argument('-d', '--date', dest='date', help='Type forecast date [YYYY-MM-DD]', required=True)

    args = parser.parse_args()

    settings_dict = {}
    settings_dict['API_KEY'] = args.api_key
    settings_dict['LOCATION'] = args.location

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


def request_weather_data(settings_dict):
    pass
    

if __name__ == '__main__':
    main()
