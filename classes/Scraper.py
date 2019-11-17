# Importing external libraries
from bs4 import BeautifulSoup
import pandas as pd
import time

# Importing internal libraries
from util.utilFunctions import *



class Scraper:
    def __init__(self, soort="koophuizen", stad_url="noord+brabant/west-noord-brabant/breda", huissoort=None):
        self.city = stad_url.rsplit("/", 1)[-1]
        self.soort = soort if soort in ["koophuizen", "huurhuizen"] else None
        self.stad_url = stad_url
        self.huissoort = huissoort if huissoort in ["appartement", "woonhuis"] else None
        self.url = f"https://www.jaap.nl/{self.soort}/{self.stad_url}/{self.huissoort + '/' if self.huissoort else ''}"
        self.n_pages = self._get_n_pages()
        self.links = []

    def _get_n_pages(self):
        soup = get_page(self.url)
        n_pages_string = soup.find("span", {"class": "page-info"})
        n_pages = largest_number(n_pages_string.text)
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

            # Download the page
            soup = get_page(f"{self.url}/p{current_page}")

            # Extract information from every house listed on the page
            for house in soup.findAll("div", {"class": "property-info"}):
                # Getting the address
                address = house.find("h2", {"class": "property-address-street"}).text

                # Getting the postal code
                postal_code = house.find("div", {"class": "property-address-zipcity"}).text
                postal_code = postal_code[:7]

                # Getting the price
                price = house.find("div", {"class": "price-info"}).text
                price = int(re.findall("\d+", price.replace(".", ""))[0]) if has_numbers(price) else None

                # Getting sold
                sold_cond1 = bool(True) if house.find("span", {"style": "color:#d32013; font-size: 15px; font-weight: bold;"}) else bool(False)
                sold_cond2 = bool(True) if house.find("span", {"style": "display: table-cell; vertical-align: middle"}) else bool(False)
                sold = sold_cond1 or sold_cond2

                # Getting the house_type, number of rooms and square_meters
                feature_list = [feature.text for feature in house.findAll("div", {"class": "property-feature"})]
                house_type, number_of_rooms, square_meters = find_features(feature_list) if feature_list else (None, None, None,)

                # Calculating additional features
                price_per_sqm = price/square_meters if all([price, square_meters]) else None

                # Making the JSON
                row_json = {"address": address, "city": self.city, "postal_code": postal_code,
                            "price": price, "sold": sold, "house_type": house_type,
                            "number_of_rooms": number_of_rooms, "square_meters": square_meters,
                            "price_per_sqm": price_per_sqm}

                # Appending it to the dataframe
                df = df.append(row_json, ignore_index=True)

        return df

    def complete_scrape(self):
        pass

