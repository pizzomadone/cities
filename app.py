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

    lat = city_row['latitude']
    lon = city_row['longitude']
    has_coords = bool(lat and lon)

    nearby = []
    lat_dms = lon_dms = None

    # ── Dati geo estesi ────────────────────────────────────────────
    geo = {
        'flag':         utils.country_flag(city_row['countrycode']),
        'tld':          utils.get_tld(city_row['countrycode']),
        'phone_prefix': utils.get_phone_prefix(city_row['countrycode']),
        'tz_offset':    None,
        'tz_label':     None,
        'hemisphere_ns': None,
        'hemisphere_ew': None,
        'equator_km':   None,
        'anti_lat':     None,
        'anti_lon':     None,
        'anti_lat_dms': None,
        'anti_lon_dms': None,
        'sunrise':      None,
        'sunset':       None,
        'day_length':   None,
        'sun_date':     None,
    }

    if has_coords:
        lat_dms, lon_dms = utils.format_coords(lat, lon)

        geo['tz_offset'], geo['tz_label'] = utils.approx_timezone(lon)
        geo['hemisphere_ns'], geo['hemisphere_ew'] = utils.get_hemisphere(lat, lon)
        geo['equator_km'] = utils.distance_from_equator(lat)

        anti_lat, anti_lon = utils.antipode(lat, lon)
        geo['anti_lat'] = anti_lat
        geo['anti_lon'] = anti_lon
        geo['anti_lat_dms'], geo['anti_lon_dms'] = utils.format_coords(anti_lat, anti_lon)

        geo['sunrise'], geo['sunset'], geo['day_length'], geo['sun_date'] = \
            utils.sunrise_sunset(lat, lon)

        nearby_raw = db.get_nearby_cities(lat, lon, city_row['cityid'])
        for n in nearby_raw:
            if n['latitude'] and n['longitude']:
                dist = utils.haversine(lat, lon, n['latitude'], n['longitude'])
                nearby.append(dict(n) | {'distance_km': dist})

    # ── Statistiche regionali ──────────────────────────────────────
    region_city_count  = db.get_region_city_count(cslug, rslug)
    country_city_count = db.get_country_city_count(cslug)

    city_name    = city_row['cityname']
    region_name  = city_row['stateprovince']
    country_name = city_row['countryname']
    code         = city_row['countrycode']

    return template('city',
                    city=city_row,
                    nearby=nearby,
                    lat_dms=lat_dms,
                    lon_dms=lon_dms,
                    geo=geo,
                    region_city_count=region_city_count,
                    country_city_count=country_city_count,
                    base_url=BASE_URL,
                    title=f'{city_name}, {region_name}, {country_name} – '
                          f'GPS Coordinates, Map, Time Zone & Nearby Cities',
                    description=f'{city_name} is a city in {region_name}, {country_name} ({code}). '
                                f'GPS coordinates: latitude {lat}, longitude {lon}. '
                                f'Discover the time zone, sunrise & sunset times, antipode, '
                                f'hemisphere, and nearby cities.')


# ── Avvio ─────────────────────────────────────────────────────────

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    debug = os.environ.get('DEBUG', 'false').lower() == 'true'
    run(app, host='0.0.0.0', port=port, debug=debug, reloader=debug)
