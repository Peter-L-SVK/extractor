import pytest
import json
from unittest.mock import patch, mock_open
from golemio_extractor import get_data, save_data, process_opening_hours
import os

# Testovacie dáta
SAMPLE_API_RESPONSE = {
    "features": [
        {
            "properties": {
                "id": "1",
                "name": "Test Library",
                "address": {
                    "street": "Test Street",
                    "postal_code": "12345",
                    "locality": "Test City",
                    "region": "Test Region",
                    "address_country": "Česko"
                },
                "opening_hours": [
                    {
                        "day_of_week": "Monday",
                        "opens": "08:00",
                        "closes": "18:00",
                        "description": "Test hours",
                        "is_default": True
                    }
                ]
            },
            "geometry": {
                "coordinates": [14.0, 50.0]
            }
        }
    ]
}

def test_get_data_success():
    """
    Testuje úspešné získanie dát z API
    - Simuluje úspešnú odpoveď API s platnými dátami
    - Overuje, že funkcia vráti očakávanú štruktúru dát
    """
    with patch('requests.get') as mocked_get:
        # Nastavíme mock pre requests.get
        mocked_get.return_value.status_code = 200
        mocked_get.return_value.json.return_value = SAMPLE_API_RESPONSE
        
        # Volanie testovanej funkcie
        result = get_data()
        
        # Overenie výsledkov
        assert isinstance(result, dict)
        assert "features" in result
        assert len(result["features"]) > 0
        assert result["features"][0]["properties"]["id"] == "1"
        mocked_get.assert_called_once_with(
            "https://api.golemio.cz/v2/municipallibraries",
            headers={"X-Access-Token": os.getenv('GOLEMIO_API_KEY')}
        )

def test_get_data_failure():
    """
    Testuje správanie pri chybe API
    - Simuluje chybový stav API (404 Not Found)
    - Overuje, že funkcia správne vyvolá výnimku
    """
    with patch('requests.get') as mocked_get:
        mocked_get.return_value.status_code = 404
        mocked_get.return_value.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        
        with pytest.raises(requests.exceptions.HTTPError):
            get_data()

def test_process_opening_hours():
    """
    Testuje spracovanie otváracích hodín
    - Testuje rôzne scenáre: normálne hodiny, chýbajúce údaje, neplatný formát
    """
    # Testovacie údaje
    props = {
        "opening_hours": [
            {
                "day_of_week": "Monday",
                "opens": "08:00",
                "closes": "18:00",
                "description": "Test hours",
                "is_default": True
            },
            {
                "day_of_week": "Tuesday",
                "opens": "09:00",
                "closes": "17:00",
                "is_default": False  # Toto by sa malo ignorovať
            }
        ]
    }
    
    row_data = {}
    days = ['Monday', 'Tuesday', 'Wednesday']
    
    # Volanie testovanej funkcie
    process_opening_hours(props, row_data, days)
    
    # Overenie výsledkov
    assert row_data["Monday_opens"] == "08:00"
    assert row_data["Monday_closes"] == "18:00"
    assert row_data["Monday_description"] == "Test hours"
    assert row_data["Tuesday_opens"] == "N/A"  # Pretože is_default=False
    assert row_data["Wednesday_opens"] == "N/A"  # Pretože žiadne údaje

def test_process_opening_hours_string_input():
    """
    Testuje spracovanie otváracích hodín, keď sú vstupom reťazec
    - Simuluje prípad, keď API vráti otváracie hodiny ako JSON reťazec
    """
    props = {
        "opening_hours": "[{'day_of_week': 'Wednesday', 'opens': '10:00', 'closes': '20:00', 'is_default': true}]"
    }
    
    row_data = {}
    days = ['Monday', 'Wednesday']
    
    # Volanie testovanej funkcie
    process_opening_hours(props, row_data, days)
    
    # Overenie výsledkov
    assert row_data["Wednesday_opens"] == "10:00"
    assert row_data["Wednesday_closes"] == "20:00"
    assert row_data["Monday_opens"] == "N/A"

def test_save_data(tmp_path):
    """
    Testuje ukladanie dát do CSV súboru
    - Vytvára dočasný súbor pomocou pytest tmp_path fixture
    - Overuje, že súbor bol vytvorený a obsahuje očakávané údaje
    """
    # Vytvoríme dočasný súbor
    output_file = tmp_path / "test_output.csv"
    
    # Volanie testovanej funkcie
    save_data(SAMPLE_API_RESPONSE, str(output_file))
    
    # Overenie, že súbor existuje
    assert output_file.exists()
    
    # Overenie obsahu súboru
    with open(output_file, 'r', encoding='utf-8') as f:
        content = f.read()
        assert "Test Library" in content
        assert "08:00" in content  # Otváracie hodiny v pondelok
        assert "18:00" in content  # Zatváracie hodiny v pondelok

def test_save_data_empty_input(tmp_path):
    """
    Testuje ukladanie prázdnych dát
    - Overuje správanie funkcie, keď vstupné dáta sú prázdne
    """
    output_file = tmp_path / "empty_output.csv"
    
    # Prázdne vstupné dáta
    empty_data = {"features": []}
    
    save_data(empty_data, str(output_file))
    
    # Overenie, že súbor bol vytvorený, ale obsahuje iba hlavičku
    with open(output_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        assert len(lines) == 1  # Iba hlavička

# Spustenie testov
if __name__ == "__main__":
    pytest.main(["-v", "--cov=golemio_extractor", "--cov-report=term-missing"])
