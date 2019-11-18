# Importing external libraries

# Importing internal libraries
from classes.Scraper import Scraper
from util.cloudFunctions import *
from util.locationFunctions import *
from util.utilFunctions import *

def main(stad_url, method="simple", type="koophuizen"):
    # TODO make urls so that you only need the city

    # Initialize the Class
    scraper = Scraper(soort=type, stad_url=stad_url)

    # Scrape Jaap.nl
    if method == "simple":
        scraped_df = scraper.simple_scrape()
    elif method == "complete":
        scraped_df = scraper.complete_scrape()
    else:
        raise ValueError("Please supply a valid scraping method: 'simple', 'complete'")

    # Load in bigQuery dataset and remove duplicates
    destination_table =f"condos.{method}_{scraper.city}"
    scraped_df = remove_rows_already_in_bq(scraped_df, destination_table=destination_table)

    if scraped_df.empty:
        print("Did not upload anything to bigquery, since it does not have new data")
        return "Did not upload anything to bigquery, since it does not have new data"

    # Get lat and lng of the addresses
    for i in range(0,len(scraped_df)):
        if i % 10 == 0:
            print(f"iteration {i} of {len(scraped_df)}")
        scraped_df["lat"].iloc[i], scraped_df["lng"].iloc[i] = get_coordinates(scraped_df["address"].iloc[i], scraper.city)
        scraped_df["neighbourhood"].iloc[i], scraped_df["living_units"].iloc[i] = get_neighbourhood(scraped_df["postal_code"].iloc[i])

    # Upload it to bigQuery
    to_bigquery(scraped_df, destination_table=destination_table)

    # Save it locally on a csv
    path = f"Resources/house_info/{method}/{scraper.city}/"
    save_as_csv(scraped_df, path=path)

if __name__ == "__main__":
    main(method="simple", type="koophuizen", stad_url="noord+brabant/west-noord-brabant/breda")



