import gzip
import io
import math
import os
from bottle import Bottle, run, template, static_file, request, response, abort, HTTPError

import db
import utils

app = Bottle()


# ── Gzip middleware ────────────────────────────────────────────────

_COMPRESSIBLE = ('text/', 'application/json', 'application/javascript',
                 'application/xml', 'image/svg')

class GzipMiddleware:
    """Comprime le risposte HTTP con gzip se il client le accetta."""

    def __init__(self, wsgi_app, min_size=512):
        self.app      = wsgi_app
        self.min_size = min_size

    def __call__(self, environ, start_response):
        if 'gzip' not in environ.get('HTTP_ACCEPT_ENCODING', ''):
            return self.app(environ, start_response)

        captured_status  = []
        captured_headers = []

        def fake_start(status, headers, exc_info=None):
            captured_status.append(status)
            captured_headers.append(list(headers))

        body = b''.join(self.app(environ, fake_start))

        status  = captured_status[0]
        headers = captured_headers[0]

        ctype = next((v for k, v in headers if k.lower() == 'content-type'), '')
        should_compress = (
            len(body) >= self.min_size
            and any(t in ctype for t in _COMPRESSIBLE)
        )

        if not should_compress:
            start_response(status, headers)
            return [body]

        buf = io.BytesIO()
        with gzip.GzipFile(fileobj=buf, mode='wb', compresslevel=6) as f:
            f.write(body)
        compressed = buf.getvalue()

        new_headers = [(k, v) for k, v in headers
                       if k.lower() not in ('content-length', 'content-encoding')]
        new_headers += [
            ('Content-Encoding', 'gzip'),
            ('Content-Length',   str(len(compressed))),
            ('Vary',             'Accept-Encoding'),
        ]
        start_response(status, new_headers)
        return [compressed]

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
                    noindex=(total < 3),
                    base_url=BASE_URL,
                    title=f'Cities in {region_name}, {country_name} – Full List with Coordinates',
                    description=f'Browse all {total} cities in {region_name}, {country_name}. '
                                f'GPS coordinates, maps and nearby cities for each location.')


# ── Ricerca ───────────────────────────────────────────────────────

@app.route('/search')
def search():
    q = request.query.get('q', '').strip()
    results = db.search_cities(q) if len(q) >= 2 else []
    if q:
        title = f'Search results for "{q}" – WorldCities'
        desc  = (f'Found {len(results)} cities matching "{q}". '
                 f'GPS coordinates and maps for each location.')
    else:
        title = 'Search Cities – WorldCities'
        desc  = 'Search the WorldCities directory for any city worldwide.'
    return template('search',
                    q=q,
                    results=results,
                    base_url=BASE_URL,
                    title=title,
                    description=desc)


# ── Città ─────────────────────────────────────────────────────────

def _city_base(cslug, rslug, cityslug):
    """Dati comuni a tutte le pagine di una città."""
    city_row = db.get_city(cslug, rslug, cityslug)
    if not city_row:
        return None

    lat = city_row['latitude']
    lon = city_row['longitude']
    has_coords = bool(lat and lon)

    geo = {
        'flag':          utils.country_flag(city_row['countrycode']),
        'tld':           utils.get_tld(city_row['countrycode']),
        'phone_prefix':  utils.get_phone_prefix(city_row['countrycode']),
        'tz_offset':     None,
        'tz_label':      None,
        'hemisphere_ns': None,
        'hemisphere_ew': None,
        'equator_km':    None,
        'anti_lat':      None,
        'anti_lon':      None,
        'anti_lat_dms':  None,
        'anti_lon_dms':  None,
        'sunrise':       None,
        'sunset':        None,
        'day_length':    None,
        'sun_date':      None,
    }
    lat_dms = lon_dms = None

    if has_coords:
        lat_dms, lon_dms = utils.format_coords(lat, lon)
        geo['tz_offset'], geo['tz_label'] = utils.lookup_timezone(city_row['countrycode'], lon)
        geo['hemisphere_ns'], geo['hemisphere_ew'] = utils.get_hemisphere(lat, lon)
        geo['equator_km'] = utils.distance_from_equator(lat)
        anti_lat, anti_lon = utils.antipode(lat, lon)
        geo['anti_lat'], geo['anti_lon'] = anti_lat, anti_lon
        geo['anti_lat_dms'], geo['anti_lon_dms'] = utils.format_coords(anti_lat, anti_lon)
        geo['sunrise'], geo['sunset'], geo['day_length'], geo['sun_date'] = \
            utils.sunrise_sunset(lat, lon)

    intro_paragraph = (
        utils.city_intro_paragraph(city_row, geo, lat_dms, lon_dms)
        if has_coords else None
    )

    return {
        'city': city_row,
        'lat': lat, 'lon': lon, 'has_coords': has_coords,
        'lat_dms': lat_dms, 'lon_dms': lon_dms,
        'geo': geo,
        'country_info': utils.get_country_info(city_row['countrycode']),
        'intro_paragraph': intro_paragraph,
        'noindex': not has_coords,
        'base_url': BASE_URL,
    }


