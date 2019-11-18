# Importing external libraries
from google.oauth2 import service_account
import pandas_gbq
import pandas as pd


# AUTH
credentials = service_account.Credentials.from_service_account_file(
    'Resources/service_account_bigquery.json')

def remove_rows_already_in_bq(df, destination_table="condos.simple_breda", project_id="jaap-scraper"):
    # Reading in the current dataset
    query = f"SELECT * FROM {destination_table}"
    try:
        df_bq = pandas_gbq.read_gbq(query, project_id=project_id, credentials=credentials)
    except:
        return df

    # Appending the two datasets and remove rows that are already in bq
    df_all = df.merge(df_bq.drop_duplicates(), on=['address', 'postal_code'],
                       how='left', indicator=True)

    if not any(df_all['_merge'] == 'left_only'):
        return pd.DataFrame()

    df = df[df_all['_merge'] == 'left_only']
    return df

def to_bigquery(df, destination_table="condos.simple_breda", project_id="jaap-scraper"):
    pandas_gbq.to_gbq(df, destination_table=destination_table, project_id=project_id, if_exists="append",
                      credentials=credentials)

    print("Done with writing to BigQuery")