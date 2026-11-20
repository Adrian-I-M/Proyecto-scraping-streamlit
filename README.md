# Práctica Web Scraping y Streamlit - Books to Scrape

Proyecto de extracción de datos de libros con **BeautifulSoup** y **Pandas**, y visualización mediante un dashboard interactivo en **Streamlit**.

## Estructura del repositorio
- `scraper.py`: script que extrae los libros por género, limpia los precios y valoraciones, y genera el CSV.
- `data/datos_limpios.csv`: dataset generado con 205 libros de 12 categorías.
- `app.py`: aplicación web en Streamlit con filtros por género, precio y estrellas, gráficos y tabla de resultados.
- `requirements.txt`: librerías necesarias para ejecutar el proyecto.

## Buenas prácticas aplicadas
- Se comprobó `https://books.toscrape.com/robots.txt` antes de extraer datos (devuelve `404 Not Found`, sin restricciones, y es una web pública pensada para practicar scraping).
- Se incluye cabecera `User-Agent` en las peticiones y pausas de 1 segundo (`time.sleep(1)`) entre páginas para no saturar el servidor.

## Cómo ejecutarlo
1. Instalar dependencias:
   ```bash
   pip install -r requirements.txt