@app.route('/country/<cslug>/<rslug>/<cityslug>/')
def city(cslug, rslug, cityslug):
    d = _city_base(cslug, rslug, cityslug)
    if d is None:
        abort(404)

    city_row = d['city']
    lat, lon, has_coords = d['lat'], d['lon'], d['has_coords']
    nearby = []
    moon   = None
    season = None

    if has_coords:
        nearby_raw = db.get_nearby_cities(lat, lon, city_row['cityid'])
        for n in nearby_raw:
            if n['latitude'] and n['longitude']:
                dist = utils.haversine(lat, lon, n['latitude'], n['longitude'])
                if dist > 0:
                    nearby.append(dict(n) | {'distance_km': dist})
        moon   = utils.moon_phase()
        season = utils.current_season(lat)

    region_city_count, region_poi_count   = db.get_region_city_count(cslug, rslug)
    country_city_count, country_poi_count = db.get_country_city_count(cslug)

    city_name, region_name, country_name = \
        city_row['cityname'], city_row['stateprovince'], city_row['countryname']

    return template('city',
                    **d,
                    nearby=nearby,
                    moon=moon,
                    season=season,
                    region_city_count=region_city_count,
                    region_poi_count=region_poi_count,
                    country_city_count=country_city_count,
                    country_poi_count=country_poi_count,
                    title=f'{city_name}, {region_name}, {country_name} – '
                          f'GPS Coordinates, Map, Time Zone & Info',
                    description=f'{city_name} is a city in {region_name}, {country_name}. '
                                f'GPS coordinates: latitude {lat}, longitude {lon}. '
                                f'Time zone, sunrise, moon phase, golden hour, daylight hours '
                                f'and nearby cities.')


@app.route('/country/<cslug>/<rslug>/<cityslug>/time/')
def city_time_page(cslug, rslug, cityslug):
    d = _city_base(cslug, rslug, cityslug)
    if d is None:
        abort(404)
    city_row = d['city']
    cn, co = city_row['cityname'], city_row['countryname']
    return template('city_time',
                    **d,
                    title=f'Current Time in {cn}, {co}',
                    description=f'What time is it in {cn}, {co}? Live clock, UTC offset, '
                                f'and local date and time for {cn}.')


@app.route('/country/<cslug>/<rslug>/<cityslug>/sunrise/')
def city_sunrise_page(cslug, rslug, cityslug):
    d = _city_base(cslug, rslug, cityslug)
    if d is None:
        abort(404)
    lat, lon, has_coords = d['lat'], d['lon'], d['has_coords']
    sun_calendar = utils.build_sun_calendar(lat, lon) if has_coords else []
    season       = utils.current_season(lat) if has_coords else None
    ann_daylight = utils.annual_daylight(lat, lon, d['geo']['tz_offset'] or 0) if has_coords else []
    city_row = d['city']
    cn, co = city_row['cityname'], city_row['countryname']
    return template('city_sunrise',
                    **d,
                    sun_calendar=sun_calendar,
                    season=season,
                    ann_daylight=ann_daylight,
                    title=f'Sunrise and Sunset in {cn}, {co} – Times & Calendar',
                    description=f'Sunrise and sunset times in {cn}, {co} today and for every '
                                f'day of the month. Daily daylight duration and annual chart.')


