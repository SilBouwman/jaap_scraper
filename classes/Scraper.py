# Importing external libraries
import time
import numpy as np

# Importing internal libraries
from util.utilFunctions import *
from classes.gcp import *


class Scraper:
    def __init__(self, area_to_search, type="koophuizen", huissoort=None):
        self.type = type if type in ["koophuizen", "huurhuizen"] else "koophuizen"
        self.area_to_search = area_to_search
        self.extended_url = self._get_url_extender()
        self.huissoort = huissoort if huissoort in ["appartement", "woonhuis"] else None
        self.url = f"{self.extended_url}/{self.huissoort + '/' if self.huissoort else ''}"
        self.n_pages = self._get_n_pages()
        self.links = []

    @staticmethod
    def _get_page(url):
        headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:66.0) Gecko/20100101 Firefox/66.0"}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        return soup

    @staticmethod
    def _find_features(list_of_features):
        house_type = [s for s in list_of_features if not has_numbers(s)]
        house_type = house_type[0] if house_type else None

        number_of_rooms = [s for s in list_of_features if "kamers" in s]
        number_of_rooms = int(re.findall("\d+", number_of_rooms[0])[0]) if number_of_rooms else None

        square_meters = [s for s in list_of_features if "m²" in s]
        square_meters = int(re.findall("\d+", square_meters[0])[0]) if square_meters else None

        return (house_type, number_of_rooms, square_meters,)

    @staticmethod
    def _clean_string_from_chars(series, chars=None):
        if chars is None:
            chars = ['.', '€', 'm²', 'm³']
        for ch in chars:
            series = series.str.replace(ch, "")
        return series

    def _get_n_pages(self):
        soup = self._get_page(self.url)
        n_pages_string = soup.find("span", {"class": "page-info"})
        n_pages = largest_number(n_pages_string.text)
        return n_pages

    def _get_links(self):
        for current_page in range(0, self.n_pages):
            current_page += 1
            soup = self._get_page(f"{self.url}/p{current_page}")
            for link in soup.findAll("a", {"class": "property-inner"}, href=True):
                self.links.append(link["href"])

    def _get_url_extender(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'it-IT,it;q=0.8,en-US;q=0.5,en;q=0.3',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://www.jaap.nl',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Referer': f'https://www.jaap.nl/{self.type}/',
            'Upgrade-Insecure-Requests': '1',
        }

        data = {
            'action': 'searchExtensive',
            'url': f'/{self.type}',
            'search_input_extensive': self.area_to_search
        }

        response = requests.post('https://www.jaap.nl/', headers=headers, data=data)
        if response.url == "https://www.jaap.nl/":
            raise ValueError("Did not recognize the city you're trying to search")
        return response.url

    @staticmethod
    def _check_if_sold(soup):
        # Getting sold
        sold_cond1 = bool(True) if soup.find("span", {
            "style": "color:#d32013; font-size: 15px; font-weight: bold;"}) else bool(False)
        sold_cond2 = bool(True) if soup.find("span", {
            "style": "display: table-cell; vertical-align: middle"}) else bool(False)
        sold = sold_cond1 or sold_cond2
        return sold

    @staticmethod
    def _parse_features(tables, selected_tables):
        df = pd.DataFrame()
        for table in selected_tables:
            t = tables[table].transpose()
            new_header = t.iloc[0]
            t = t[1:]
            t.columns = new_header
            t.reset_index(drop=True, inplace=True)
            df = pd.concat([df, t], axis=1)
        return df


    def simple_scrape(self):
        df = pd.DataFrame()

        for current_page in range(0, self.n_pages):
            time.sleep(1)
            current_page += 1
            print(f"page {current_page} of {self.n_pages}")

            # Download the page
            soup = self._get_page(f"{self.url}/p{current_page}")

            # Extract information from every house listed on the page
            for house in soup.findAll("div", {"class": "property-info"}):
                # Getting the address
                address = house.find("h2", {"class": "property-address-street"}).text

                # Getting the postal code
                postal_code = house.find("div", {"class": "property-address-zipcity"}).text
                postal_code = postal_code[:7] if has_numbers(postal_code) else None

                # Getting the price
                price = house.find("div", {"class": "price-info"}).text
                price = int(re.findall("\d+", price.replace(".", ""))[0]) if has_numbers(price) else None

                # Getting sold
                sold = self._check_if_sold(house)

                # Getting the house_type, number of rooms and square_meters
                feature_list = [feature.text for feature in house.findAll("div", {"class": "property-feature"})]
                house_type, number_of_rooms, square_meters = self._find_features(feature_list) if feature_list else (
                None, None, None,)

                # Calculating additional features
                price_per_sqm = price / square_meters if all([price, square_meters]) else None

                # Making the JSON
                row_json = {"address": address, "city": None, "postal_code": postal_code,
                            "price": price, "sold": sold, "house_type": house_type,
                            "number_of_rooms": number_of_rooms, "square_meters": square_meters,
                            "price_per_sqm": price_per_sqm, "lat": None, "lng": None,
                            "neighbourhood": None, "living_units": None}

                # Appending it to the dataframe
                df = df.append(row_json, ignore_index=True)

        df = df.drop_duplicates()
        df = df.astype({"address": "object", "city": "object", "postal_code": "object",
                        "price": "float64", "sold": "bool", "house_type": "object",
                        "number_of_rooms": "float64", "square_meters": "float64",
                        "price_per_sqm": "float64", "lat": "float64", "lng": "float64",
                        "neighbourhood": "object", "living_units": "float64"})
        return df

    def complete_scrape(self):
        self._get_links()
        n_link = 0
        df = pd.DataFrame()

        for link in self.links:
            n_link += 1
            time.sleep(1)
            print(f"link {n_link} of {len(self.links)} links total")

            # Download the page
            soup = self._get_page(link)

            # Getting the basic house info
            address = soup.find("div", {"class": "detail-address-street"}).text

            postal_code = soup.find("div", {"class": "detail-address-zipcity"}).text
            postal_code = postal_code[:7] if has_numbers(postal_code) else None

            price = soup.find("div", {"class": "detail-address-price"}).text
            price = int(re.findall("\d+", price.replace(".", ""))[0]) if has_numbers(price) else None

            sold = self._check_if_sold(soup)

            # Scraping the selected scraped_tables on the page
            selected_tables = ["Woninggegevens", "Energie", "Binnen", "Buiten", "Statistiek", "Vraagprijs", "Prijs"]
            scraped_tables = pd.read_html(str(soup), flavor="bs4", index_col=None)

            tables = {}
            for scraped_table in scraped_tables:
                # Removing unwanted scraped_tables
                if not list(scraped_table)[0] in selected_tables:
                    continue

                # Cleaning the scraped data
                scraped_table.dropna(axis=0, how='all', inplace=True)
                scraped_table.dropna(axis=1, how='all', inplace=True)

                # Basic cleaning of columns
                cols = list(scraped_table)
                for col in cols:
                    scraped_table[col] = scraped_table[col].astype(str)
                    scraped_table[col] = self._clean_string_from_chars(scraped_table[col])

                # Coupling the scraped_tables with their name
                tables[cols[0]] = scraped_table

            # Extracting all the usefull information
            row_pd = self._parse_features(tables, selected_tables)
            row_json = {"address": address, "city": None, "postal_code": postal_code,
                         "price": price, "sold": sold}
            row_pd = row_pd.join(pd.DataFrame(row_json, index=row_pd.index))

            # Appending it to the dataframe
            df = df.append(row_pd, ignore_index=True)
            print(df.columns)
        # Checking the data
        df = df.drop_duplicates()
        df = df.astype({"address": "object", "city": "object", "postal_code": "object",
                        "price": "float64", "sold": "bool", "house_type": "object",
                        "number_of_rooms": "float64", "square_meters": "float64",
                        "price_per_sqm": "float64", "lat": "float64", "lng": "float64",
                        "neighbourhood": "object", "living_units": "float64"})

        dtypes = {'Type': '', 'Bouwjaar': '', 'Woonoppervlakte': '',                                                                                                                           ',
                'Inhoud': '', 'Perceeloppervlakte': '', 'Bijzonderheden': '',                                                                                                                             ',
                'Isolatie': '', 'Verwarming': '', 'Energielabel (geschat)': '',                                                                                                                                 ',
                'Energieverbruik (geschat)': '', 'Staat onderhoud': '', 'Kamers' : '',                                                                                                                                ',
                'Slaapkamers': '', 'Sanitaire voorzieningen': '', 'Keuken': '',                                                                                                                                 ',
                'Staat onderhoud': '', 'Staat schilderwerk': '', 'Tuin': '',                                                                                                                                 ',
                'Uitzicht': '', 'Balkon': '', 'Garage': '', 'Aantal keer getoond': '',                                                                                                                                 ',
                'Aantal keer getoond gisteren': '', 'Geplaatst op': '', 'Huidige vraagprijs': '',                                                                                  ',
                'Oorspronkelijke vraagprijs': '', 'Daling / stijging vraagprijs': '', 'Prijs': '',                                                                                   ',
                'Prijs per': '', 'Tijd in de verkoop': '', 'address': '',
                'city': '', 'postal_code': '', 'price': '', 'sold': ''}

        return df

















