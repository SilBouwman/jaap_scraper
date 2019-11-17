# Importing external libraries
import requests
from bs4 import BeautifulSoup
from google.oauth2 import service_account
import pandas_gbq
import re

# Importing internal libraries


# AUTH
credentials = service_account.Credentials.from_service_account_file(
    'Resources/service_account_bigquery.json')


def largest_number(in_str):
    l = [int(x) for x in in_str.split() if x.isdigit()]
    return max(l) if l else None


def has_numbers(inputString):
    return any(char.isdigit() for char in inputString)


def get_page(url):
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:66.0) Gecko/20100101 Firefox/66.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    return soup


def to_bigquery(df, destination_table="condos.simple", project_id="jaap-scraper"):
    # Reading in the current dataset
    query = f"SELECT * FROM {destination_table}"
    df_bq = pandas_gbq.read_gbq(query, project_id=project_id, credentials=credentials)

    # Appending the two datasets and remove duplicates
    df = df.append(df_bq)
    df = df.drop_duplicates()

    # Upload newly merged dataset
    pandas_gbq.to_gbq(df, destination_table=destination_table, project_id=project_id, if_exists="replace",
                      credentials=credentials)

    print("Done with writing to BigQuery")


def find_features(list_of_features):
    house_type = [s for s in list_of_features if not has_numbers(s)]
    house_type = house_type[0] if house_type else None

    number_of_rooms = [s for s in list_of_features if "kamers" in s]
    number_of_rooms = int(re.findall("\d+", number_of_rooms[0])[0]) if number_of_rooms else None

    square_meters = [s for s in list_of_features if "m²" in s]
    square_meters = int(re.findall("\d+", square_meters[0])[0]) if square_meters else None

    return (house_type, number_of_rooms, square_meters,)
