import os
import json
from datetime import datetime

from src.scrapers.metrocuadrado import MetrocuadradoScraper
from src.scrapers.ciencuadras import CiencuadrasScraper


# -----------------------------
# Helpers para guardar JSON
# -----------------------------
def save_json(data, source, city):
    """Guarda un archivo JSON para una fuente y ciudad."""
    date = datetime.today().strftime("%Y-%m-%d")

    base_dir = f"data/raw/{date}/{source}"
    os.makedirs(base_dir, exist_ok=True)

    path = f"{base_dir}/{city}.json"

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[SAVE] {path}")


# -----------------------------
# Pipeline principal
# -----------------------------
def main():
    # ---------------------------------------
    # METROCUADRADO
    # ---------------------------------------
    cities_metro = ["medellin", "sabaneta", "itagui", "envigado", "bello"]

    print("\n=== EJECUTANDO METROCUADRADO ===")
    m_scraper = MetrocuadradoScraper(
        cities=cities_metro,
        max_pages=100,
        sleep_range=(1.0, 2.5),
    )
    metro_data = m_scraper.run()

    # Guardar cada ciudad
    for city in metro_data:
        save_json(metro_data[city], "metrocuadrado", city)

    # ---------------------------------------
    # CIENCUADRAS
    # ---------------------------------------
    print("\n=== EJECUTANDO CIENCUADRAS ===")
    c_scraper = CiencuadrasScraper(
        cities=["medellin", "bogota", "cali", "envigado", "sabaneta", "bello"],
        max_pages=50,
        sleep_range=(1.0, 2.0),
    )
    cien_data = c_scraper.run()

    # Guardar cada ciudad
    for city in cien_data:
        save_json(cien_data[city], "ciencuadras", city)


if __name__ == "__main__":
    main()
