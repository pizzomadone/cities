% import re as _re
% cslug = _re.sub(r'[-\s]+', '-', country['continent'].lower().strip())
% rebase('base',
%   title=title,
%   description=description,
%   canonical=base_url + '/country/' + country['slug_country'] + '/',
%   breadcrumbs=[
%     {'label': country['continent'], 'url': '/continent/' + cslug + '/'},
%     {'label': country['countryname'], 'url': '/country/' + country['slug_country'] + '/'},
%   ]
% )

<h1>Cities in {{country['countryname']}}</h1>
<p class="meta">
  Continent: <a href="/continent/{{cslug}}/">{{country['continent']}}</a> &nbsp;|&nbsp;
  Country code: <strong>{{country['countrycode']}}</strong>
</p>

<h2>Regions & Provinces ({{len(regions)}})</h2>
<div class="card-grid">
  % for row in regions:
  <a href="/country/{{country['slug_country']}}/{{row['slug_region']}}/" class="card">
    <strong>{{row['stateprovince'] or '(unnamed)'}}</strong>
    <span>{{'{:,}'.format(row['city_count'])}} cities</span>
  </a>
  % end
</div>
