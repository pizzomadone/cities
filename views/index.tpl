% rebase('base', title=title, description=description, canonical=base_url + '/')
% import json
% schema = {"@context":"https://schema.org","@type":"WebSite","name":"WorldCities","url": base_url}
% schema_json = json.dumps(schema)

<script type="application/ld+json">{{!schema_json}}</script>

<section class="hero">
  <h1>World Cities Directory</h1>
  <p>Explore geographic data for millions of cities across every country and continent.
     Find GPS coordinates, maps, time zones, sunrise &amp; sunset times, and nearby places.</p>
  <form action="/search" method="get" class="search-form" role="search">
    <label for="q" class="sr-only">Search for a city</label>
    <input id="q" type="search" name="q" placeholder="Search for a city… (e.g. Rome, Tokyo, New York)"
           autocomplete="off" spellcheck="false">
    <button type="submit">Search</button>
  </form>
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
