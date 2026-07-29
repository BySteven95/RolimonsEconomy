from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd
import os, sys

# 1. Configurar Credenciales y Cliente de BigQuery
PROJECT_ID = "robloxtradinginfo" 
DATASET_ID = "rolimons_data"
TABLE_ID = "history"
TABLE_REF = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

def resourcePath(relative_path):
        # Devuelve la ruta absoluta a un recurso, compatible con PyInstaller.
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

creds = service_account.Credentials.from_service_account_file(resourcePath("credentials.json"))
client = bigquery.Client(credentials=creds, project=PROJECT_ID)

# 2. Definir el Esquema de la Tabla 
SCHEMA = [
  bigquery.SchemaField("extraction_timestamp", "TIMESTAMP", mode="REQUIRED"),
  bigquery.SchemaField("item_id", "INTEGER", mode="REQUIRED"),
  bigquery.SchemaField("name", "STRING"),
  bigquery.SchemaField("acronym", "STRING"),
  bigquery.SchemaField("rap", "INTEGER"),
  bigquery.SchemaField("value", "INTEGER"),
  bigquery.SchemaField("default_value", "INTEGER"),
  bigquery.SchemaField("demand", "STRING"),
  bigquery.SchemaField("trend", "STRING"),
  bigquery.SchemaField("projected", "BOOLEAN"),
  bigquery.SchemaField("hyped", "BOOLEAN"),
  bigquery.SchemaField("rare", "BOOLEAN"),
]

    

def init_bigquery_table():
  """Crea la tabla si no existe, asegurando la estructura correcta."""
  try:
    client.get_table(TABLE_REF)
    print(f"La tabla {TABLE_ID} ya existe.")
  except Exception:
    print(f"Creando la tabla {TABLE_ID}...")
    table = bigquery.Table(TABLE_REF, schema=SCHEMA)
    client.create_table(table)

def sync_to_bigquery(df: pd.DataFrame):
  """Inserta los nuevos registros del DataFrame en BigQuery."""

  init_bigquery_table()

  df.columns = [c.lower().replace(" ", "_") for c in df.columns]

  # Configuración de la carga
  job_config = bigquery.LoadJobConfig(
    schema=SCHEMA,
    write_disposition="WRITE_APPEND"
  )

  print("Cargando datos a BigQuery...")
  job = client.load_table_from_dataframe(df, TABLE_REF, job_config=job_config)
  job.result()  # Espera a que termine el proceso
  print(f"Se insertaron correctamente {len(df)} filas.")
