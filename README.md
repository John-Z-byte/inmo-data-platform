🧭 Visión rápida del sistema

Este proyecto es una plataforma de datos inmobiliarios. Empieza con Metrocuadrado (Valle de Aburrá) y está diseñada para escalar a más portales, ciudades y capas de datos (bronze → gold), además de analítica y modelos de precios.

⚙️ Cómo funciona el scraping

Las páginas modernas (Next.js / React SSR) no entregan HTML con tarjetas. Entregan un <script> con JSON escapado. El scraper:

Simula un navegador real (headers, cookies, user-agent).

Detecta el <script> donde Metrocuadrado incrusta los datos.

Extrae y reconstruye los objetos JSON.

Deduplica por midinmueble.

Pagina usando ?search=save&from=OFFSET&seo=....

🧱 Arquitectura del proyecto
src/
  scrapers/       # lógica de scraping
  pipelines/      # orquestación de corridas
  db/             # modelo futuro de tablas
  ml/             # espacio para EDA y modelos
  utils/          # utilidades comunes
data/             # raw, logs y dumps (futuro)


Todo está organizado para crecer sin perder orden: más fuentes, más ciudades, más capas.

🚀 Ejecutar
python -m src.pipelines.ingest_raw