@app.route('/country/<cslug>/<rslug>/<cityslug>/moon/')
def city_moon_page(cslug, rslug, cityslug):
    d = _city_base(cslug, rslug, cityslug)
    if d is None:
        abort(404)
    moon          = utils.moon_phase()
    moon_calendar = utils.build_moon_calendar()
    city_row = d['city']
    cn, co = city_row['cityname'], city_row['countryname']
    return template('city_moon',
                    **d,
                    moon=moon,
                    moon_calendar=moon_calendar,
                    title=f'Moon Phase Today in {cn}, {co} – Lunar Calendar',
                    description=f'Current moon phase in {cn}, {co}: {moon["name"]} '
                                f'({moon["illumination"]}% illuminated). '
                                f'Monthly lunar calendar with full and new moon dates.')


@app.route('/country/<cslug>/<rslug>/<cityslug>/golden-hour/')
def city_golden_hour_page(cslug, rslug, cityslug):
    d = _city_base(cslug, rslug, cityslug)
    if d is None:
        abort(404)
    lat, lon, has_coords = d['lat'], d['lon'], d['has_coords']
    golden = utils.golden_hour(lat, lon) if has_coords else None
    city_row = d['city']
    cn, co = city_row['cityname'], city_row['countryname']
    return template('city_golden_hour',
                    **d,
                    golden=golden,
                    title=f'Golden Hour in {cn}, {co} – Photography Times Today',
                    description=f'Golden hour and blue hour times in {cn}, {co} today. '
                                f'Best photography light windows for sunrise and sunset.')


@app.route('/country/<cslug>/<rslug>/<cityslug>/daylight/')
def city_daylight_page(cslug, rslug, cityslug):
    d = _city_base(cslug, rslug, cityslug)
    if d is None:
        abort(404)
    lat, lon, has_coords = d['lat'], d['lon'], d['has_coords']
    ann_daylight = utils.annual_daylight(lat, lon, d['geo']['tz_offset'] or 0) if has_coords else []
    city_row = d['city']
    cn, co = city_row['cityname'], city_row['countryname']
    return template('city_daylight',
                    **d,
                    ann_daylight=ann_daylight,
                    title=f'Daylight Hours in {cn}, {co} – By Month & Season',
                    description=f'How many hours of daylight does {cn}, {co} get? '
                                f'Monthly daylight duration table and annual chart.')


@app.route('/country/<cslug>/<rslug>/<cityslug>/nearby/')
def city_nearby_page(cslug, rslug, cityslug):
    d = _city_base(cslug, rslug, cityslug)
    if d is None:
        abort(404)
    city_row = d['city']
    lat, lon, has_coords = d['lat'], d['lon'], d['has_coords']
    nearby = []
    if has_coords:
        nearby_raw = db.get_nearby_cities(lat, lon, city_row['cityid'])
        for n in nearby_raw:
            if n['latitude'] and n['longitude']:
                dist = utils.haversine(lat, lon, n['latitude'], n['longitude'])
                if dist > 0:
                    nearby.append(dict(n) | {'distance_km': dist})
    cn, co, rn = city_row['cityname'], city_row['countryname'], city_row['stateprovince']
    nearest = nearby[0]['cityname'] if nearby else None
    nearest_km = round(nearby[0]['distance_km']) if nearby else None
    return template('city_nearby',
                    **d,
                    nearby=nearby,
                    title=f'Cities near {cn}, {co} – Nearest Cities with Distances',
                    description=f'What cities are closest to {cn}, {co}? '
                                + (f'The nearest city is {nearest}, {nearest_km} km away. ' if nearest else '')
                                + f'Full list of cities near {cn} with distances.')


# ── WSGI app (con gzip) ───────────────────────────────────────────
# Usato da gunicorn/uwsgi: gunicorn "app:application"
application = GzipMiddleware(app)


# ── Avvio ─────────────────────────────────────────────────────────

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    debug = os.environ.get('DEBUG', 'false').lower() == 'true'
    run(application, host='0.0.0.0', port=port, debug=debug, reloader=debug)
