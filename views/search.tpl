% rebase('base', title=title, description=description)

<section class="search-page">

  <h1>Search Cities</h1>

  <form action="/search" method="get" class="search-form" role="search">
    <label for="q" class="sr-only">Search for a city</label>
    <input id="q" type="search" name="q" value="{{q}}"
           placeholder="Search for a city… (e.g. Rome, Tokyo, New York)"
           autocomplete="off" spellcheck="false" autofocus>
    <button type="submit">Search</button>
  </form>

  % if q and len(q) < 2:
  <p class="search-hint">Please enter at least 2 characters.</p>
  % elif q and not results:
  <p class="search-hint">No cities found for <strong>{{q}}</strong>. Try a different spelling.</p>
  % elif results:
  <p class="search-count">
    Found <strong>{{len(results)}}</strong> result{{'s' if len(results) != 1 else ''}}
    for <strong>{{q}}</strong>
    % if len(results) == 30:
    <span class="search-limit">(showing first 30)</span>
    % end
  </p>
  <ul class="search-results">
    % for r in results:
    <li>
      <a href="/country/{{r['slug_country']}}/{{r['slug_region']}}/{{r['slug_city']}}/"
         class="result-name">{{r['cityname']}}</a>
      <span class="result-region">{{r['stateprovince']}}</span>
      <a href="/country/{{r['slug_country']}}/" class="result-country">
        {{r['countryname']}}
        <span class="result-code">({{r['countrycode']}})</span>
      </a>
    </li>
    % end
  </ul>
  % end

</section>
