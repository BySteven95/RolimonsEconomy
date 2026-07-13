import pandas as pd
from datetime import datetime
import RolimonsDataExtraction

def CreateDataFrame(data):

    # Timestamp único para toda la extracción
    extraction_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    rows = []

    for item_id, item in data["items"].items():
        rows.append({
            "Extraction Timestamp": extraction_timestamp,
            "Item ID": item_id,
            "Name": item[0],
            "Acronym": item[1],
            "RAP": item[2],
            "Value": item[3],
            "Default Value": item[4],
            "Demand": item[5],
            "Trend": item[6],
            "Projected": item[7],
            "Hyped": item[8],
            "Rare": item[9],
        })

    return pd.DataFrame(rows)

if __name__ == "__main__":
    data = RolimonsDataExtraction.ExtractFromAPI()
    CreateDataFrame(data)