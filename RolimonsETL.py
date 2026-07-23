from datetime import datetime, timezone
import pandas as pd

# Diccionario de mapeo según la documentación de Rolimons
DEMAND_MAP = {
    -1: "None",
    0: "Terrible",
    1: "Low",
    2: "Normal",
    3: "High",
    4: "Amazing"
}

TREND_MAP = {
    -1: "None",
    0: "Lowering",
    1: "Unstable",
    2: "Stable",
    3: "Raising",
    4: "Fluctuating"
}

def CreateDataFrame(data):
    extraction_timestamp = datetime.now(timezone.utc)
    rows = []

    for item_id, item in data["items"].items():
        # Extraemos los valores numéricos de demand y trend
        raw_demand = item[5]
        raw_trend = item[6]

        # Convertimos el número a su texto correspondiente usando el mapa.
        # Si llega un valor raro que no está en el mapa, pone "Unknown"
        demand_str = DEMAND_MAP.get(raw_demand, "Unknown") if raw_demand is not None else None
        
        # Hacemos lo mismo con trend
        trend_str = str(raw_trend) if raw_trend is not None else None

        rows.append({
            "Extraction Timestamp": extraction_timestamp,
            "Item ID": int(item_id),
            "Name": str(item[0]) if item[0] is not None else None,
            "Acronym": str(item[1]) if item[1] is not None else None,
            "RAP": int(item[2]) if item[2] is not None else 0,
            "Value": int(item[3]) if item[3] is not None else 0,
            "Default Value": int(item[4]) if item[4] is not None else 0,
            
            # Pasamos las variables ya convertidas a texto legible
            "Demand": demand_str,
            "Trend": trend_str,
            
            "Projected": bool(item[7]) if item[7] is not None else False,
            "Hyped": bool(item[8]) if item[8] is not None else False,
            "Rare": bool(item[9]) if item[9] is not None else False,
        })

    df = pd.DataFrame(rows)
    df.columns = [c.lower().replace(" ", "_") for c in df.columns]

    return df