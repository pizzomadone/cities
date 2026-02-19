% rebase('base',
%   title=title,
%   description=description,
%   canonical=base_url + '/continent/' + continent_slug + '/',
%   breadcrumbs=[{'label': continent, 'url': '/continent/' + continent_slug + '/'}]
% )

<h1>Cities in {{continent}}</h1>
<p>{{len(countries)}} countries — browse by country to explore regions and cities.</p>

<div class="card-grid">
  % for row in countries:
  <a href="/country/{{row['slug_country']}}/" class="card">
    <strong>{{row['countryname']}}</strong>
    <span>{{'{:,}'.format(row['city_count'])}} cities</span>
    <span>{{row['region_count']}} regions</span>
  </a>
  % end
</div>
