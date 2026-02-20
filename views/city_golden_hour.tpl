% import re as _re
% cslug_cont = _re.sub(r'[-\s]+', '-', city['continent'].lower().strip())
% city_url = '/country/' + city['slug_country'] + '/' + city['slug_region'] + '/' + city['slug_city'] + '/'

% rebase('base',
%   title=title,
%   description=description,
%   canonical=base_url + city_url + 'golden-hour/',
%   use_leaflet=False,
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

  <!-- ── Today's Times ─────────────────────────────────────────── -->
  <section class="info-box" id="golden-today">
    <h2>Golden Hour &amp; Blue Hour Today – {{city['cityname']}}</h2>
    <p class="section-intro">
      The <strong>golden hour</strong> is the short window just after sunrise and just before
      sunset when sunlight is warm, soft, and directional — the ideal light for photography.
      The <strong>blue hour</strong> occurs when the sun is slightly below the horizon,
      creating a cool, even blue tone in the sky.
      All times are in UTC.
    </p>

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
      just after sunrise and just before sunset. During this time, sunlight travels through more
      atmosphere, which scatters blue wavelengths and leaves warm golden tones.
      Photographers, filmmakers, and architects prize this light for its softness and depth.
    </p>
    <table class="coords-table">
      <tr>
        <th>Golden Hour definition</th>
        <td>Sun elevation between 0° and +6°</td>
      </tr>
      <tr>
        <th>Blue Hour definition</th>
        <td>Sun elevation between −6° and −4°</td>
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
