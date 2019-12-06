# Importing external libraries
import requests
import os
from bs4 import BeautifulSoup
import re
from datetime import datetime
import json

# Importing internal libraries


def largest_number(in_str):
    l = [int(x) for x in in_str.split() if x.isdigit()]
    return max(l) if l else None


def has_numbers(inputString):
    return any(char.isdigit() for char in inputString)


def save_as_csv(df, path):
    if not os.path.exists(path):
        os.makedirs(path)

    filename = f"{datetime.now().date()}.csv"
    df.to_csv(f"{path}{filename}", index=False)



