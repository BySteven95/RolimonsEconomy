import DataFrameToBigQuery
import RolimonsETL
import RolimonsDataExtraction

def mainRuntime():
  APIdata = RolimonsDataExtraction.ExtractFromAPI()
  dataframe = RolimonsETL.CreateDataFrame(APIdata)
  DataFrameToBigQuery.sync_to_bigquery(dataframe)

if __name__ == "__main__":
  mainRuntime()