% import re as _re, json as _json
% cslug_cont = _re.sub(r'[-\s]+', '-', city['continent'].lower().strip())
% city_url = '/country/' + city['slug_country'] + '/' + city['slug_region'] + '/' + city['slug_city'] + '/'

% rebase('base',
%   title=title,
%   description=description,
%   canonical=base_url + city_url + 'golden-hour/',
%   use_leaflet=False,
%   use_chartjs=bool(has_coords and golden),
%   breadcrumbs=[
%     {'label': city['continent'],     'url': '/continent/' + cslug_cont + '/'},
%     {'label': city['countryname'],   'url': '/country/' + city['slug_country'] + '/'},
%     {'label': city['stateprovince'], 'url': '/country/' + city['slug_country'] + '/' + city['slug_region'] + '/'},
%     {'label': city['cityname'],      'url': city_url},
%     {'label': 'Golden Hour',         'url': city_url + 'golden-hour/'},
%   ]
% )

% include('_city_subnav', city=city, active_page='golden-hour')

<article class="city-detail subpage">

  <h1>
    % if geo['flag']:
    <span class="city-flag">{{geo['flag']}}</span>
    % end
    Golden Hour in {{city['cityname']}}, {{city['countryname']}} – Today
  </h1>

  % if has_coords and golden:

  <!-- ── Intro SEO ─────────────────────────────────────────────── -->
  <section class="info-box" id="golden-intro">
    <p class="section-intro">
      What time is the golden hour in <strong>{{city['cityname']}}</strong> today?
      On <strong>{{geo['sun_date']}}</strong>, the morning golden hour in
      <strong>{{city['cityname']}}</strong> runs from
      <strong>{{golden['golden_morning_start']}}</strong> to
      <strong>{{golden['golden_morning_end']}}</strong> (UTC), and the evening golden hour
      from <strong>{{golden['golden_evening_start']}}</strong> to
      <strong>{{golden['golden_evening_end']}}</strong> (UTC).
      The <strong>blue hour</strong> occurs just before and after these windows,
      offering a cooler, softer natural light beloved by photographers.
      All times are in Coordinated Universal Time (UTC).
    </p>
  </section>

  <!-- ── Day Timeline Chart ────────────────────────────────────── -->
  <section class="info-box" id="golden-chart">
    <h2>Day Timeline – {{city['cityname']}}</h2>
    <p class="section-intro">
      The chart below shows how light conditions change throughout the day in
      <strong>{{city['cityname']}}</strong>. From night to blue hour, golden hour,
      full daylight, and back again — find the best times for outdoor photography.
    </p>
    <div class="chart-container">
      <canvas id="goldenChart"></canvas>
    </div>
  </section>

  <!-- ── Today's Times ─────────────────────────────────────────── -->
  <section class="info-box" id="golden-today">
    <h2>Golden Hour &amp; Blue Hour Times – {{city['cityname']}}</h2>

    <div class="golden-panels">

      <div class="golden-panel golden-panel--morning">
        <h3>🌄 Morning</h3>
        <table class="coords-table">
          <tr>
            <th>🌑 Blue Hour</th>
            <td>{{golden['blue_morning_start']}} – {{golden['blue_morning_end']}}</td>
          </tr>
          <tr>
            <th>🌅 Golden Hour</th>
            <td>{{golden['golden_morning_start']}} – {{golden['golden_morning_end']}}</td>
          </tr>
          <tr>
            <th>☀️ Sunrise</th>
            <td>{{geo['sunrise']}}</td>
          </tr>
        </table>
      </div>

      <div class="golden-panel golden-panel--evening">
        <h3>🌇 Evening</h3>
        <table class="coords-table">
          <tr>
            <th>☀️ Sunset</th>
            <td>{{geo['sunset']}}</td>
          </tr>
          <tr>
            <th>🌇 Golden Hour</th>
            <td>{{golden['golden_evening_start']}} – {{golden['golden_evening_end']}}</td>
          </tr>
          <tr>
            <th>🌃 Blue Hour</th>
            <td>{{golden['blue_evening_start']}} – {{golden['blue_evening_end']}}</td>
          </tr>
        </table>
      </div>

    </div>
  </section>

  <!-- ── What is Golden Hour ───────────────────────────────────── -->
  <section class="info-box" id="golden-info">
    <h2>What is the Golden Hour?</h2>
    <p class="section-intro">
      The <strong>golden hour</strong> (also called the <em>magic hour</em>) occurs twice daily —
      just after sunrise and just before sunset. During this period sunlight travels through more
      of the Earth's atmosphere, scattering shorter blue wavelengths and leaving warm amber and
      golden tones. The resulting light is soft, directional, and flattering — ideal for
      landscape photography, portrait work, and cinematography.
      The <strong>blue hour</strong> occurs when the sun is slightly below the horizon (between
      −6° and −4° elevation), casting an even, diffused blue light over the landscape.
    </p>
    <table class="coords-table">
      <tr>
        <th>Golden Hour</th>
        <td>Sun elevation between 0° and +6° above horizon</td>
      </tr>
      <tr>
        <th>Blue Hour</th>
        <td>Sun elevation between −6° and −4° below horizon</td>
      </tr>
      <tr>
        <th>Today's date</th>
        <td>{{geo['sun_date']}}</td>
      </tr>
      <tr>
        <th>Location</th>
        <td>{{city['cityname']}}, {{city['countryname']}} ({{city['latitude']}}°, {{city['longitude']}}°)</td>
      </tr>
    </table>
  </section>

  % else:
  <section class="info-box">
    <p>Coordinates not available — cannot calculate golden hour for this location.</p>
  </section>
  % end

