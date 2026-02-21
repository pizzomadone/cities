% import re as _re, json as _json
% cslug_cont = _re.sub(r'[-\s]+', '-', city['continent'].lower().strip())
% city_url = '/country/' + city['slug_country'] + '/' + city['slug_region'] + '/' + city['slug_city'] + '/'

% rebase('base',
%   title=title,
%   description=description,
%   canonical=base_url + city_url + 'daylight/',
%   use_leaflet=False,
%   use_chartjs=True,
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
    Daylight Hours in {{city['cityname']}}, {{city['countryname']}} – By Month
  </h1>

  % if ann_daylight:
  % lat_abs = abs(city['latitude'])

  <!-- ── Intro SEO ─────────────────────────────────────────────── -->
  <section class="info-box" id="daylight-intro">
    <p class="section-intro">
      How many hours of daylight does <strong>{{city['cityname']}}</strong> get throughout the year?
      Located at latitude <strong>{{city['latitude']}}°</strong>,
      % if lat_abs < 10:
      {{city['cityname']}} is near the equator and experiences relatively stable daylight hours year-round, typically between 11 and 13 hours.
      % elif lat_abs < 35:
      {{city['cityname']}} is in the tropics or subtropics, where daylight varies moderately between seasons.
      % elif lat_abs < 60:
      {{city['cityname']}} experiences significant seasonal variation — long summer days and short winter days are a defining feature of life at this latitude.
      % else:
      {{city['cityname']}} is at a high latitude and experiences extreme seasonal daylight variation, including very long summer days and very short winter days.
      % end
      Today, <strong>{{city['cityname']}}</strong> has approximately <strong>{{geo['day_length']}}</strong> of daylight.
    </p>
  </section>

  <!-- ── Chart ─────────────────────────────────────────────────── -->
  <section class="info-box" id="daylight-chart">
    <h2>Annual Daylight Hours Chart – {{city['cityname']}}</h2>
    <p class="section-intro">
      The chart shows how sunrise and sunset times shift throughout the year in
      <strong>{{city['cityname']}}</strong>. The shaded area between the two lines represents
      the hours of daylight each month. All times are in UTC.
    </p>
    <div class="chart-container">
      <canvas id="daylightChart"></canvas>
    </div>
  </section>

  <!-- ── Table ─────────────────────────────────────────────────── -->
  <section class="info-box" id="daylight-table">
    <h2>Sunrise &amp; Sunset by Month – {{city['cityname']}}</h2>
    <p class="section-intro">
      Typical sunrise, sunset, and total hours of sunlight for <strong>{{city['cityname']}}, {{city['countryname']}}</strong>
      throughout the year. Values are calculated for the 15th of each month ({{geo['tz_label']}}).
    </p>
    <div class="sun-table-wrap">
      <table class="sun-table annual-table">
        <thead>
          <tr>
            <th>Month</th><th>Sunrise ({{geo['tz_label']}})</th><th>Sunset ({{geo['tz_label']}})</th><th>Daylight</th>
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

% if ann_daylight:
<script>
(function() {
  var labels   = {{!_json.dumps([m['month_short'] for m in ann_daylight])}};
  var sunrises = {{!_json.dumps([m['sunrise_h'] for m in ann_daylight])}};
  var sunsets  = {{!_json.dumps([m['sunset_h']  for m in ann_daylight])}};

  function hToHHMM(h) {
    var hh = Math.floor(h), mm = Math.round((h - hh) * 60);
    return String(hh).padStart(2,'0') + ':' + String(mm).padStart(2,'0');
  }

  new Chart(document.getElementById('daylightChart'), {
    type: 'line',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'Sunrise ({{geo['tz_label']}})',
          data: sunrises,
          borderColor: '#e8821d',
          backgroundColor: 'rgba(232,130,29,0.08)',
          tension: 0.4, fill: false, pointRadius: 4,
        },
        {
          label: 'Sunset ({{geo['tz_label']}})',
          data: sunsets,
          borderColor: '#2a5298',
          backgroundColor: 'rgba(42,82,152,0.12)',
          tension: 0.4, fill: '-1', pointRadius: 4,
        }
      ]
    },
    options: {
      responsive: true,
      interaction: { mode: 'index' },
      plugins: {
        tooltip: {
          callbacks: {
            label: function(ctx) {
              return ctx.dataset.label + ': ' + hToHHMM(ctx.parsed.y);
            }
          }
        }
      },
      scales: {
        y: {
          title: { display: true, text: 'Time of Day ({{geo['tz_label']}})' },
          ticks: { callback: function(v) { return hToHHMM(v); } },
          suggestedMin: 0, suggestedMax: 24,
        }
      }
    }
  });
})();
</script>
% end
