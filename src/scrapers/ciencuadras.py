import time
import random
import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException


DEFAULT_HEADERS = {
    "user-agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


class CiencuadrasScraper:
    BASE = "https://www.ciencuadras.com"

    def __init__(self, cities, max_pages=20, sleep_range=(1.0, 2.5), headers=None):
        """
        cities: lista de slugs de ciudad, ej: ["medellin", "bogota", "envigado"]
        """
        self.cities = cities
        self.max_pages = max_pages
        self.sleep_range = sleep_range
        self.headers = headers or DEFAULT_HEADERS

    # ----------------- Helpers -----------------
    @staticmethod
    def format_elapsed(start_ts: float) -> str:
        elapsed = int(time.time() - start_ts)
        mins = elapsed // 60
        secs = elapsed % 60
        return f"{mins:02d}:{secs:02d}"

    def build_list_url(self, city_slug: str, page: int) -> str:
        """
        /arriendo/{city} para página 1
        /arriendo/{city}?page=N para el resto (paginación típica)
        """
        base = f"{self.BASE}/arriendo/{city_slug}"
        if page <= 1:
            return base
        return f"{base}?page={page}"

    def get_list_page(self, city_slug: str, page: int):
        url = self.build_list_url(city_slug, page)

        try:
            resp = requests.get(url, headers=self.headers, timeout=60)
            resp.raise_for_status()
        except RequestException as e:
            print(f"[WARN] Error listando {city_slug}, página {page}: {e}")
            return []

        soup = BeautifulSoup(resp.text, "html.parser")

        urls = []
        for a in soup.select("a[href^='/inmueble/']"):
            href = a.get("href")
            if not href:
                continue
            if href.startswith("http"):
                urls.append(href)
            else:
                urls.append(self.BASE + href)

        return list(set(urls))  # quitar duplicados en la página

    def parse_detail(self, url: str) -> dict:
        try:
            resp = requests.get(url, headers=self.headers, timeout=60)
            resp.raise_for_status()
        except RequestException as e:
            print(f"[WARN] Error detalle {url}: {e}")
            return {}

        soup = BeautifulSoup(resp.text, "html.parser")
        data = {"url": url}

        # Título y ubicación
        h1 = soup.find("h1")
        if h1:
            data["titulo"] = h1.get_text(strip=True)

        h2 = soup.find("h2")
        if h2:
            data["ubicacion"] = h2.get_text(strip=True)

        # Mapeo de labels -> nombres de campos
        label_map = {
            "Arriendo sin administración": "precio_arriendo_sin_admin",
            "Valor de arriendo": "precio_arriendo",
            "Área privada": "area_privada",
            "Área construida": "area_construida",
            "Habitaciones": "habitaciones",
            "Baños": "banos",
            "Parqueaderos": "parqueaderos",
            "Estrato": "estrato",
        }

        for label, field_name in label_map.items():
            el = soup.find(string=lambda s: s and label in s)
            if not el:
                continue
            parent = el.find_parent()
            sibling = parent.find_next_sibling() if parent else None

            if sibling:
                value = sibling.get_text(" ", strip=True)
            elif parent:
                value = parent.get_text(" ", strip=True)
            else:
                value = el.strip()

            data[field_name] = value

        return data

    # ----------------- Por ciudad -----------------
    def scrape_city(self, city_slug: str):
        seen = set()
        items = []
        start_ts = time.time()

        print(f"[CIUDAD] {city_slug}")

        for page in range(1, self.max_pages + 1):
            print(f"[{city_slug:<10}] LISTADO página {page}")
            urls = self.get_list_page(city_slug, page)
            if not urls:
                print(f"[{city_slug:<10}] [STOP] página {page} sin resultados.")
                break

            new_urls = [u for u in urls if u not in seen]
            if not new_urls:
                print(f"[{city_slug:<10}] [STOP] sin URLs nuevas en página {page}.")
                break

            for url in new_urls:
                seen.add(url)
                item = self.parse_detail(url)
                if item:
                    items.append(item)

                time.sleep(random.uniform(*self.sleep_range))

            msg = (
                f"[{city_slug:<10}] páginas: {page:3d}  "
                f"props únicas: {len(items):4d}  "
                f"tiempo: {self.format_elapsed(start_ts)}"
            )
            print(msg)

        return items

    # ----------------- Run completo -----------------
    def run(self):
        totals = {}
        all_data = {}

        print("== Ciencuadras Scraper ==")
        print(f"Ciudades: {', '.join(self.cities)}\n")

        for city in self.cities:
            city_items = self.scrape_city(city)
            totals[city] = len(city_items)
            all_data[city] = city_items

        print("\n== RESUMEN CIENCUADRAS ==")
        for city, n in totals.items():
            print(f"{city:<10}: {n} registros")

        return all_data
