import sqlite3
import os

DB_PATH = os.environ.get('CITIES_DB', 'cities.db')

# Condizione riutilizzabile: solo centri abitati riconosciuti da GeoNames.
# I punti di interesse (musei, fiumi, cime, ecc.) hanno is_populated_place=0
# e compaiono solo nella loro pagina diretta, non in elenchi o statistiche.
_IS_CITY = 'is_populated_place = 1'


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ── Continenti ────────────────────────────────────────────────────

def get_continents():
    with get_conn() as conn:
        return conn.execute(f'''
            SELECT continent,
                   COUNT(*)                  AS city_count,
                   COUNT(DISTINCT countrycode) AS country_count
            FROM   cities
            WHERE  continent != '' AND cityname != ''
              AND  {_IS_CITY}
            GROUP  BY continent
            ORDER  BY continent
        ''').fetchall()


# ── Paesi ─────────────────────────────────────────────────────────

def get_countries_by_continent(continent):
    with get_conn() as conn:
        return conn.execute(f'''
            SELECT countryname, countrycode, slug_country, continent,
                   COUNT(*)                  AS city_count,
                   COUNT(DISTINCT regionid)  AS region_count
            FROM   cities
            WHERE  continent = ? AND cityname != ''
              AND  {_IS_CITY}
            GROUP  BY countrycode
            ORDER  BY countryname
        ''', (continent,)).fetchall()


def get_country(country_slug):
    with get_conn() as conn:
        return conn.execute('''
            SELECT countryname, countrycode, continent, slug_country
            FROM   cities
            WHERE  slug_country = ?
            LIMIT  1
        ''', (country_slug,)).fetchone()


def get_all_countries():
    with get_conn() as conn:
        return conn.execute(f'''
            SELECT DISTINCT countryname, countrycode, slug_country, continent
            FROM   cities
            WHERE  countryname != '' AND {_IS_CITY}
            ORDER  BY countryname
        ''').fetchall()


# ── Regioni ───────────────────────────────────────────────────────

def get_regions_by_country(country_slug):
    with get_conn() as conn:
        return conn.execute(f'''
            SELECT stateprovince, slug_region,
                   COUNT(*) AS city_count
            FROM   cities
            WHERE  slug_country = ? AND stateprovince != '' AND cityname != ''
              AND  {_IS_CITY}
            GROUP  BY slug_region
            ORDER  BY stateprovince
        ''', (country_slug,)).fetchall()


def get_region(country_slug, region_slug):
    with get_conn() as conn:
        return conn.execute('''
            SELECT stateprovince, slug_region, countryname, slug_country, continent
            FROM   cities
            WHERE  slug_country = ? AND slug_region = ?
            LIMIT  1
        ''', (country_slug, region_slug)).fetchone()


# ── Città ─────────────────────────────────────────────────────────

def get_cities_by_region(country_slug, region_slug, page=1, per_page=50):
    offset = (page - 1) * per_page
    with get_conn() as conn:
        cities = conn.execute(f'''
            SELECT cityid, cityname, slug_city, latitude, longitude
            FROM   cities
            WHERE  slug_country = ? AND slug_region = ? AND cityname != ''
              AND  {_IS_CITY}
            ORDER  BY cityname
            LIMIT  ? OFFSET ?
        ''', (country_slug, region_slug, per_page, offset)).fetchall()

        total = conn.execute(f'''
            SELECT COUNT(*)
            FROM   cities
            WHERE  slug_country = ? AND slug_region = ? AND cityname != ''
              AND  {_IS_CITY}
        ''', (country_slug, region_slug)).fetchone()[0]

    return cities, total


def get_city(country_slug, region_slug, city_slug):
    # Nessun filtro is_populated_place: la pagina di un POI rimane
    # accessibile (mostra quota ma non popolazione).
    with get_conn() as conn:
        return conn.execute('''
            SELECT cityid, cityname, stateprovince, countryname, countrycode,
                   continent, latitude, longitude,
                   slug_city, slug_country, slug_region,
                   population, elevation_m, is_populated_place
            FROM   cities
            WHERE  slug_country = ? AND slug_region = ? AND slug_city = ?
            LIMIT  1
        ''', (country_slug, region_slug, city_slug)).fetchone()


