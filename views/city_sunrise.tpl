% import re as _re
% cslug_cont = _re.sub(r'[-\s]+', '-', city['continent'].lower().strip())
% city_url = '/country/' + city['slug_country'] + '/' + city['slug_region'] + '/' + city['slug_city'] + '/'

% rebase('base',
%   title=title,
%   description=description,
%   canonical=base_url + city_url + 'sunrise/',
%   use_leaflet=False,
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

  <!-- ── Today ────────────────────────────────────────────────── -->
  <section class="info-box" id="today">
    <h2>Sunrise &amp; Sunset Today in {{city['cityname']}}</h2>
    <p class="section-intro">
      On <strong>{{geo['sun_date']}}</strong>, sunrise in <strong>{{city['cityname']}}</strong>
      is at <strong>{{geo['sunrise']}}</strong> and sunset at <strong>{{geo['sunset']}}</strong>
      (UTC). Total daylight: <strong>{{geo['day_length']}}</strong>.
    </p>
    <table class="coords-table">
      <tr><th>Date</th>      <td colspan="2">{{geo['sun_date']}}</td></tr>
      <tr><th>Sunrise (UTC)</th><td colspan="2">{{geo['sunrise']}}</td></tr>
      <tr><th>Sunset (UTC)</th> <td colspan="2">{{geo['sunset']}}</td></tr>
      <tr><th>Day Length</th>   <td colspan="2">{{geo['day_length']}}</td></tr>
      % if season:
      <tr><th>Current Season</th>
          <td colspan="2">{{season['emoji']}} {{season['name']}} ({{season['months']}})</td></tr>
      % end
    </table>
  </section>

  <!-- ── Monthly Calendar ─────────────────────────────────────── -->
  % if sun_calendar:
  <section class="info-box sun-calendar" id="calendar">
    <h2>Monthly Sunrise &amp; Sunset Calendar – {{city['cityname']}}</h2>
    <p class="section-intro">
      Daily sunrise, sunset, and daylight duration (UTC) for
      <strong>{{city['cityname']}}</strong> across the previous, current, and next month.
    </p>
    % for mo in sun_calendar:
    <h3>{{mo['month_name']}} {{mo['year']}}</h3>
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
            <td class="moon-col" title="Moon phase">{{d['moon']}}</td>
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
