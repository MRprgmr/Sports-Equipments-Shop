import requests

def get_usd_to_uzs_currency():
    """Return USD currency rate"""

    api = "https://cbu.uz/uz/arkhiv-kursov-valyut/json/"
    data = requests.get(api).json()
    for i in data:
        if i['Ccy'] == 'USD':
            return int(float(i['Rate']))

usd_in_uzs = get_usd_to_uzs_currency()