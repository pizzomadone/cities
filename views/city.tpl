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
%       "name": city['countryname']
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

  <h1>{{city['cityname']}}</h1>
  <p class="meta">
    {{city['stateprovince']}} &rsaquo;
    <a href="/country/{{city['slug_country']}}/">{{city['countryname']}}</a> &rsaquo;
    <a href="/continent/{{cslug_cont}}/">{{city['continent']}}</a>
  </p>

  <!-- Coordinates -->
  <section class="info-box">
    <h2>Geographic Coordinates</h2>
    % if has_coords:
    <table class="coords-table">
      <tr>
        <th>Latitude</th>
        <td>{{city['latitude']}} ({{lat_dms}})</td>
      </tr>
      <tr>
        <th>Longitude</th>
        <td>{{city['longitude']}} ({{lon_dms}})</td>
      </tr>
      <tr>
        <th>Country code</th>
        <td>{{city['countrycode']}}</td>
      </tr>
      <tr>
        <th>Continent</th>
        <td>{{city['continent']}}</td>
      </tr>
    </table>
    % else:
    <p>Coordinates not available for this location.</p>
    % end
  </section>

  <!-- Map -->
  % if has_coords:
  <section class="map-section">
    <h2>Map of {{city['cityname']}}</h2>
    <div id="map"></div>
    <script>
      var map = L.map('map').setView([{{city['latitude']}}, {{city['longitude']}}], 11);
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 18,
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      }).addTo(map);
      L.marker([{{city['latitude']}}, {{city['longitude']}}])
        .addTo(map)
        .bindPopup('<strong>{{city['cityname']}}</strong><br>{{city['countryname']}}')
        .openPopup();
    </script>
  </section>
  % end

  <!-- Nearby cities -->
  % if nearby:
  <section class="nearby">
    <h2>Cities near {{city['cityname']}}</h2>
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
