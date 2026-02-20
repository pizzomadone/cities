% import json as _json, re as _re
% cslug_cont = _re.sub(r'[-\s]+', '-', city['continent'].lower().strip())
% has_coords = city['latitude'] and city['longitude']

% schema = {
%   "@context": "https://schema.org",
%   "@type": "City",
%   "name": city['cityname'],
%   "containedInPlace": {
%     "@type": "AdministrativeArea",
%     "name": city['stateprovince'],
%     "containedInPlace": {
%       "@type": "Country",
%       "name": city['countryname'],
%       "telephone": geo['phone_prefix'] or '',
%     }
%   }
% }
% if has_coords:
%   schema["geo"] = {
%     "@type": "GeoCoordinates",
%     "latitude": city['latitude'],
%     "longitude": city['longitude']
%   }
% end

% rebase('base',
%   title=title,
%   description=description,
%   canonical=base_url + '/country/' + city['slug_country'] + '/' + city['slug_region'] + '/' + city['slug_city'] + '/',
%   schema_json=_json.dumps(schema, ensure_ascii=False),
%   use_leaflet=has_coords,
%   breadcrumbs=[
%     {'label': city['continent'],      'url': '/continent/' + cslug_cont + '/'},
%     {'label': city['countryname'],    'url': '/country/' + city['slug_country'] + '/'},
%     {'label': city['stateprovince'],  'url': '/country/' + city['slug_country'] + '/' + city['slug_region'] + '/'},
%     {'label': city['cityname'],       'url': '/country/' + city['slug_country'] + '/' + city['slug_region'] + '/' + city['slug_city'] + '/'},
%   ]
% )

