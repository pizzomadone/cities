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

  <!-- ── Current Season ──────────────────────────────────────── -->
  % if season:
  <section class="info-box" id="current-season">
    <h2>Current Season in {{city['cityname']}}</h2>
    <p class="section-intro">
      Based on its position in the <strong>{{season['hemisphere']}}</strong>,
      <strong>{{city['cityname']}}</strong> is currently in
      <strong>{{season['name']}}</strong> {{season['emoji']}}.
      Meteorological {{season['name'].lower()}} in the {{season['hemisphere']}} runs from
      <strong>{{season['months']}}</strong>.
    </p>
    <table class="coords-table">
      <tr>
        <th>Current Season</th>
        <td colspan="2" class="season-cell">
          <span class="season-emoji">{{season['emoji']}}</span>
          <strong>{{season['name']}}</strong>
        </td>
      </tr>
      <tr>
        <th>Hemisphere</th>
        <td colspan="2">{{season['hemisphere']}}</td>
      </tr>
      <tr>
        <th>Season Months</th>
        <td colspan="2">{{season['months']}}</td>
      </tr>
    </table>
  </section>
  % end

  <!-- ── Sunrise & Sunset ─────────────────────────────────────── -->
  <section class="info-box" id="sun-times">
    <h2>Sunrise and Sunset in {{city['cityname']}} Today</h2>
    <p class="section-intro">
      On <strong>{{geo['sun_date']}}</strong>, the approximate
      <strong>sunrise in {{city['cityname']}}</strong> is at
      <strong>{{geo['sunrise']}}</strong> and the
      <strong>sunset in {{city['cityname']}}</strong> is at
      <strong>{{geo['sunset']}}</strong>.
      The total daylight duration is approximately <strong>{{geo['day_length']}}</strong>.
      All times are in Coordinated Universal Time (UTC).
    </p>
    <table class="coords-table">
      <tr>
        <th>Date</th>
        <td colspan="2">{{geo['sun_date']}}</td>
      </tr>
      <tr>
        <th>Sunrise (UTC)</th>
        <td colspan="2">{{geo['sunrise']}}</td>
      </tr>
      <tr>
        <th>Sunset (UTC)</th>
        <td colspan="2">{{geo['sunset']}}</td>
      </tr>
      <tr>
        <th>Day Length</th>
        <td colspan="2">{{geo['day_length']}}</td>
      </tr>
    </table>
  </section>

  <!-- ── Golden Hour & Blue Hour ─────────────────────────────── -->
  % if golden:
  <section class="info-box" id="golden-hour">
    <h2>Golden Hour &amp; Blue Hour in {{city['cityname']}} Today</h2>
    <p class="section-intro">
      The <strong>golden hour</strong> is the period just after sunrise and just before sunset when
      sunlight is soft and warm – ideal for photography. The <strong>blue hour</strong> occurs when
      the sun is slightly below the horizon, bathing the sky in a deep blue tone.
      All times are in UTC.
    </p>
    <table class="coords-table golden-table">
      <thead>
        <tr><th colspan="3">Morning</th></tr>
      </thead>
      <tbody>
        <tr>
          <th>🌑 Blue Hour</th>
          <td colspan="2">{{golden['blue_morning_start']}} – {{golden['blue_morning_end']}}</td>
        </tr>
        <tr>
          <th>🌅 Golden Hour</th>
          <td colspan="2">{{golden['golden_morning_start']}} – {{golden['golden_morning_end']}}</td>
        </tr>
      </tbody>
      <thead>
        <tr><th colspan="3">Evening</th></tr>
      </thead>
      <tbody>
        <tr>
          <th>🌇 Golden Hour</th>
          <td colspan="2">{{golden['golden_evening_start']}} – {{golden['golden_evening_end']}}</td>
        </tr>
        <tr>
          <th>🌃 Blue Hour</th>
          <td colspan="2">{{golden['blue_evening_start']}} – {{golden['blue_evening_end']}}</td>
        </tr>
      </tbody>
    </table>
  </section>
  % end

  <!-- ── Monthly Sun Calendar ────────────────────────────────── -->
  % if sun_calendar:
  <section class="info-box sun-calendar" id="sun-calendar">
    <h2>Monthly Sunrise and Sunset Calendar for {{city['cityname']}}, {{city['countryname']}}</h2>
    <p class="section-intro">
      Daily sunrise and sunset times (UTC) for <strong>{{city['cityname']}}</strong>
      across the previous, current, and next month.
      Use these tables to look up any specific date.
    </p>
    % for mo in sun_calendar:
    <h3>{{mo['month_name']}} {{mo['year']}} – Sunrise &amp; Sunset in {{city['cityname']}}</h3>
    <div class="sun-table-wrap">
      <table class="sun-table">
        <thead>
          <tr>
            <th>Day</th>
            <th>Date</th>
            <th>Sunrise (UTC)</th>
            <th>Sunset (UTC)</th>
            <th>Daylight</th>
            <th title="Moon phase">Moon</th>
          </tr>
        </thead>
        <tbody>
          % for d in mo['days']:
          <tr{{!' class="today-row"' if d['is_today'] else ''}}>
            <td class="dow">{{d['dow']}}</td>
            <td class="date-col">{{d['day']}} {{mo['month_name'][:3]}} {{mo['year']}}</td>
            <td class="sun-rise">{{d['sunrise']}}</td>
            <td class="sun-set">{{d['sunset']}}</td>
            <td class="day-len">{{d['day_length']}}</td>
            <td class="moon-col" title="Moon phase">{{d['moon']}}</td>
          </tr>
          % end
        </tbody>
      </table>
    </div>
    % end
  </section>
  % end

  <!-- ── Annual Daylight Table ────────────────────────────────── -->
  % if ann_daylight:
  <section class="info-box" id="annual-daylight">
    <h2>Daylight Hours by Month in {{city['cityname']}}</h2>
    <p class="section-intro">
      Typical sunrise, sunset, and total daylight for <strong>{{city['cityname']}}</strong>
      throughout the year, calculated for the 15th of each month.
      Times are in UTC.
    </p>
    <div class="sun-table-wrap">
      <table class="sun-table annual-table">
        <thead>
          <tr>
            <th>Month</th>
            <th>Sunrise (UTC)</th>
            <th>Sunset (UTC)</th>
            <th>Daylight</th>
          </tr>
        </thead>
        <tbody>
          % for m in ann_daylight:
          <tr>
            <td class="month-col"><strong>{{m['month_name']}}</strong></td>
            <td class="sun-rise">{{m['sunrise']}}</td>
            <td class="sun-set">{{m['sunset']}}</td>
            <td class="day-len">{{m['day_length']}}</td>
          </tr>
          % end
        </tbody>
      </table>
    </div>
  </section>
  % end

  <!-- ── Moon Phase ───────────────────────────────────────────── -->
  % if moon:
  <section class="info-box" id="moon-phase">
    <h2>Moon Phase Today in {{city['cityname']}}</h2>
    <p class="section-intro">
      Today the moon is in its <strong>{{moon['name']}}</strong> phase {{moon['emoji']}},
      with approximately <strong>{{moon['illumination']}}%</strong> of its surface illuminated.
      The moon is <strong>{{moon['age']}} days</strong> into the current lunar cycle.
    </p>
    <table class="coords-table">
      <tr>
        <th>Phase</th>
        <td colspan="2" class="moon-phase-cell">
          <span class="moon-emoji">{{moon['emoji']}}</span>
          <strong>{{moon['name']}}</strong>
        </td>
      </tr>
      <tr>
        <th>Illumination</th>
        <td colspan="2">{{moon['illumination']}}%</td>
      </tr>
      <tr>
        <th>Moon Age</th>
        <td colspan="2">{{moon['age']}} days into lunar cycle</td>
      </tr>
      <tr>
        <th>Days to Full Moon</th>
        <td colspan="2">{{moon['days_to_full']}} days</td>
      </tr>
      <tr>
        <th>Days to New Moon</th>
        <td colspan="2">{{moon['days_to_new']}} days</td>
      </tr>
    </table>
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
