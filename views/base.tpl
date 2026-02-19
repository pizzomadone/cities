<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{title}}</title>
  <meta name="description" content="{{description}}">
  % if defined('canonical'):
  <link rel="canonical" href="{{canonical}}">
  % end
  <link rel="stylesheet" href="/static/css/style.css">
  % if defined('schema_json'):
  <script type="application/ld+json">{{!schema_json}}</script>
  % end
  % if defined('use_leaflet') and use_leaflet:
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  % end
</head>
<body>

<header class="site-header">
  <div class="container">
    <a href="/" class="logo">WorldCities</a>
    <span class="tagline">Geographic directory of cities worldwide</span>
  </div>
</header>

% if defined('breadcrumbs') and breadcrumbs:
<nav class="breadcrumb" aria-label="Breadcrumb">
  <div class="container">
    <ol>
      <li><a href="/">Home</a></li>
      % for i, crumb in enumerate(breadcrumbs):
        % if i == len(breadcrumbs) - 1:
        <li aria-current="page">{{crumb['label']}}</li>
        % else:
        <li><a href="{{crumb['url']}}">{{crumb['label']}}</a></li>
        % end
      % end
    </ol>
  </div>
</nav>
% end

<main class="container">
  {{!base}}
</main>

<footer class="site-footer">
  <div class="container">
    <p>WorldCities — Geographic data for millions of locations worldwide.</p>
    <p><a href="/sitemap.xml">Sitemap</a></p>
  </div>
</footer>

</body>
</html>
