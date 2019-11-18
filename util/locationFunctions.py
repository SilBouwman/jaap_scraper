# Importing external libraries
import googlemaps
import pandas as pd

# Importing internal libraries
from util.utilFunctions import *

# Setting credentials
API_KEY_GOOGLE_MAPS = open("Resources/api_key_google_maps.txt").read()
gmaps = googlemaps.Client(API_KEY_GOOGLE_MAPS)

# Reading in the neighbourhood dataset
neighbourhood_codes = pd.read_csv("Resources/datasets/neighbourhood_codes.csv")

def get_coordinates(address, city):
    address = f"{address}, {city}"
    try:
        geocode_result = gmaps.geocode(address)
        geocode_result = geocode_result[0].get("geometry").get("location")
        lat = geocode_result["lat"]
        lng = geocode_result["lng"]
    except:
        lat, lng = (None, None)

    return (lat, lng,)


def get_neighbourhood(zipcode):
    if len(zipcode) < 4 or not has_numbers(zipcode):
        return (None, None,)
    neighbourhood_code = int(zipcode[:4])
    row = neighbourhood_codes[neighbourhood_codes.neighbourhood_code == neighbourhood_code]
    if row.empty:
        return (None, None,)
    return (row.neighbourhood.iloc[0], row.living_units.iloc[0],)








