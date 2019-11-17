# Importing external libraries

# Importign internal libraries
from classes.Scraper import Scraper


scraper = Scraper("koophuizen", "noord+brabant/west-noord-brabant/breda")

print(scraper.simple_scrape())