<article class="city-detail">

  <h1>
    % if geo['flag']:
    <span class="city-flag" aria-label="{{city['countryname']}} flag">{{geo['flag']}}</span>
    % end
    {{city['cityname']}}
    <span class="city-country-label">, {{city['countryname']}}</span>
  </h1>
  <p class="meta">
    <a href="/country/{{city['slug_country']}}/{{city['slug_region']}}/">{{city['stateprovince']}}</a> &rsaquo;
    <a href="/country/{{city['slug_country']}}/">{{city['countryname']}}</a> &rsaquo;
    <a href="/continent/{{cslug_cont}}/">{{city['continent']}}</a>
  </p>

  <!-- ── GPS Coordinates ─────────────────────────────────────── -->
  <section class="info-box" id="coordinates">
    <h2>GPS Coordinates of {{city['cityname']}}, {{city['countryname']}}</h2>
    % if has_coords:
    <p class="section-intro">
      The GPS coordinates of <strong>{{city['cityname']}}</strong> are
      latitude <strong>{{city['latitude']}}</strong> and longitude <strong>{{city['longitude']}}</strong>.
      In degrees, minutes, and seconds (DMS) format the coordinates are {{lat_dms}} latitude and {{lon_dms}} longitude.
    </p>
    <table class="coords-table">
      <tr>
        <th>Latitude</th>
        <td>{{city['latitude']}}</td>
        <td class="dms">{{lat_dms}}</td>
      </tr>
      <tr>
        <th>Longitude</th>
        <td>{{city['longitude']}}</td>
        <td class="dms">{{lon_dms}}</td>
      </tr>
      <tr>
        <th>Country Code</th>
        <td colspan="2">{{city['countrycode']}}</td>
      </tr>
      <tr>
        <th>Continent</th>
        <td colspan="2">{{city['continent']}}</td>
      </tr>
    </table>
    % else:
    <p>Coordinates not available for this location.</p>
    % end
  </section>

  <!-- ── Map ─────────────────────────────────────────────────── -->
  % if has_coords:
  <section class="map-section" id="map-section">
    <h2>Map of {{city['cityname']}}, {{city['stateprovince']}}</h2>
    <div id="map"></div>
    <script>
      var map = L.map('map').setView([{{city['latitude']}}, {{city['longitude']}}], 11);
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 18,
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      }).addTo(map);
      L.marker([{{city['latitude']}}, {{city['longitude']}}])
        .addTo(map)
        .bindPopup('<strong>{{city['cityname']}}</strong><br>{{city['stateprovince']}}, {{city['countryname']}}')
        .openPopup();
    </script>
  </section>
  % end

  <!-- ── Country Information ─────────────────────────────────── -->
  <section class="info-box" id="country-info">
    <h2>{{city['countryname']}} – Country Information</h2>
    <p class="section-intro">
      <strong>{{city['cityname']}}</strong> is located in
      <a href="/country/{{city['slug_country']}}/">{{city['countryname']}}</a>
      (ISO country code: <strong>{{city['countrycode']}}</strong>)
      % if geo['phone_prefix']:
      . The international dialing code for {{city['countryname']}} is <strong>{{geo['phone_prefix']}}</strong>
      % end
      % if geo['tld']:
      and the country's internet domain (ccTLD) is <strong>{{geo['tld']}}</strong>
      % end
      .
    </p>
    <table class="coords-table">
      % if geo['flag']:
      <tr>
        <th>Flag</th>
        <td colspan="2" class="flag-cell">
          <span class="flag-emoji">{{geo['flag']}}</span>
          {{city['countryname']}}
        </td>
      </tr>
      % end
      <tr>
        <th>Country Code</th>
        <td colspan="2">{{city['countrycode']}}</td>
      </tr>
      % if geo['phone_prefix']:
      <tr>
        <th>Dialing Code</th>
        <td colspan="2">{{geo['phone_prefix']}}</td>
      </tr>
      % end
      % if geo['tld']:
      <tr>
        <th>Internet TLD</th>
        <td colspan="2">{{geo['tld']}}</td>
      </tr>
      % end
      <tr>
        <th>Continent</th>
        <td colspan="2">
          <a href="/continent/{{cslug_cont}}/">{{city['continent']}}</a>
        </td>
      </tr>
      <tr>
        <th>Region / State</th>
        <td colspan="2">
          <a href="/country/{{city['slug_country']}}/{{city['slug_region']}}/">{{city['stateprovince']}}</a>
        </td>
      </tr>
      % if country_info:
      <tr>
        <th>Capital City</th>
        <td colspan="2">{{country_info['capital']}}</td>
      </tr>
      <tr>
        <th>Official Language</th>
        <td colspan="2">{{country_info['language']}}</td>
      </tr>
      <tr>
        <th>Currency</th>
        <td colspan="2">
          {{country_info['currency_name']}}
          ({{country_info['currency_code']}}
          % if country_info['currency_symbol'] != country_info['currency_code']:
          &nbsp;·&nbsp;<span class="currency-symbol">{{country_info['currency_symbol']}}</span>
          % end
          )
        </td>
      </tr>
      % end
    </table>
  </section>

  <!-- ── Time Zone ───────────────────────────────────────────── -->
  % if has_coords:
  <section class="info-box" id="timezone">
    <h2>Time Zone of {{city['cityname']}}, {{city['countryname']}}</h2>
    <p class="section-intro">
      Based on its longitude of <strong>{{city['longitude']}}</strong>,
      <strong>{{city['cityname']}}</strong> lies in the approximate solar time zone
      <strong>{{geo['tz_label']}}</strong>.
      Note that the legal (civil) time zone may differ due to national or regional boundaries.
    </p>
    <table class="coords-table">
      <tr>
        <th>Approximate UTC Offset</th>
        <td colspan="2">{{geo['tz_label']}}</td>
      </tr>
      <tr>
        <th>Based On Longitude</th>
        <td colspan="2">{{city['longitude']}}°</td>
      </tr>
    </table>
  </section>

  <!-- ── Explore ─────────────────────────────────────────────── -->
  % if has_coords:
  <section class="info-box" id="explore">
    <h2>Explore {{city['cityname']}}</h2>
    <p class="section-intro">Detailed information pages about {{city['cityname']}}.</p>
    % city_url = '/country/' + city['slug_country'] + '/' + city['slug_region'] + '/' + city['slug_city'] + '/'
    <div class="explore-grid">

      <a class="explore-card" href="{{city_url}}time/">
        <span class="explore-icon">🕐</span>
        <span class="explore-label">Current Time</span>
        % if geo['tz_label']:
        <span class="explore-value">{{geo['tz_label']}}</span>
        % end
      </a>

      <a class="explore-card" href="{{city_url}}sunrise/">
        <span class="explore-icon">🌅</span>
        <span class="explore-label">Sunrise &amp; Sunset</span>
        % if geo['sunrise']:
        <span class="explore-value">{{geo['sunrise']}} / {{geo['sunset']}}</span>
        % end
      </a>

      <a class="explore-card" href="{{city_url}}moon/">
        <span class="explore-icon">
          % if moon:
          {{moon['emoji']}}
          % else:
          🌙
          % end
        </span>
        <span class="explore-label">Moon Phase</span>
        % if moon:
        <span class="explore-value">{{moon['name']}} · {{moon['illumination']}}%</span>
        % end
      </a>

      <a class="explore-card" href="{{city_url}}golden-hour/">
        <span class="explore-icon">📸</span>
        <span class="explore-label">Golden Hour</span>
        % if geo['sunrise']:
        <span class="explore-value">{{geo['sunrise']}} &amp; {{geo['sunset']}}</span>
        % end
      </a>

      <a class="explore-card" href="{{city_url}}daylight/">
        <span class="explore-icon">☀️</span>
        <span class="explore-label">Daylight Hours</span>
        % if geo['day_length']:
        <span class="explore-value">{{geo['day_length']}} today</span>
        % end
      </a>

    </div>
  </section>
  % end


  <!-- ── Geographic Position ──────────────────────────────────── -->
  <section class="info-box" id="geographic-position">
    <h2>Geographic Position of {{city['cityname']}}</h2>
    <p class="section-intro">
      <strong>{{city['cityname']}}</strong> is located in the
      <strong>{{geo['hemisphere_ns']}} Hemisphere</strong> and the
      <strong>{{geo['hemisphere_ew']}} Hemisphere</strong>.
      It lies approximately <strong>{{geo['equator_km']}} km</strong>
      from the equator (based on its latitude of {{city['latitude']}}°).
    </p>
    <table class="coords-table">
      <tr>
        <th>Latitude Hemisphere</th>
        <td colspan="2">{{geo['hemisphere_ns']}} Hemisphere</td>
      </tr>
      <tr>
        <th>Longitude Hemisphere</th>
        <td colspan="2">{{geo['hemisphere_ew']}} Hemisphere</td>
      </tr>
      <tr>
        <th>Distance from Equator</th>
        <td colspan="2">≈ {{geo['equator_km']}} km</td>
      </tr>
      <tr>
        <th>Latitude (decimal)</th>
        <td colspan="2">{{city['latitude']}}° ({{lat_dms}})</td>
      </tr>
      <tr>
        <th>Longitude (decimal)</th>
        <td colspan="2">{{city['longitude']}}° ({{lon_dms}})</td>
      </tr>
    </table>
  </section>

  <!-- ── Antipode ─────────────────────────────────────────────── -->
  <section class="info-box" id="antipode">
    <h2>Antipode of {{city['cityname']}}</h2>
    <p class="section-intro">
      The <strong>antipode of {{city['cityname']}}</strong> — the point diametrically
      opposite on Earth — is located at latitude <strong>{{geo['anti_lat']}}</strong>
      ({{geo['anti_lat_dms']}}) and longitude <strong>{{geo['anti_lon']}}</strong>
      ({{geo['anti_lon_dms']}}). If you dug a tunnel straight through the center of
      the Earth from {{city['cityname']}}, you would come out at this location.
    </p>
    <table class="coords-table">
      <tr>
        <th>Antipode Latitude</th>
        <td colspan="2">{{geo['anti_lat']}}° ({{geo['anti_lat_dms']}})</td>
      </tr>
      <tr>
        <th>Antipode Longitude</th>
        <td colspan="2">{{geo['anti_lon']}}° ({{geo['anti_lon_dms']}})</td>
      </tr>
    </table>
    <p class="antipode-osm">
      <a href="https://www.openstreetmap.org/?mlat={{geo['anti_lat']}}&mlon={{geo['anti_lon']}}&zoom=5"
         rel="nofollow noopener" target="_blank">
        View antipode location on map
      </a>
    </p>
  </section>
  % end

  <!-- ── Regional Statistics ──────────────────────────────────── -->
  <section class="info-box" id="statistics">
    <h2>{{city['cityname']}} in Numbers – Cities in {{city['stateprovince']}} and {{city['countryname']}}</h2>
    <p class="section-intro">
      The <strong>{{city['stateprovince']}}</strong> region of
      <strong>{{city['countryname']}}</strong> contains
      <strong>{{region_city_count}}</strong>
      % if region_city_count == 1:
      city
      % else:
      cities
      % end
      in our database.
      <strong>{{city['countryname']}}</strong> as a whole has
      <strong>{{country_city_count}}</strong>
      % if country_city_count == 1:
      city
      % else:
      cities
      % end
      listed across all regions.
    </p>
    <table class="coords-table">
      <tr>
        <th>Cities in {{city['stateprovince']}}</th>
        <td colspan="2">
          <a href="/country/{{city['slug_country']}}/{{city['slug_region']}}/">
            {{region_city_count}} cities
          </a>
        </td>
      </tr>
      <tr>
        <th>Cities in {{city['countryname']}}</th>
        <td colspan="2">
          <a href="/country/{{city['slug_country']}}/">
            {{country_city_count}} cities
          </a>
        </td>
      </tr>
    </table>
  </section>

  <!-- ── Nearby Cities ────────────────────────────────────────── -->
  % if nearby:
  <section class="info-box nearby" id="nearby">
    <h2>Cities near {{city['cityname']}}, {{city['countryname']}}</h2>
    <p class="section-intro">
      The following cities are located closest to
      <strong>{{city['cityname']}}</strong>, sorted by straight-line distance.
    </p>
    <ul class="nearby-list">
      % for n in nearby:
      <li>
        <a href="/country/{{n['slug_country']}}/{{n['slug_region']}}/{{n['slug_city']}}/">
          {{n['cityname']}}
        </a>
        <span class="country-tag">{{n['countryname']}}</span>
        % if n.get('distance_km'):
        <span class="dist-tag">{{n['distance_km']}} km</span>
        % end
      </li>
      % end
    </ul>
  </section>
  % end

</article>
