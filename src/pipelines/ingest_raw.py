from src.scrapers.metrocuadrado import MetrocuadradoScraper


def main():
    cities = ["medellin", "sabaneta", "itagui", "envigado", "bello"]

    scraper = MetrocuadradoScraper(
        cities=cities,
        max_pages=100,
        sleep_range=(1.0, 2.5),
    )

    scraper.run()


if __name__ == "__main__":
    main()
