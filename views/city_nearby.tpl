% import re as _re
% cslug_cont = _re.sub(r'[-\s]+', '-', city['continent'].lower().strip())
% city_url = '/country/' + city['slug_country'] + '/' + city['slug_region'] + '/' + city['slug_city'] + '/'

% rebase('base',
%   title=title,
%   description=description,
%   canonical=base_url + city_url + 'nearby/',
%   use_leaflet=has_coords,
%   breadcrumbs=[
%     {'label': city['continent'],     'url': '/continent/' + cslug_cont + '/'},
%     {'label': city['countryname'],   'url': '/country/' + city['slug_country'] + '/'},
%     {'label': city['stateprovince'], 'url': '/country/' + city['slug_country'] + '/' + city['slug_region'] + '/'},
%     {'label': city['cityname'],      'url': city_url},
%     {'label': 'Nearby Cities',       'url': city_url + 'nearby/'},
%   ]
% )

% include('_city_subnav', city=city, active_page='nearby')

<article class="city-detail subpage">

  <h1>
    % if geo['flag']:
    <span class="city-flag">{{geo['flag']}}</span>
    % end
    Cities near {{city['cityname']}}, {{city['countryname']}}
  </h1>

  % if has_coords and nearby:
  % nearest = nearby[0]

  <!-- ── Intro SEO ─────────────────────────────────────────────── -->
  <section class="info-box" id="nearby-intro">
    <p class="section-intro">
      The nearest city to <strong>{{city['cityname']}}</strong> is
      <strong>
        <a href="/country/{{nearest['slug_country']}}/{{nearest['slug_region']}}/{{nearest['slug_city']}}/">
          {{nearest['cityname']}}
        </a>
      </strong>,
      located approximately <strong>{{round(nearest['distance_km'])}} km</strong> away.
      The table below lists all cities near <strong>{{city['cityname']}}, {{city['countryname']}}</strong>,
      sorted by straight-line distance. Coordinates: {{city['latitude']}}°N, {{city['longitude']}}°E.
    </p>
  </section>

  <!-- ── Map ───────────────────────────────────────────────────── -->
  <section class="map-section" id="nearby-map">
    <h2>Map of Cities near {{city['cityname']}}</h2>
    <div id="map"></div>
    <script>
      var map = L.map('map').setView([{{city['latitude']}}, {{city['longitude']}}], 8);
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 18,
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
      }).addTo(map);

      // Main city marker
      L.marker([{{city['latitude']}}, {{city['longitude']}}], {
        icon: L.divIcon({className: 'main-city-marker', html: '★', iconSize: [20,20]})
      }).addTo(map)
        .bindPopup('<strong>{{city['cityname']}}</strong> (this city)');

      // Nearby city markers
      % for n in nearby:
      % if n['latitude'] and n['longitude']:
      L.marker([{{n['latitude']}}, {{n['longitude']}}])
        .addTo(map)
        .bindPopup('<strong>{{n['cityname']}}</strong><br>{{n['stateprovince']}}, {{n['countryname']}}<br>≈ {{round(n['distance_km'])}} km');
      % end
      % end
    </script>
  </section>

  <!-- ── List ──────────────────────────────────────────────────── -->
  <section class="info-box" id="nearby-list">
    <h2>Nearest Cities to {{city['cityname']}}, {{city['stateprovince']}}</h2>
    <div class="sun-table-wrap">
      <table class="sun-table nearby-table">
        <thead>
          <tr>
            <th>#</th>
            <th>City</th>
            <th>Region</th>
            <th>Country</th>
            <th>Distance</th>
          </tr>
        </thead>
        <tbody>
          % for i, n in enumerate(nearby, 1):
          <tr>
            <td class="nearby-rank">{{i}}</td>
            <td class="nearby-city">
              <a href="/country/{{n['slug_country']}}/{{n['slug_region']}}/{{n['slug_city']}}/">
                {{n['cityname']}}
              </a>
            </td>
            <td class="nearby-region">{{n['stateprovince']}}</td>
            <td class="nearby-country">{{n['countryname']}}</td>
            <td class="nearby-dist"><strong>{{round(n['distance_km'])}} km</strong></td>
          </tr>
          % end
        </tbody>
      </table>
    </div>
  </section>

  % else:
  <section class="info-box">
    <p>No nearby cities found for this location.</p>
  </section>
  % end

</article>
