# Importing external libraries
from bs4 import BeautifulSoup
import datetime
import requests

# Importing internal libraries
from util.utilFunctions import largestNumber



class Scraper:
    def __init__(self, soort, stad_url, huissoort=None):
        self.soort = soort if soort in ["koophuizen", "huurhuizen"] else None
        self.stad_url = stad_url
        self.huissoort = huissoort if huissoort in ["appartement", "woonhuis"] else None
        self.url = f"https://www.jaap.nl/{self.soort}/{self.stad_url}/{self.huissoort + '/' if self.huissoort else ''}"
        self.n_pages = self._get_n_pages()
        self.links = []


    def _get_n_pages(self):
        headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:66.0) Gecko/20100101 Firefox/66.0"}
        response = requests.get(self.url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        n_pages_string = soup.find("span", {"class": "page-info"})
        n_pages = largestNumber(n_pages_string.text)
        return n_pages

    def _get_links(self):
        headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:66.0) Gecko/20100101 Firefox/66.0"}
        for current_page in range(0, self.n_pages):
            current_page += 1
            response = requests.get(f"{self.url}/p{current_page}", headers=headers)
            soup = BeautifulSoup(response.text, "html.parser")
            for link in soup.findAll("a", {"class": "property-inner"}, href=True):
                self.links.append(link["href"])

    def simple_scrape(self):
        headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:66.0) Gecko/20100101 Firefox/66.0"}
        for current_page in range(0, self.n_pages):
            current_page += 1
            response = requests.get(f"{self.url}/p{current_page}", headers=headers)
            soup = BeautifulSoup(response.text, "html.parser")
            for house in soup.findAll("div", {"class": "property-info"}):
                print(house.find("h2", {"class": "property-address-street"}).text)
                print(house.find("div", {"class": "property-address-zipcity"}).text)
                print(house.find("div", {"class": "property-features"}).text)








