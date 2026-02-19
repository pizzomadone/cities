<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <sitemap>
    <loc>{{base_url}}/sitemap-countries.xml</loc>
  </sitemap>
  % for i in range(1, num_chunks + 1):
  <sitemap>
    <loc>{{base_url}}/sitemap-cities-{{i}}.xml</loc>
  </sitemap>
  % end
</sitemapindex>
