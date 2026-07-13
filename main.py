import DataFrameToSpreadsheet
import RolimonsETL
import RolimonsDataExtraction

def mainRuntime():
  APIdata = RolimonsDataExtraction.ExtractFromAPI()
  dataframe = RolimonsETL.CreateDataFrame(APIdata)
  DataFrameToSpreadsheet.sync_sheet(dataframe)

if __name__ == "__main__":
  mainRuntime()