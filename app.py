import math
import os
from bottle import Bottle, run, template, static_file, request, response, abort, HTTPError

import db
import utils

app = Bottle()

BASE_URL = os.environ.get('BASE_URL', 'https://example.com').rstrip('/')


# ── Asset statici ─────────────────────────────────────────────────

@app.route('/static/<filepath:path>')
def static(filepath):
    return static_file(filepath, root='./static')


# ── robots.txt ────────────────────────────────────────────────────

@app.route('/robots.txt')
def robots():
    response.content_type = 'text/plain'
    return f"User-agent: *\nAllow: /\nSitemap: {BASE_URL}/sitemap.xml\n"


# ── Sitemap index ─────────────────────────────────────────────────

@app.route('/sitemap.xml')
def sitemap_index():
    response.content_type = 'application/xml; charset=utf-8'
    total = db.get_total_cities_with_slug()
    num_chunks = math.ceil(total / db.SITEMAP_CHUNK)
    return template('sitemap_index',
                    base_url=BASE_URL,
                    num_chunks=num_chunks)


@app.route('/sitemap-countries.xml')
def sitemap_countries():
    response.content_type = 'application/xml; charset=utf-8'
    countries = db.get_all_countries()
    return template('sitemap_countries',
                    base_url=BASE_URL,
                    countries=countries)


@app.route('/sitemap-cities-<n:int>.xml')
def sitemap_cities(n):
    total = db.get_total_cities_with_slug()
    num_chunks = math.ceil(total / db.SITEMAP_CHUNK)
    if n < 1 or n > num_chunks:
        abort(404)
    response.content_type = 'application/xml; charset=utf-8'
    offset = (n - 1) * db.SITEMAP_CHUNK
    cities = db.get_cities_for_sitemap(offset)
    return template('sitemap_cities',
                    base_url=BASE_URL,
                    cities=cities)


# ── Homepage ──────────────────────────────────────────────────────

@app.route('/')
def index():
    continents = db.get_continents()
    return template('index',
                    continents=continents,
                    base_url=BASE_URL,
                    title='World Cities Directory – Explore Cities by Country and Region',
                    description='Browse our complete world cities directory. '
                                'Find coordinates, maps, and nearby cities for every location on Earth.')


# ── Continente ────────────────────────────────────────────────────

@app.route('/continent/<cslug>/')
def continent(cslug):
    # Ricostruisce il nome del continente dallo slug
    continent_name = cslug.replace('-', ' ').title()
    countries = db.get_countries_by_continent(continent_name)
    if not countries:
        abort(404)
    return template('continent',
                    continent=continent_name,
                    continent_slug=cslug,
                    countries=countries,
                    base_url=BASE_URL,
                    title=f'Cities in {continent_name} – Country List',
                    description=f'Explore all countries and cities in {continent_name}. '
                                f'Find geographic coordinates and local information.')


# ── Paese ─────────────────────────────────────────────────────────

@app.route('/country/<cslug>/')
def country(cslug):
    country_row = db.get_country(cslug)
    if not country_row:
        abort(404)
    regions = db.get_regions_by_country(cslug)
    return template('country',
                    country=country_row,
                    regions=regions,
                    base_url=BASE_URL,
                    title=f'Cities in {country_row["countryname"]} – Regions and Provinces',
                    description=f'Complete list of regions and cities in {country_row["countryname"]}. '
                                f'Find coordinates, maps and nearby places for every city.')


# ── Regione ───────────────────────────────────────────────────────

@app.route('/country/<cslug>/<rslug>/')
def region(cslug, rslug):
    region_row = db.get_region(cslug, rslug)
    if not region_row:
        abort(404)
    page = max(1, int(request.query.get('page', 1)))
    cities, total = db.get_cities_by_region(cslug, rslug, page=page)
    pag = utils.paginate(total, page, per_page=50)
    region_name = region_row['stateprovince']
    country_name = region_row['countryname']
    return template('region',
                    region=region_row,
                    cities=cities,
                    pag=pag,
                    base_url=BASE_URL,
                    title=f'Cities in {region_name}, {country_name} – Full List with Coordinates',
                    description=f'Browse all {total} cities in {region_name}, {country_name}. '
                                f'GPS coordinates, maps and nearby cities for each location.')


# ── Città ─────────────────────────────────────────────────────────

@app.route('/country/<cslug>/<rslug>/<cityslug>/')
def city(cslug, rslug, cityslug):
    city_row = db.get_city(cslug, rslug, cityslug)
    if not city_row:
        abort(404)

    nearby = []
    lat_dms = lon_dms = None
    if city_row['latitude'] and city_row['longitude']:
        lat_dms, lon_dms = utils.format_coords(city_row['latitude'], city_row['longitude'])
        nearby_raw = db.get_nearby_cities(
            city_row['latitude'],
            city_row['longitude'],
            city_row['cityid']
        )
        # Calcola distanza reale Haversine per ciascuna città vicina
        nearby = []
        for n in nearby_raw:
            if n['latitude'] and n['longitude']:
                dist = utils.haversine(
                    city_row['latitude'], city_row['longitude'],
                    n['latitude'], n['longitude']
                )
                nearby.append(dict(n) | {'distance_km': dist})

    city_name    = city_row['cityname']
    region_name  = city_row['stateprovince']
    country_name = city_row['countryname']

    return template('city',
                    city=city_row,
                    nearby=nearby,
                    lat_dms=lat_dms,
                    lon_dms=lon_dms,
                    base_url=BASE_URL,
                    title=f'{city_name}, {region_name}, {country_name} – '
                          f'Coordinates, Map & Nearby Cities',
                    description=f'{city_name} is a city in {region_name}, {country_name}. '
                                f'Latitude {city_row["latitude"]}, longitude {city_row["longitude"]}. '
                                f'Find map, GPS coordinates and nearby cities.')


# ── Avvio ─────────────────────────────────────────────────────────

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    debug = os.environ.get('DEBUG', 'false').lower() == 'true'
    run(app, host='0.0.0.0', port=port, debug=debug, reloader=debug)
