<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>{{base_url}}/</loc><priority>1.0</priority></url>
  % for c in countries:
  <url>
    <loc>{{base_url}}/country/{{c['slug_country']}}/</loc>
    <priority>0.8</priority>
  </url>
  % end
</urlset>
