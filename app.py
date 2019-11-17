# Importing external libraries
from datetime import datetime
import pandas as pd

# Importing internal libraries
from classes.Scraper import Scraper
from util.utilFunctions import to_bigquery

def main():
    # Initialize the Class
    scraper = Scraper("koophuizen", "noord+brabant/west-noord-brabant/breda")

    # Scrape Jaap.nl
    scraped_df = scraper.simple_scrape()

    # Save it locally on a csv
    scraped_df.to_csv(f"Resources/house_info/simple/data_{datetime.now().date()}.csv", index=False)

    # Upload it to bigQuery
    to_bigquery(scraped_df)

if __name__ == "__main__":
    main()