def get_nearby_cities(lat, lon, current_cityid, limit=12, radius_deg=2.0):
    """Città vicine usando bounding box + distanza euclidea approssimata."""
    with get_conn() as conn:
        return conn.execute(f'''
            SELECT cityid, cityname, stateprovince, countryname,
                   slug_city, slug_country, slug_region,
                   latitude, longitude,
                   ((latitude  - ?) * (latitude  - ?) +
                    (longitude - ?) * (longitude - ?)) AS dist_sq
            FROM   cities
            WHERE  latitude  BETWEEN ? AND ?
              AND  longitude BETWEEN ? AND ?
              AND  cityname  != ''
              AND  latitude  IS NOT NULL
              AND  longitude IS NOT NULL
              AND  cityid    != ?
              AND  {_IS_CITY}
            ORDER  BY dist_sq
            LIMIT  ?
        ''', (
            lat, lat, lon, lon,
            lat - radius_deg, lat + radius_deg,
            lon - radius_deg, lon + radius_deg,
            current_cityid,
            limit
        )).fetchall()


# ── Sitemap ───────────────────────────────────────────────────────

SITEMAP_CHUNK = 50_000


def get_cities_for_sitemap(offset, limit=SITEMAP_CHUNK):
    with get_conn() as conn:
        return conn.execute(f'''
            SELECT slug_city, slug_country, slug_region
            FROM   cities
            WHERE  cityname != '' AND slug_city != ''
              AND  slug_country != '' AND slug_region != ''
              AND  {_IS_CITY}
            LIMIT  ? OFFSET ?
        ''', (limit, offset)).fetchall()


def get_total_cities_with_slug():
    with get_conn() as conn:
        return conn.execute(f'''
            SELECT COUNT(*) FROM cities
            WHERE cityname != '' AND slug_city != ''
              AND slug_country != '' AND slug_region != ''
              AND {_IS_CITY}
        ''').fetchone()[0]


def get_city_count():
    with get_conn() as conn:
        return conn.execute(
            f"SELECT COUNT(*) FROM cities WHERE cityname != '' AND {_IS_CITY}"
        ).fetchone()[0]


def get_region_city_count(country_slug, region_slug):
    """Numero di città e POI in una regione specifica."""
    with get_conn() as conn:
        row = conn.execute(
            f"""SELECT
                    SUM(CASE WHEN {_IS_CITY} THEN 1 ELSE 0 END) AS cities,
                    SUM(CASE WHEN is_populated_place = 0 THEN 1 ELSE 0 END) AS pois
                FROM cities
                WHERE slug_country = ? AND slug_region = ? AND cityname != ''""",
            (country_slug, region_slug)
        ).fetchone()
        return int(row['cities'] or 0), int(row['pois'] or 0)


def get_country_city_count(country_slug):
    """Numero totale di città e POI in un paese."""
    with get_conn() as conn:
        row = conn.execute(
            f"""SELECT
                    SUM(CASE WHEN {_IS_CITY} THEN 1 ELSE 0 END) AS cities,
                    SUM(CASE WHEN is_populated_place = 0 THEN 1 ELSE 0 END) AS pois
                FROM cities
                WHERE slug_country = ? AND cityname != ''""",
            (country_slug,)
        ).fetchone()
        return int(row['cities'] or 0), int(row['pois'] or 0)


def search_cities(query, limit=30):
    """Ricerca città per nome (parziale, case-insensitive)."""
    with get_conn() as conn:
        return conn.execute(f'''
            SELECT cityname, stateprovince, countryname, countrycode,
                   slug_city, slug_country, slug_region
            FROM   cities
            WHERE  cityname LIKE ? AND cityname != ''
              AND  slug_city != '' AND slug_country != '' AND slug_region != ''
              AND  {_IS_CITY}
            ORDER  BY cityname
            LIMIT  ?
        ''', (f'%{query}%', limit)).fetchall()
