import json
import time
import random
from datetime import datetime

import requests
from requests.exceptions import RequestException


# -------------------------------------------------------------------
# IMPORTANTE:
# Reemplaza el contenido de DEFAULT_HEADERS con los HEADERS largos
# que ya tenías en tu script original de Metrocuadrado.
# -------------------------------------------------------------------
DEFAULT_HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "max-age=0",
    "cookie": "MRID=445673846.1763759213; utag_main__sn=1; utag_main_ses_id=1763759210597%3Bexp-session; split_segmentation=FAB; split_segmentation_50=FAB_SUS_50; utag_main_vapi_domain=metrocuadrado.com; at_check=true; utag_main__ss=0%3Bexp-session; utag_main_v_id=019aa83dc7cc0026cac6658f785c0506f00f106700bd0; utag_main_dc_visit=1; utag_main_dc_region=us-east-1%3Bexp-session; _fbp=fb.1.1763759212850.422108589807941523; _hjSession_3298791=eyJpZCI6IjQzMWFiMTFmLTliZDUtNDNhYy1hNGVlLTFiNmM1NDcwN2RiZiIsImMiOjE3NjM3NTkyMTI5MDQsInMiOjAsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjoxLCJzcCI6MX0=; _gcl_gs=2.1.k1$i1763759209$u191886646; _ga=GA1.1.445673846.1763759213; _gcl_au=1.1.1664729431.1763759213; canary_param=false; lastSearch=%2Fapartamento%2Farriendo%2Fmedellin%2F%3Fsearch%3Dsave%26from%3D0%26seo%3D%2Fapartamentos%2Farriendo%2Fmedellin%2F; project=detail; _hjSessionUser_3298791=eyJpZCI6IjgwMDk0NDIwLTdkZGQtNTViMC1hYzRkLWU1ZGE0ZTQxZGM4NSIsImNyZWF0ZWQiOjE3NjM3NTkyMTI5MDQsImV4aXN0aW5nIjp0cnVlfQ==; cd_value=9500000; disclaimerCookies=true; _gcl_aw=GCL.1763760206.CjwKCAiAuIDJBhBoEiwAxhgyFhDevhdqdbzHl2tgytWuJyCXsB5uF-2n8y2WbgFNKuFLsDapt71gshoC-5YQAvD_BwE; userLatitude=6.1338929; userLongitude=-75.6364308; utag_main__pn=10%3Bexp-session; utag_main_dc_event=9%3Bexp-session; cto_bundle=bBwZ1F9BaXhqczhCJTJGZ2d5WUI3M0hmb1NFNEclMkZ5MUs5MmElMkZPVHFDcFVPUGZNek01T0JlR1d0aVdEUmJiMFMybVlVQnB4RUFJU2k3UkZBTUM1OWttJTJCMnBabTlzSmZLT3JSbld5WFRKbFJXVUY0UmxranBFb1g5ZCUyQkpXZWdXYmc4TlYxaXI2ejhuYW0lMkJ6bzlNdEYlMkJOa2FsbGZWdVl3S1BxUjd1cUFBS1JlNzFXTm1qRSUzRA; utag_main__se=129%3Bexp-session; utag_main__st=1763762714319%3Bexp-session; _ga_02LQXVPQF9=GS2.1.s1763759212$o1$g1$t1763760914$j59$l0$h0; mbox=session#57e7c20952884ea4b091455c4c999c04#1763762775|PC#57e7c20952884ea4b091455c4c999c04.34_0#1827005715; AWSALB=tbst58AdwdTGKS/IxqR+H0oA+QHqCYw3kScje78hJzQjo8qQ6Tj077iXdAFsUxZ0wcvXIk/PQXBaTV6AZyG27WSYJuajuFVPsbr5Lvs2b+9KIBB52/68tqG/dfy+TSKdODo1T4FsPGIGZjtHKEAWquuo7Oep5V6SrocbOwEbsi3/wQcKZB7BpZJL+St73g==",
    "priority": "u=0, i",
    "sec-ch-ua": '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
}

