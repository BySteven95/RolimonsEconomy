import requests

def ExtractFromAPI():
  url = "https://www.rolimons.com/itemapi/itemdetails"

  response = requests.get(url)

  data = response.json()

  print(data.keys())

  return data

