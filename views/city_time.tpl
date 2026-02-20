% import re as _re
% cslug_cont = _re.sub(r'[-\s]+', '-', city['continent'].lower().strip())
% city_url = '/country/' + city['slug_country'] + '/' + city['slug_region'] + '/' + city['slug_city'] + '/'

% rebase('base',
%   title=title,
%   description=description,
%   canonical=base_url + city_url + 'time/',
%   use_leaflet=False,
%   breadcrumbs=[
%     {'label': city['continent'],     'url': '/continent/' + cslug_cont + '/'},
%     {'label': city['countryname'],   'url': '/country/' + city['slug_country'] + '/'},
%     {'label': city['stateprovince'], 'url': '/country/' + city['slug_country'] + '/' + city['slug_region'] + '/'},
%     {'label': city['cityname'],      'url': city_url},
%     {'label': 'Current Time',        'url': city_url + 'time/'},
%   ]
% )

% include('_city_subnav', city=city, active_page='time')

<article class="city-detail subpage">

  <h1>
    % if geo['flag']:
    <span class="city-flag">{{geo['flag']}}</span>
    % end
    Current Time in {{city['cityname']}}, {{city['countryname']}}
  </h1>

  % if has_coords:
  <!-- ── Live Clock ────────────────────────────────────────────── -->
  <section class="info-box" id="clock">
    <div class="clock-display">
      <div class="clock-local" id="clock-local">--:--:--</div>
      <div class="clock-date"  id="clock-date">Loading…</div>
      <div class="clock-tz">Approximate local time ({{geo['tz_label']}})</div>
    </div>
    <div class="clock-utc-row">
      UTC time: <span id="clock-utc">--:--:--</span>
    </div>
  </section>

  <!-- ── Time Zone Info ────────────────────────────────────────── -->
  <section class="info-box" id="timezone">
    <h2>Time Zone of {{city['cityname']}}</h2>
    <p class="section-intro">
      Based on its longitude of <strong>{{city['longitude']}}°</strong>,
      <strong>{{city['cityname']}}</strong> lies in the approximate solar time zone
      <strong>{{geo['tz_label']}}</strong>.
      Note that the official (civil) time zone may differ due to national boundaries.
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
      <tr>
        <th>Today's Sunrise</th>
        <td colspan="2">{{geo['sunrise']}}</td>
      </tr>
      <tr>
        <th>Today's Sunset</th>
        <td colspan="2">{{geo['sunset']}}</td>
      </tr>
    </table>
  </section>
  % else:
  <section class="info-box">
    <p>Coordinates not available — cannot calculate time zone for this location.</p>
  </section>
  % end

</article>

% if has_coords:
<script>
(function() {
  var UTC_OFFSET = {{geo['tz_offset'] or 0}};
  var DAYS   = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];
  var MONTHS = ['January','February','March','April','May','June',
                'July','August','September','October','November','December'];

  function pad(n) { return String(n).padStart(2, '0'); }

  function tick() {
    var now  = new Date();
    var utcH = now.getUTCHours(), utcM = now.getUTCMinutes(), utcS = now.getUTCSeconds();

    var localMs   = now.getTime() + UTC_OFFSET * 3600000;
    var local     = new Date(localMs);
    var lH = local.getUTCHours(), lM = local.getUTCMinutes(), lS = local.getUTCSeconds();

    document.getElementById('clock-local').textContent =
      pad(lH) + ':' + pad(lM) + ':' + pad(lS);
    document.getElementById('clock-utc').textContent =
      pad(utcH) + ':' + pad(utcM) + ':' + pad(utcS);
    document.getElementById('clock-date').textContent =
      DAYS[local.getUTCDay()] + ', ' + local.getUTCDate() + ' ' +
      MONTHS[local.getUTCMonth()] + ' ' + local.getUTCFullYear();
  }

  tick();
  setInterval(tick, 1000);
})();
</script>
% end
