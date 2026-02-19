% rebase('base', title=title, description=description, canonical=base_url + '/')
% import json
% schema = {"@context":"https://schema.org","@type":"WebSite","name":"WorldCities","url": base_url}
% schema_json = json.dumps(schema)

<script type="application/ld+json">{{!schema_json}}</script>

<section class="hero">
  <h1>World Cities Directory</h1>
  <p>Explore geographic data for millions of cities across every country and continent.
     Find GPS coordinates, maps, and nearby places.</p>
</section>

<section class="continent-grid">
  <h2>Browse by Continent</h2>
  <div class="card-grid">
    % for c in continents:
    % import re
    % cslug = re.sub(r'[-\s]+', '-', c['continent'].lower().strip())
    <a href="/continent/{{cslug}}/" class="card">
      <strong>{{c['continent']}}</strong>
      <span>{{'{:,}'.format(c['city_count'])}} cities</span>
      <span>{{c['country_count']}} countries</span>
    </a>
    % end
  </div>
</section>
