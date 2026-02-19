<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  % for c in cities:
  <url>
    <loc>{{base_url}}/country/{{c['slug_country']}}/{{c['slug_region']}}/{{c['slug_city']}}/</loc>
    <priority>0.6</priority>
  </url>
  % end
</urlset>
