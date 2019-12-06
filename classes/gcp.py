# Importing external libraries
from google.oauth2 import service_account
import pandas_gbq
import pandas as pd


# AUTH
CREDENTIALS = service_account.Credentials.from_service_account_file(
    'Resources/service_account_bigquery.json')

class GCP:
    def __init__(self, project_id="jaap-scraper", destination_table="condos.simple_breda"):
        self.project_id = project_id
        self.destination_table = destination_table

    @staticmethod
    def _join_on_left(df1, df2):
        df_all = pd.merge(df1, df2.drop_duplicates(), on=['address', 'postal_code'], how="left", indicator=True,
                          suffixes=('', '_y'))

        if not any(df_all['_merge'] == 'left_only'):
            return pd.DataFrame()

        df = df_all[df_all['_merge'] == 'left_only']
        df = df.drop("_merge", 1)
        df.drop(list(df.filter(regex='_y$')), axis=1, inplace=True)
        return df

    def remove_rows_already_in_bq(self, df):
        # Reading in the current dataset
        query = f"SELECT * FROM {self.destination_table}"
        try:
            df_bq = pandas_gbq.read_gbq(query, project_id=self.project_id, credentials=CREDENTIALS)
        except:
            return df

        # Appending the two datasets and remove rows that are already in bq
        df = self._join_on_left(df, df_bq)
        return df

    def to_bigquery(self, df):
        pandas_gbq.to_gbq(df, destination_table=self.destination_table, project_id=self.project_id, if_exists="append",
                          credentials=CREDENTIALS)

        print("Done with writing to BigQuery")