% city_url = '/country/' + city['slug_country'] + '/' + city['slug_region'] + '/' + city['slug_city'] + '/'
<nav class="city-subnav" aria-label="City pages">
  <a href="{{city_url}}" class="subnav-back">← {{city['cityname']}}</a>
  <div class="subnav-tabs">
    <a href="{{city_url}}time/"        {{'class="subnav-active"' if active_page == 'time'        else ''}}>🕐 Time</a>
    <a href="{{city_url}}sunrise/"     {{'class="subnav-active"' if active_page == 'sunrise'     else ''}}>🌅 Sunrise</a>
    <a href="{{city_url}}moon/"        {{'class="subnav-active"' if active_page == 'moon'        else ''}}>🌑 Moon</a>
    <a href="{{city_url}}golden-hour/" {{'class="subnav-active"' if active_page == 'golden-hour' else ''}}>📸 Golden Hour</a>
    <a href="{{city_url}}daylight/"    {{'class="subnav-active"' if active_page == 'daylight'    else ''}}>☀️ Daylight</a>
    <a href="{{city_url}}nearby/"      {{'class="subnav-active"' if active_page == 'nearby'      else ''}}>📍 Nearby</a>
  </div>
</nav>