class MetrocuadradoScraper:
    BASE_DOMAIN = "https://www.metrocuadrado.com"

    def __init__(self, cities, max_pages=100, sleep_range=(1.0, 2.5), headers=None):
        self.cities = cities
        self.max_pages = max_pages
        self.sleep_range = sleep_range
        self.headers = headers or DEFAULT_HEADERS

    # ----------------- Helpers -----------------
    @staticmethod
    def fix_text(s):
        if not isinstance(s, str):
            return s
        if "Ã" not in s and "Â" not in s:
            return s
        try:
            return s.encode("latin1").decode("utf-8")
        except Exception:
            return s

    @staticmethod
    def extract_json_objects(text: str):
        key = "contactPhone"
        objs = []
        n = len(text)
        pos = 0

        while True:
            idx = text.find(key, pos)
            if idx == -1:
                break

            start = text.rfind("{", 0, idx)
            if start == -1:
                pos = idx + len(key)
                continue

            brace = 0
            j = start
            started = False
            while j < n:
                c = text[j]
                if c == "{":
                    brace += 1
                    started = True
                elif c == "}":
                    brace -= 1
                    if started and brace == 0:
                        j += 1
                        break
                j += 1

            raw = text[start:j]
            objs.append(raw)
            pos = idx + len(key)

        return objs

    def build_urls(self, city_slug):
        seo_path = f"/apartamentos/arriendo/{city_slug}/"
        base_seo_url = self.BASE_DOMAIN + seo_path
        base_search_url = f"{self.BASE_DOMAIN}/apartamento/arriendo/{city_slug}/"
        return base_seo_url, base_search_url, seo_path

    @staticmethod
    def format_elapsed(start_ts: float) -> str:
        elapsed = int(time.time() - start_ts)
        mins = elapsed // 60
        secs = elapsed % 60
        return f"{mins:02d}:{secs:02d}"

    # ----------------- Scraping -----------------
    def scrape_page(self, city_slug: str, offset: int):
        base_seo_url, base_search_url, seo_path = self.build_urls(city_slug)

        if offset == 0:
            url = base_seo_url
        else:
            url = f"{base_search_url}?search=save&from={offset}&seo={seo_path}"

        try:
            resp = requests.get(url, headers=self.headers, timeout=60)
            resp.raise_for_status()
            html = resp.text
        except RequestException as e:
            print(f"\n[WARN] Error en {city_slug}, offset {offset}: {e}")
            return []

        raw_objs = self.extract_json_objects(html)

        inmuebles = []
        for raw in raw_objs:
            try:
                raw_clean = raw.encode("utf-8").decode("unicode_escape")
                data = json.loads(raw_clean)
            except Exception:
                continue

            inmuebles.append({
                "id": data.get("midinmueble"),
                "titulo": self.fix_text(data.get("title")),
                "link": self.BASE_DOMAIN + (data.get("link") or ""),
                "precio": data.get("mvalorarriendo"),
                "area": data.get("marea"),
                "cuartos": data.get("mnrocuartos"),
                "banos": data.get("mnrobanos"),
                "barrio": self.fix_text(data.get("mnombrecomunbarrio") or data.get("mbarrio")),
                "telefono": data.get("contactPhone"),
            })

        return inmuebles

    def scrape_city(self, city_slug: str):
        seen_ids = set()
        all_items = []
        pages = 0
        start_ts = time.time()

        print(f"[CIUDAD] {city_slug}")

        while pages < self.max_pages:
            offset = len(seen_ids)
            results = self.scrape_page(city_slug, offset)

            if not results:
                break

            nuevos = []
            for item in results:
                mid = item.get("id")
                if not mid or mid in seen_ids:
                    continue
                seen_ids.add(mid)
                nuevos.append(item)

            all_items.extend(nuevos)
            pages += 1

            msg = (
                f"[{city_slug:<9}] páginas: {pages:3d}  "
                f"props únicas: {len(all_items):4d}  "
                f"tiempo: {self.format_elapsed(start_ts)}"
            )
            print("\r" + msg, end="", flush=True)

            if not nuevos:
                break

            time.sleep(random.uniform(*self.sleep_range))

        print()
        return all_items

    # ----------------- Run completo -----------------
    def run(self):
        totals = {}
        global_start = time.time()

        print("== Metrocuadrado Scraper ==")
        print(f"Fecha: {datetime.today().strftime('%Y-%m-%d')}")
        print(f"Ciudades: {', '.join(self.cities)}")
        print()

        for city in self.cities:
            items = self.scrape_city(city)
            totals[city] = len(items)

        elapsed = self.format_elapsed(global_start)

        print("\n== RESUMEN ==")
        for city, count in totals.items():
            print(f"{city:<10}: {count} registros")
        print(f"Tiempo total: {elapsed}")

        return totals
