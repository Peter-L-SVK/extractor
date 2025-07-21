import requests
import csv
from datetime import datetime
import json
import os
from dotenv import load_dotenv

# Načíta premenné prostredia zo súboru .env
load_dotenv()

API_URL = "https://api.golemio.cz/v2/municipallibraries"
API_KEY = os.getenv('GOLEMIO_API_KEY')  # API kľúč sa načíta z premenných prostredia

def fetch_and_save_data():
    if not API_KEY:
        raise ValueError("API kľúč nie je nastavený. Nastavte ho v premenných prostredia.")
    
    try:
        headers = {"X-Access-Token": API_KEY}
        response = requests.get(API_URL, headers=headers)
        
        print("HTTP Status:", response.status_code)
        
        response.raise_for_status()
        
        data = response.json()
        
        if not isinstance(data, dict) or "features" not in data:
            raise ValueError("Neočakávaný formát odpovede - chýba 'features'")
        
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        output_file = f"libraries_{datetime.now().strftime('%Y%m%d')}.csv"
        
        with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = [
                "id", "name", "street", "postal_code", "city", "region", 
                "country", "latitude", "longitude"
            ]
            
            for day in days:
                fieldnames.extend([f"{day}_opens", f"{day}_closes", f"{day}_description"])
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for feature in data["features"]:
                props = feature.get("properties", {})
                geometry = feature.get("geometry", {})
                coords = geometry.get("coordinates", [None, None])
                address = props.get("address", {})
                
                row_data = {
                    "id": props.get("id", "N/A"),
                    "name": props.get("name", "N/A"),
                    "street": address.get("street", "N/A"),
                    "postal_code": address.get("postal_code", "N/A"),
                    "city": address.get("locality", "N/A"),
                    "region": address.get("region", "N/A"),
                    "country": address.get("address_country", "Česko"),
                    "longitude": coords[0] if coords else "N/A",
                    "latitude": coords[1] if coords else "N/A"
                }
                
                opening_hours = props.get("opening_hours", [])
                if isinstance(opening_hours, str):
                    try:
                        opening_hours = json.loads(opening_hours.replace("'", '"'))
                    except:
                        opening_hours = []
                
                for day in days:
                    row_data[f"{day}_opens"] = "N/A"
                    row_data[f"{day}_closes"] = "N/A"
                    row_data[f"{day}_description"] = "N/A"
                
                for hour in opening_hours:
                    if hour.get("is_default", True):
                        day = hour.get("day_of_week")
                        if day in days:
                            row_data[f"{day}_opens"] = hour.get("opens", "N/A")
                            row_data[f"{day}_closes"] = hour.get("closes", "N/A")
                            row_data[f"{day}_description"] = hour.get("description", "N/A")
                
                writer.writerow(row_data)
                
        print(f"Dáta úspešne uložené do súboru: {output_file}")
                
    except requests.exceptions.HTTPError as err:
        print(f"HTTP Chyba: {err}\nDetail: {err.response.text}")
    except Exception as e:
        print(f"Všeobecná chyba: {e}")

if __name__ == "__main__":
    fetch_and_save_data()
