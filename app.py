# Importing external libraries

# Importing internal libraries
from classes.Scraper import Scraper
from classes.gcp import GCP
from util.locationFunctions import *
from util.utilFunctions import *

def main(area_to_search, method="simple", type="koophuizen", geocode=False):

    # Initialize the Class
    scraper = Scraper(area_to_search=area_to_search, type=type)

    # Scrape Jaap.nl
    if method == "simple":
        scraped_df = scraper.simple_scrape()
    elif method == "complete":
        scraped_df = scraper.complete_scrape()
        print(scraped_df)
    else:
        raise ValueError("Please supply a valid scraping method: 'simple', 'complete'")

    # # Load in bigQuery dataset and remove duplicates
    # destination_table =f"{type}_{method}.{scraper.area_to_search}"
    # gcp = GCP(destination_table=destination_table)
    # scraped_df = gcp.remove_rows_already_in_bq(scraped_df)
    #
    # if scraped_df.empty:
    #     print("Did not upload anything to bigquery, since it does not have new data")
    #     return None
    #
    # # Get lat and lng of the addresses
    # for i in range(0,len(scraped_df)):
    #     if i % 10 == 0:
    #         print(f"iteration {i} of {len(scraped_df)}")
    #     scraped_df["city"].iloc[i], scraped_df["neighbourhood"].iloc[i], scraped_df["living_units"].iloc[i] = get_neighbourhood(scraped_df["postal_code"].iloc[i])
    #     if geocode:
    #         scraped_df["lat"].iloc[i], scraped_df["lng"].iloc[i] = get_coordinates(scraped_df["address"].iloc[i], scraper.area_to_search)
    #
    #
    # # Upload it to bigQuery
    # gcp.to_bigquery(scraped_df)
    #
    # # Save it locally on a csv
    # path = f"Resources/house_info/{type}/{method}/{scraper.area_to_search}/"
    # save_as_csv(scraped_df, path=path)

if __name__ == "__main__":
    main(area_to_search="noordgouwe", method="complete", type="koophuizen")





