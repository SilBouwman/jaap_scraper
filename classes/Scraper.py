# Importing external libraries
from bs4 import BeautifulSoup
import pandas as pd
import requests
import re
import time

# Importing internal libraries
from util.utilFunctions import largestNumber, hasNumbers, get_page



class Scraper:
    def __init__(self, soort="koophuizen", stad_url="noord+brabant/west-noord-brabant/breda", huissoort=None):
        self.soort = soort if soort in ["koophuizen", "huurhuizen"] else None
        self.stad_url = stad_url
        self.huissoort = huissoort if huissoort in ["appartement", "woonhuis"] else None
        self.url = f"https://www.jaap.nl/{self.soort}/{self.stad_url}/{self.huissoort + '/' if self.huissoort else ''}"
        self.n_pages = self._get_n_pages()
        self.links = []


    def _get_n_pages(self):
        soup = get_page(self.url)
        n_pages_string = soup.find("span", {"class": "page-info"})
        n_pages = largestNumber(n_pages_string.text)
        return n_pages

    def _get_links(self):
        for current_page in range(0, self.n_pages):
            current_page += 1
            soup = get_page(f"{self.url}/p{current_page}")
            for link in soup.findAll("a", {"class": "property-inner"}, href=True):
                self.links.append(link["href"])

    def simple_scrape(self):
        df = pd.DataFrame()
        for current_page in range(0, self.n_pages):
            time.sleep(1)
            current_page += 1
            print(f"page {current_page} of {self.n_pages}")
            soup = get_page(f"{self.url}/p{current_page}")
            for house in soup.findAll("div", {"class": "property-info"}):
                # Getting the address
                address = house.find("h2", {"class": "property-address-street"}).text

                # Getting the postal code
                postal_code = house.find("div", {"class": "property-address-zipcity"}).text
                postal_code = postal_code[:7]

                # Getting the price
                price = house.find("div", {"class": "price-info"}).text
                price = int(re.findall("\d+", price.replace(".", ""))[0]) if hasNumbers(price) else None

                # Getting sold
                sold = bool(True) if house.find("span", {"style": "color:#d32013; font-size: 15px; font-weight: bold;"}) else bool(False)

                # Getting the house_type, number of rooms and square_meters
                feature_list = [feature.text for feature in house.findAll("div", {"class": "property-feature"})]
                house_type = feature_list[0] if feature_list else None
                number_of_rooms = int(re.findall("\d+", feature_list[1])[0]) if len(feature_list) > 1 else None
                square_meters = int(re.findall("\d+", feature_list[2])[0]) if len(feature_list) > 2 else None

                # Making the JSON
                row_json = {"address": address, "postal_code": postal_code, "price": price,
                            "sold": sold, "house_type": house_type,
                            "number_of_rooms": number_of_rooms, "square_meters": square_meters}

                # Appending it to the dataframe
                df = df.append(row_json, ignore_index=True)

        return df

