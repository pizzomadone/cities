% import re as _re
% cslug = _re.sub(r'[-\s]+', '-', region['continent'].lower().strip())
% rebase('base',
%   title=title,
%   description=description,
%   canonical=base_url + '/country/' + region['slug_country'] + '/' + region['slug_region'] + '/',
%   breadcrumbs=[
%     {'label': region['continent'],      'url': '/continent/' + cslug + '/'},
%     {'label': region['countryname'],    'url': '/country/' + region['slug_country'] + '/'},
%     {'label': region['stateprovince'],  'url': '/country/' + region['slug_country'] + '/' + region['slug_region'] + '/'},
%   ]
% )

<h1>Cities in {{region['stateprovince']}}, {{region['countryname']}}</h1>
<p class="meta">{{'{:,}'.format(pag['total'])}} cities found in this region.</p>

<table class="city-table">
  <thead>
    <tr>
      <th>City</th>
      <th>Latitude</th>
      <th>Longitude</th>
    </tr>
  </thead>
  <tbody>
    % for c in cities:
    <tr>
      <td>
        <a href="/country/{{region['slug_country']}}/{{region['slug_region']}}/{{c['slug_city']}}/">
          {{c['cityname']}}
        </a>
      </td>
      <td>{{c['latitude'] if c['latitude'] else '—'}}</td>
      <td>{{c['longitude'] if c['longitude'] else '—'}}</td>
    </tr>
    % end
  </tbody>
</table>

% if pag['total_pages'] > 1:
<nav class="pagination" aria-label="Pagination">
  % base_href = '/country/' + region['slug_country'] + '/' + region['slug_region'] + '/'
  % if pag['has_prev']:
  <a href="{{base_href}}?page={{pag['page'] - 1}}">&larr; Prev</a>
  % end
  <span>Page {{pag['page']}} of {{pag['total_pages']}}</span>
  % if pag['has_next']:
  <a href="{{base_href}}?page={{pag['page'] + 1}}">Next &rarr;</a>
  % end
</nav>
% end
