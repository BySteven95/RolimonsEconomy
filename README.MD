# Rolimons Economy Extractor

Roblox Economy Extractor es un proyecto en Python para extraer información de mercado de ítems de Roblox desde la API de Rolimons, transformarla en un DataFrame, cargarla a Google BigQuery y generar predicciones de dirección de precio mediante modelos de Machine Learning.

El proyecto incluye además una interfaz gráfica sencilla construida con PySide6 para controlar los procesos de extracción, carga y predicción.

## 🚀 Funcionalidades

- Extracción de datos desde la API de Rolimons.
- Transformación y normalización de datos en un DataFrame.
- Carga automática de datos históricos a BigQuery.
- Entrenamiento y generación de predicciones con Random Forest en BigQuery.
- Interfaz gráfica para iniciar/detener procesos de forma sencilla.

## 🧱 Tecnologías utilizadas

- Python
- Pandas
- Requests
- PySide6
- Google Cloud BigQuery
- Google Auth
- Scikit-learn / modelos de BigQuery ML (via SQL)

## 📦 Requisitos

- Python 3.10 o superior
- Acceso a una cuenta de Google Cloud con BigQuery habilitado
- Archivo de credenciales de servicio en formato JSON llamado `credentials.json`

## ⚙️ Instalación

1. Clona este repositorio:
   ```bash
   git clone <url-del-repositorio>
   cd RobloxEconomyExtractor
   ```

2. Crea y activa un entorno virtual:
   ```bash
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Coloca tu archivo de credenciales en la raíz del proyecto:
   ```bash
   credentials.json
   ```

## ▶️ Uso

Ejecuta la interfaz principal:

```bash
python main.py
```

Desde la ventana podrás:

- Iniciar el proceso diario de extracción histórica y predicción.
- Iniciar el proceso semanal de entrenamiento.
- Detener los procesos cuando sea necesario.

## 📁 Estructura del proyecto

- [main.py](main.py): interfaz gráfica y control de procesos.
- [RolimonsDataExtraction.py](RolimonsDataExtraction.py): extracción de datos desde la API de Rolimons.
- [RolimonsETL.py](RolimonsETL.py): transformación de datos a DataFrame.
- [DataFrameToBigQuery.py](DataFrameToBigQuery.py): carga de datos a BigQuery.
- [RandomForestBigQuery.py](RandomForestBigQuery.py): entrenamiento del modelo y generación de predicciones.
- [requirements.txt](requirements.txt): dependencias del proyecto.
- [credentials.json](credentials.json): credenciales de servicio de Google Cloud (no subir al repositorio si contiene información sensible).

## 🔧 Configuración importante

Antes de ejecutar el proyecto, revisa los siguientes valores en los scripts:

- `PROJECT_ID`
- `DATASET_ID`
- `TABLE_ID`
- Ruta del archivo `credentials.json`

Asegúrate de que tu proyecto en BigQuery tenga las tablas y permisos correctos para cargar datos y ejecutar consultas.

## 📝 Notas

- Los procesos están configurados para ejecutarse de forma periódica en la interfaz.
- Si deseas probarlos más rápido, puedes reducir los intervalos en [main.py](main.py).
- El proyecto está pensado como una base para análisis de mercado y predicción de tendencias en Roblox.

## 👤 Autores

Proyecto desarrollado por Laura Aldana y Daniel Osorio.
