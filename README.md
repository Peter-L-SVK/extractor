# Golemio Libraries Data Extractor

## Popis
Skript na denné sťahovanie dát o knižniciach z API Golemio.

## Požiadavky
- Python 3.8+
- Knižnice: requests, python-dotenv
- requirements.txt
```
requests>=2.25.1
python-dotenv>=0.19.0
```
## Inštalácia
1. Naklonujte repozitár
2. Vytvorte virtuálne prostredie: `python -m venv venv`
3. Aktivujte prostredie:
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`
4. Nainštalujte závislosti: 
```pip install -r requirements.txt```


5. Vytvorte súbor `.env` a pridajte váš API kľúč: GOLEMIO_API_KEY=your_api_key_here
6. Spustite skript: 
```bash
python golemio_extractor.py
```

## Automatizácia
Naplánujte denné spustenie cez `cron` (Linux/macOS) alebo Task Scheduler (Windows):
```bash
0 7 * * 1 /usr/bin/python3 /cesta/k/skriptu/golemio_extractor.py
```

## Ako spustiť testy:

1. Nainštalujte potrebné balíčky:
   ```bash
   pip install pytest pytest-cov requests
   ```
2. Spustite testy s pokrytím kódu:
   ```bash
   python test_golemio_extractor.py
   ```

### Výstup testov bude obsahovať:

-  Zoznam úspešných testov
-  Akékoľvek zlyhané testy
-  Percento pokrytia kódu testami
-  Informácie o tom, ktoré časti kódu nie sú testované