</article>

% if has_coords and golden:
<script>
(function() {
  var bms = {{!_json.dumps(golden.get('blue_morning_start_h',   0))}};
  var bme = {{!_json.dumps(golden.get('blue_morning_end_h',     0))}};
  var gms = {{!_json.dumps(golden.get('golden_morning_start_h', 0))}};
  var gme = {{!_json.dumps(golden.get('golden_morning_end_h',   0))}};
  var ges = {{!_json.dumps(golden.get('golden_evening_start_h', 0))}};
  var gee = {{!_json.dumps(golden.get('golden_evening_end_h',   0))}};
  var bes = {{!_json.dumps(golden.get('blue_evening_start_h',   0))}};
  var bee = {{!_json.dumps(golden.get('blue_evening_end_h',     0))}};

  function hToHHMM(h) {
    if (h == null || isNaN(h)) return '';
    var hh = Math.floor(h), mm = Math.round((h - hh) * 60);
    return String(hh).padStart(2,'0') + ':' + String(mm).padStart(2,'0');
  }

  // Build floating-bar segments [start, end]
  var segments = [
    { label: 'Night',               color: '#1a2044', data: [0,   bms] },
    { label: 'Blue Hour (morning)', color: '#4d6fcb', data: [bms, bme] },
    { label: 'Golden Hour (morning)', color: '#f5a623', data: [gms, gme] },
    { label: 'Daylight',            color: '#87ceeb', data: [gme, ges] },
    { label: 'Golden Hour (evening)', color: '#e8821d', data: [ges, gee] },
    { label: 'Blue Hour (evening)', color: '#5a7db5', data: [gee, bee] },
    { label: 'Night (end)',         color: '#1a2044', data: [bee,  24] },
  ];

  var datasets = segments.map(function(s) {
    return {
      label: s.label,
      data: [[s.data[0], s.data[1]]],
      backgroundColor: s.color,
      borderColor: 'transparent',
      borderWidth: 0,
    };
  });

  new Chart(document.getElementById('goldenChart'), {
    type: 'bar',
    data: { labels: ['Today'], datasets: datasets },
    options: {
      indexAxis: 'y',
      responsive: true,
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            font: { size: 11 },
            filter: function(item) { return item.text !== 'Night (end)'; }
          }
        },
        tooltip: {
          callbacks: {
            label: function(ctx) {
              var d = ctx.raw;
              return ctx.dataset.label + ': ' + hToHHMM(d[0]) + ' – ' + hToHHMM(d[1]);
            }
          }
        }
      },
      scales: {
        x: {
          min: 0, max: 24,
          title: { display: true, text: 'Time of Day (UTC)' },
          ticks: { callback: function(v) { return hToHHMM(v); } },
          stacked: false,
        },
        y: { stacked: true }
      }
    }
  });
})();
</script>
% end
