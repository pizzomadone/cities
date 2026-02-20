% import re as _re
% cslug_cont = _re.sub(r'[-\s]+', '-', city['continent'].lower().strip())
% city_url = '/country/' + city['slug_country'] + '/' + city['slug_region'] + '/' + city['slug_city'] + '/'
% max_h = max((m['day_length_h'] for m in ann_daylight), default=24) or 24

% rebase('base',
%   title=title,
%   description=description,
%   canonical=base_url + city_url + 'daylight/',
%   use_leaflet=False,
%   breadcrumbs=[
%     {'label': city['continent'],     'url': '/continent/' + cslug_cont + '/'},
%     {'label': city['countryname'],   'url': '/country/' + city['slug_country'] + '/'},
%     {'label': city['stateprovince'], 'url': '/country/' + city['slug_country'] + '/' + city['slug_region'] + '/'},
%     {'label': city['cityname'],      'url': city_url},
%     {'label': 'Daylight Hours',      'url': city_url + 'daylight/'},
%   ]
% )

% include('_city_subnav', city=city, active_page='daylight')

<article class="city-detail subpage">

  <h1>
    % if geo['flag']:
    <span class="city-flag">{{geo['flag']}}</span>
    % end
    Daylight Hours in {{city['cityname']}}, {{city['countryname']}} by Month
  </h1>

  % if ann_daylight:

  <!-- ── Chart ────────────────────────────────────────────────── -->
  <section class="info-box" id="daylight-chart">
    <h2>Annual Daylight Chart – {{city['cityname']}}</h2>
    <p class="section-intro">
      Hours of daylight per month in <strong>{{city['cityname']}}</strong>.
      Calculated for the 15th of each month.
    </p>
    <div class="daylight-chart" aria-label="Daylight hours bar chart">
      % for m in ann_daylight:
      % bar_pct = round(m['day_length_h'] / max_h * 100, 1)
      <div class="daylight-bar-row">
        <span class="daylight-bar-label">{{m['month_short']}}</span>
        <div class="daylight-bar-track">
          <div class="daylight-bar-fill" style="width:{{bar_pct}}%"></div>
        </div>
        <span class="daylight-bar-value">{{m['day_length']}}</span>
      </div>
      % end
    </div>
  </section>

  <!-- ── Table ─────────────────────────────────────────────────── -->
  <section class="info-box" id="daylight-table">
    <h2>Sunrise &amp; Sunset by Month – {{city['cityname']}}</h2>
    <p class="section-intro">
      Typical sunrise, sunset, and total daylight for
      <strong>{{city['cityname']}}</strong> throughout the year (UTC).
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

  % else:
  <section class="info-box">
    <p>Coordinates not available — cannot calculate daylight hours for this location.</p>
  </section>
  % end

</article>
