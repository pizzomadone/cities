% import re as _re
% cslug_cont = _re.sub(r'[-\s]+', '-', city['continent'].lower().strip())
% city_url = '/country/' + city['slug_country'] + '/' + city['slug_region'] + '/' + city['slug_city'] + '/'

% rebase('base',
%   title=title,
%   description=description,
%   canonical=base_url + city_url + 'moon/',
%   use_leaflet=False,
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

  <!-- ── Today's Phase ────────────────────────────────────────── -->
  <section class="info-box" id="moon-today">
    <h2>Current Moon Phase – {{city['cityname']}}</h2>
    <p class="section-intro">
      The moon phase is the same worldwide. Today, the moon is in its
      <strong>{{moon['name']}}</strong> phase, with
      <strong>{{moon['illumination']}}%</strong> of its surface illuminated.
    </p>
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

  <!-- ── Monthly Lunar Calendar ───────────────────────────────── -->
  % for mo in moon_calendar:
  <section class="info-box" id="moon-{{mo['year']}}-{{mo['month']}}">
    <h2>Lunar Calendar – {{mo['month_name']}} {{mo['year']}}</h2>
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
          <tr{{!' class="today-row"' if d['is_today'] else ''}}>
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
