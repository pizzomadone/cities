% import re as _re, json as _json
% cslug_cont = _re.sub(r'[-\s]+', '-', city['continent'].lower().strip())
% city_url = '/country/' + city['slug_country'] + '/' + city['slug_region'] + '/' + city['slug_city'] + '/'
% cur_month = moon_calendar[1] if moon_calendar else None

% rebase('base',
%   title=title,
%   description=description,
%   canonical=base_url + city_url + 'moon/',
%   use_leaflet=False,
%   use_chartjs=True,
%   breadcrumbs=[
%     {'label': city['continent'],     'url': '/continent/' + cslug_cont + '/'},
%     {'label': city['countryname'],   'url': '/country/' + city['slug_country'] + '/'},
%     {'label': city['stateprovince'], 'url': '/country/' + city['slug_country'] + '/' + city['slug_region'] + '/'},
%     {'label': city['cityname'],      'url': city_url},
%     {'label': 'Moon Phase',          'url': city_url + 'moon/'},
%   ]
% )

% include('_city_subnav', city=city, active_page='moon')

<article class="city-detail subpage">

  <h1>
    % if geo['flag']:
    <span class="city-flag">{{geo['flag']}}</span>
    % end
    Moon Phase Today in {{city['cityname']}}, {{city['countryname']}}
  </h1>

  <!-- ── Intro SEO ─────────────────────────────────────────────── -->
  <section class="info-box" id="moon-intro">
    <p class="section-intro">
      What phase is the moon in <strong>{{city['cityname']}}</strong> tonight?
      The moon phase is identical everywhere on Earth. Tonight, the moon is in its
      <strong>{{moon['name']}}</strong> phase {{moon['emoji']}}, with
      <strong>{{moon['illumination']}}%</strong> of its surface visible.
      The moon is currently <strong>{{moon['age']}} days</strong> into its
      29.5-day lunar cycle. The next <strong>full moon</strong> is in
      <strong>{{moon['days_to_full']}} days</strong>, and the next
      <strong>new moon</strong> in <strong>{{moon['days_to_new']}} days</strong>.
    </p>
  </section>

  <!-- ── Today's Phase ─────────────────────────────────────────── -->
  <section class="info-box" id="moon-today">
    <h2>Current Moon Phase – {{city['cityname']}}</h2>
    <div class="moon-hero">
      <span class="moon-hero-emoji">{{moon['emoji']}}</span>
      <div class="moon-hero-info">
        <div class="moon-hero-name">{{moon['name']}}</div>
        <div class="moon-hero-illum">{{moon['illumination']}}% illuminated</div>
      </div>
    </div>
    <table class="coords-table">
      <tr><th>Phase</th>            <td colspan="2">{{moon['emoji']}} {{moon['name']}}</td></tr>
      <tr><th>Illumination</th>     <td colspan="2">{{moon['illumination']}}%</td></tr>
      <tr><th>Moon Age</th>         <td colspan="2">{{moon['age']}} days into lunar cycle</td></tr>
      <tr><th>Days to Full Moon</th><td colspan="2">{{moon['days_to_full']}} days</td></tr>
      <tr><th>Days to New Moon</th> <td colspan="2">{{moon['days_to_new']}} days</td></tr>
    </table>
  </section>

  <!-- ── Illumination Chart ────────────────────────────────────── -->
  % if cur_month:
  <section class="info-box" id="moon-chart">
    <h2>Moon Illumination – {{cur_month['month_name']}} {{cur_month['year']}}</h2>
    <p class="section-intro">
      The chart shows the moon's illumination percentage for each day of the current month.
      Peaks represent full moon (100%) and troughs represent new moon (0%).
    </p>
    <div class="chart-container">
      <canvas id="moonChart"></canvas>
    </div>
  </section>
  % end

  <!-- ── Monthly Lunar Calendars ───────────────────────────────── -->
  % for mo in moon_calendar:
  <section class="info-box" id="moon-{{mo['year']}}-{{mo['month']}}">
    <h2>Lunar Calendar – {{mo['month_name']}} {{mo['year']}}</h2>
    <p class="section-intro">
      Daily moon phases for <strong>{{mo['month_name']}} {{mo['year']}}</strong>.
      Full moon dates and new moon dates are highlighted in the table below.
    </p>
    <div class="sun-table-wrap">
      <table class="sun-table moon-table">
        <thead>
          <tr>
            <th>Day</th><th>Date</th>
            <th>Phase</th><th>Name</th><th>Illumination</th>
          </tr>
        </thead>
        <tbody>
          % for d in mo['days']:
          <tr{{!' class="today-row"' if d['is_today'] else (' class="full-moon-row"' if d['name'] == 'Full Moon' else (' class="new-moon-row"' if d['name'] == 'New Moon' else ''))}}>
            <td class="dow">{{d['dow']}}</td>
            <td class="date-col">{{d['day']}} {{mo['month_name'][:3]}} {{mo['year']}}</td>
            <td class="moon-col">{{d['emoji']}}</td>
            <td class="moon-name">{{d['name']}}</td>
            <td class="moon-illum">{{d['illumination']}}%</td>
          </tr>
          % end
        </tbody>
      </table>
    </div>
  </section>
  % end

</article>

% if cur_month:
<script>
(function() {
  var days   = {{!_json.dumps([d['day'] for d in cur_month['days']])}};
  var illums = {{!_json.dumps([d['illumination'] for d in cur_month['days']])}};

  new Chart(document.getElementById('moonChart'), {
    type: 'line',
    data: {
      labels: days,
      datasets: [{
        label: 'Moon Illumination (%)',
        data: illums,
        borderColor: '#888',
        backgroundColor: 'rgba(160,160,180,0.15)',
        fill: true, tension: 0.4,
        pointRadius: function(ctx) {
          var v = ctx.parsed.y;
          return (v >= 98 || v <= 2) ? 6 : 3;
        },
        pointBackgroundColor: function(ctx) {
          var v = ctx.parsed.y;
          if (v >= 98) return '#ffe066';
          if (v <= 2)  return '#333';
          return '#888';
        },
      }]
    },
    options: {
      responsive: true,
      plugins: {
        tooltip: {
          callbacks: {
            label: function(ctx) { return 'Illumination: ' + ctx.parsed.y + '%'; }
          }
        }
      },
      scales: {
        x: { title: { display: true, text: 'Day of Month' } },
        y: {
          title: { display: true, text: 'Illumination (%)' },
          min: 0, max: 100,
          ticks: { callback: function(v) { return v + '%'; } }
        }
      }
    }
  });
})();
</script>
% end
