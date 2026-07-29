from google.cloud import bigquery
from google.oauth2 import service_account
import os, sys
# ==========================================
# CONFIGURACIÓN DE BIGQUERY
# ==========================================
PROJECT_ID = "robloxtradinginfo" 
DATASET_ID = "rolimons_data"


def resourcePath(relative_path):
        # Devuelve la ruta absoluta a un recurso, compatible con PyInstaller.
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

creds = service_account.Credentials.from_service_account_file(resourcePath("credentials.json"))
client = bigquery.Client(credentials=creds, project=PROJECT_ID)

# Mapeo oficial de Rolimons para la columna Demand
DEMAND_MAP = {
    -1: "None",
    0: "Terrible",
    1: "Low",
    2: "Normal",
    3: "High",
    4: "Amazing"
}

# ==========================================
# ESQUEMAS DE LAS TABLAS
# ==========================================
HISTORY_SCHEMA = [
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

PREDICTION_SCHEMA = [
    bigquery.SchemaField("item_id", "INTEGER", mode="REQUIRED"),
    bigquery.SchemaField("name", "STRING"),
    bigquery.SchemaField("current_value", "INTEGER"),
    bigquery.SchemaField("predicted_direction", "STRING"),  # "up", "down", "stable"
    bigquery.SchemaField("prediction_timestamp", "TIMESTAMP", mode="REQUIRED"),
]

# ==========================================
# FUNCIONES DE INICIALIZACIÓN
# ==========================================
def train_market_model():
    """
    Envía la orden a BigQuery para entrenar o actualizar el modelo de Random Forest
    basándose en el histórico acumulado.
    """
    
    # Query de entrenamiento (utiliza los datos de la tabla 'history')
    query = f"""
    CREATE OR REPLACE MODEL `{PROJECT_ID}.{DATASET_ID}.model_item_direction`
    OPTIONS(
      MODEL_TYPE='RANDOM_FOREST_CLASSIFIER',
      NUM_TRIALS=5,                          -- Optimiza hiperparámetros automáticamente
      INPUT_LABEL_COLS=['target_direction']  -- Variable que queremos predecir
    ) AS

    WITH historico_con_futuro AS (
      SELECT 
        item_id,
        rap,
        value,
        demand,
        trend,
        projected,
        hyped,
        rare,
        -- Compara el valor actual con el que tendrá el ítem 3 días después
        LEAD(value, 3) OVER(PARTITION BY item_id ORDER BY extraction_timestamp) as future_value
      FROM 
        `{PROJECT_ID}.{DATASET_ID}.history`
      -- TIP DE OPTIMIZACIÓN: Solo entrena con los últimos 90 días para no gastar cuota de más
      WHERE extraction_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY)
    ),
    datos_etiquetados AS (
      SELECT *,
        CASE 
          WHEN future_value > value THEN 'up'
          WHEN future_value < value THEN 'down'
          ELSE 'stable'
        END as target_direction
      FROM historico_con_futuro
      WHERE future_value IS NOT NULL
    )

    SELECT 
      rap, 
      value, 
      demand, 
      trend, 
      projected, 
      hyped, 
      rare, 
      target_direction 
    FROM 
      datos_etiquetados;
    """
    
    print("🚀 Iniciando el entrenamiento del modelo Random Forest en BigQuery...")
    print("Esto puede tardar unos minutos ya que Google Cloud está optimizando los árboles...")
    
    try:
        # Ejecutar el query de entrenamiento
        query_job = client.query(query)
        
        # Esperar a que el entrenamiento termine de forma síncrona
        query_job.result() 
        
        print("✅ ¡Modelo 'model_item_direction' entrenado y guardado exitosamente en BigQuery!")
        
    except Exception as e:
        print(f"❌ Error al entrenar el modelo: {e}")

def generate_daily_predictions():
    """Llama al modelo de Random Forest y guarda las predicciones saltándose el bloqueo de Sandbox."""
    
    query = f"""
    WITH ultima_foto AS (
      SELECT * 
      FROM `{PROJECT_ID}.{DATASET_ID}.history`
      WHERE extraction_timestamp = (SELECT MAX(extraction_timestamp) FROM `{PROJECT_ID}.{DATASET_ID}.history`)
    )
    
    SELECT 
      CAST(item_id AS INT64) as item_id,
      name,
      CAST(value AS INT64) as current_value,
      predicted_target_direction as predicted_direction,
      CURRENT_TIMESTAMP() as prediction_timestamp
    FROM 
      ML.PREDICT(MODEL `{PROJECT_ID}.{DATASET_ID}.model_item_direction`, TABLE ultima_foto)
    """
    
    try:
        print("Ejecutando predicciones diarias en modo Sandbox...")
        # 2. Descargamos el resultado del modelo directamente a un DataFrame de Pandas en Python
        query_job = client.query(query)
        df_predictions = query_job.to_dataframe()
        
        if df_predictions.empty:
            print("No se generaron predicciones (¿el modelo está vacío?).")
            return

        # 3. Insertamos los datos usando el método tradicional de carga (Permitido en la capa gratis)
        table_ref = f"{PROJECT_ID}.{DATASET_ID}.item_predictions"
        job_config = bigquery.LoadJobConfig(
            schema=PREDICTION_SCHEMA,
            write_disposition="WRITE_APPEND", # O cambia a "WRITE_TRUNCATE" si solo quieres ver las predicciones de hoy
        )
        
        job = client.load_table_from_dataframe(df_predictions, table_ref, job_config=job_config)
        job.result()
        print(f"✅ ¡Predicciones diarias de {len(df_predictions)} ítems guardadas con éxito en 'item_predictions'!")
        
    except Exception as e:
        print(f"\n⚠️ Nota: No se pudieron generar las predicciones diarias: {e}\n")
