import gspread
from google.oauth2.service_account import Credentials

EXPECTED_HEADERS = [
    "Extraction Timestamp",
    "Item ID",
    "Name",
    "Acronym",
    "RAP",
    "Value",
    "Default Value",
    "Demand",
    "Trend",
    "Projected",
    "Hyped",
    "Rare"
]

scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

creds = Credentials.from_service_account_file(
    "credentials.json",
    scopes=scopes
)

gc = gspread.authorize(creds)


spreadsheet = gc.open("RobloxRolimonsDashboardData")
worksheet = spreadsheet.worksheet("History")

def sync_sheet(df):
    
  values = worksheet.get_all_values()

  # Hoja completamente vacía
  if not values:
      worksheet.append_row(EXPECTED_HEADERS)
      worksheet.append_rows(
        df.values.tolist(),
        value_input_option="USER_ENTERED"
      )
      return

  # Eliminar filas completamente vacías
  non_empty_rows = [
    row for row in values
    if any(str(cell).strip() for cell in row)
  ]

  # Si había filas vacías, reconstruimos la hoja
  if len(non_empty_rows) != len(values):
    worksheet.clear()
    worksheet.update("A1", non_empty_rows)

  # Volvemos a leer el contenido
  values = worksheet.get_all_values()

  # Validar encabezado
  header = values[0]

  if header != EXPECTED_HEADERS:
    worksheet.update(
      range_name="A1",
      values=[EXPECTED_HEADERS]
    )

  # Agregar nuevos registros
  worksheet.append_rows(
    df.values.tolist(),
    value_input_option="USER_ENTERED"
  )