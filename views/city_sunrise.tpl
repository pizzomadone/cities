% import re as _re, json as _json
% cslug_cont = _re.sub(r'[-\s]+', '-', city['continent'].lower().strip())
% city_url = '/country/' + city['slug_country'] + '/' + city['slug_region'] + '/' + city['slug_city'] + '/'

% rebase('base',
%   title=title,
%   description=description,
%   canonical=base_url + city_url + 'sunrise/',
%   use_leaflet=False,
%   use_chartjs=bool(ann_daylight),
%   breadcrumbs=[
%     {'label': city['continent'],     'url': '/continent/' + cslug_cont + '/'},
%     {'label': city['countryname'],   'url': '/country/' + city['slug_country'] + '/'},
%     {'label': city['stateprovince'], 'url': '/country/' + city['slug_country'] + '/' + city['slug_region'] + '/'},
%     {'label': city['cityname'],      'url': city_url},
%     {'label': 'Sunrise & Sunset',    'url': city_url + 'sunrise/'},
%   ]
% )

% include('_city_subnav', city=city, active_page='sunrise')

<article class="city-detail subpage">

  <h1>
    % if geo['flag']:
    <span class="city-flag">{{geo['flag']}}</span>
    % end
    Sunrise and Sunset in {{city['cityname']}}, {{city['countryname']}}
  </h1>

  % if has_coords:

  <!-- ── Intro SEO ─────────────────────────────────────────────── -->
  <section class="info-box" id="sunrise-intro">
    <p class="section-intro">
      What time does the sun rise in <strong>{{city['cityname']}}</strong> today?
      On <strong>{{geo['sun_date']}}</strong>, <strong>sunrise in {{city['cityname']}}</strong>
      is at <strong>{{geo['sunrise']}}</strong> and
      <strong>sunset in {{city['cityname']}}</strong> is at <strong>{{geo['sunset']}}</strong>.
      The total duration of daylight today is <strong>{{geo['day_length']}}</strong>.
      % if season:
      It is currently <strong>{{season['name']}}</strong> {{season['emoji']}} in the {{season['hemisphere']}}
      ({{season['months']}}).
      % end
      The annual chart and monthly table use local standard time ({{geo['tz_label']}}). The day-by-day calendar below shows UTC.
    </p>
  </section>

  <!-- ── Today ─────────────────────────────────────────────────── -->
  <section class="info-box" id="today">
    <h2>Sunrise &amp; Sunset Today – {{city['cityname']}}</h2>
    <table class="coords-table">
      <tr><th>Date</th>         <td colspan="2">{{geo['sun_date']}}</td></tr>
      <tr><th>Sunrise (UTC)</th><td colspan="2">{{geo['sunrise']}}</td></tr>
      <tr><th>Sunset (UTC)</th> <td colspan="2">{{geo['sunset']}}</td></tr>
      <tr><th>Day Length</th>   <td colspan="2">{{geo['day_length']}}</td></tr>
      % if season:
      <tr><th>Season</th>
          <td colspan="2">{{season['emoji']}} {{season['name']}} · {{season['months']}}</td></tr>
      % end
    </table>
  </section>

  <!-- ── Annual Chart ───────────────────────────────────────────── -->
  % if ann_daylight:
  <section class="info-box" id="sunrise-chart">
    <h2>Sunrise &amp; Sunset Times Throughout the Year – {{city['cityname']}}</h2>
    <p class="section-intro">
      The chart below shows when the sun rises and sets in <strong>{{city['cityname']}}</strong>
      for each month of the year. The shaded band between the two curves represents the hours of daylight.
      The widest point marks the summer solstice, the narrowest the winter solstice.
    </p>
    <div class="chart-container">
      <canvas id="sunriseChart"></canvas>
    </div>
  </section>
  % end

  <!-- ── Monthly Calendar ─────────────────────────────────────── -->
  % if sun_calendar:
  <section class="info-box sun-calendar" id="calendar">
    <h2>Monthly Sunrise &amp; Sunset Calendar – {{city['cityname']}}</h2>
    <p class="section-intro">
      Daily sunrise and sunset times (UTC) for <strong>{{city['cityname']}}, {{city['countryname']}}</strong>
      across the previous, current, and next month. Moon phases are shown in the last column.
      Use this calendar to plan outdoor activities, photography shoots, or travel.
    </p>
    % for mo in sun_calendar:
    <h3>{{mo['month_name']}} {{mo['year']}} – {{city['cityname']}}</h3>
    <div class="sun-table-wrap">
      <table class="sun-table">
        <thead>
          <tr>
            <th>Day</th><th>Date</th>
            <th>Sunrise (UTC)</th><th>Sunset (UTC)</th>
            <th>Daylight</th><th title="Moon phase">Moon</th>
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
            <td class="moon-col" title="{{d['moon']}}">{{d['moon']}}</td>
          </tr>
          % end
        </tbody>
      </table>
    </div>
    % end
  </section>
  % end

  % else:
  <section class="info-box">
    <p>Coordinates not available — cannot calculate sunrise and sunset for this location.</p>
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

  new Chart(document.getElementById('sunriseChart'), {
    type: 'line',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'Sunrise ({{geo['tz_label']}})',
          data: sunrises,
          borderColor: '#e8821d',
          backgroundColor: 'rgba(232,130,29,0.06)',
          tension: 0.4, fill: false, pointRadius: 4, pointHoverRadius: 6,
        },
        {
          label: 'Sunset ({{geo['tz_label']}})',
          data: sunsets,
          borderColor: '#2a5298',
          backgroundColor: 'rgba(42,82,152,0.10)',
          tension: 0.4, fill: '-1', pointRadius: 4, pointHoverRadius: 6,
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
