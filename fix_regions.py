"""
fix_regions.py — Corregge le assegnazioni di regione errate nel DB cities.db

MODALITÀ:
  python fix_regions.py            → dry-run: stampa report, non tocca nulla
  python fix_regions.py --apply    → applica le correzioni (fa backup prima)

ALGORITMO in 4 fasi:
  1. Calcola centroidi "puliti" per ogni regione (esclude outlier > 500 km)
  2. DUPLICATI  : per ogni gruppo con stesse coordinate (±0.001°), tieni il
                  record la cui regione ha il centroide più vicino → DELETE
  3. SINGOLI ERRATI: per ogni città la cui distanza dal centroide della propria
                     regione è > 3× la distanza dalla regione più vicina →
                     UPDATE con il regionid/stateprovince/slug_region corretti
  4. DUPLICATI POST-UPDATE: simula gli UPDATE in memoria, poi trova coppie
                     con stesso (cityname, countrycode, regionid) entro 50 km
                     → DELETE il record con cityid maggiore
"""

import math
import os
import shutil
import sqlite3
import sys
from collections import defaultdict

DB_PATH  = os.environ.get('CITIES_DB', 'cities.db')
DRY_RUN  = '--apply' not in sys.argv

# ── soglie ────────────────────────────────────────────────────────────────────
# Distanza massima (km) per escludere un record dal calcolo del centroide grezzo
CENTROID_OUTLIER_KM = 500
# Una città è "sospetta" solo se dista almeno questo dalla sua regione assegnata
MIN_SUSPICIOUS_KM   = 150
# E la regione corretta deve essere almeno 3× più vicina della regione assegnata
RATIO_THRESHOLD     = 3.0


# ── utilità geografica ────────────────────────────────────────────────────────

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi   = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


# ── connessione DB ─────────────────────────────────────────────────────────────

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ── FASE 0: carica tutte le città con coordinate ──────────────────────────────

def load_cities(conn):
    return conn.execute("""
        SELECT cityid, cityname, countrycode, regionid,
               stateprovince, slug_region, slug_country,
               latitude, longitude
        FROM   cities
        WHERE  latitude IS NOT NULL AND longitude IS NOT NULL
          AND  cityname != '' AND regionid != ''
    """).fetchall()


# ── FASE 1: calcola centroidi puliti ──────────────────────────────────────────

def compute_centroids(cities):
    """
    Passo A: centroide grezzo.
    Passo B: ricalcola escludendo città a > CENTROID_OUTLIER_KM dal grezzo.
    Restituisce dict  (countrycode, regionid) → (avg_lat, avg_lon, n_cities).
    """
    # Passo A — grezzo
    buckets = defaultdict(list)
    for c in cities:
        key = (c['countrycode'], c['regionid'])
        buckets[key].append((c['latitude'], c['longitude']))

    raw = {}
    for key, pts in buckets.items():
        raw[key] = (
            sum(p[0] for p in pts) / len(pts),
            sum(p[1] for p in pts) / len(pts),
        )

    # Passo B — pulito (escludi outlier)
    clean_buckets = defaultdict(list)
    for c in cities:
        key = (c['countrycode'], c['regionid'])
        if key not in raw:
            continue
        rlat, rlon = raw[key]
        dist = haversine(c['latitude'], c['longitude'], rlat, rlon)
        if dist <= CENTROID_OUTLIER_KM:
            clean_buckets[key].append((c['latitude'], c['longitude']))

    centroids = {}
    for key, pts in clean_buckets.items():
        if pts:
            centroids[key] = (
                sum(p[0] for p in pts) / len(pts),
                sum(p[1] for p in pts) / len(pts),
                len(pts),
            )
    return centroids


# ── FASE 2: individua duplicati da eliminare ──────────────────────────────────

def find_duplicate_deletes(cities, centroids):
    """
    Raggruppa per (cityname, countrycode, lat arrotondata, lon arrotondata).
    Nei gruppi con > 1 record tiene quello con la regione più vicina (centroide),
    e prepara i cityid da eliminare.
    Restituisce (ids_to_delete, stats).
    """
    groups = defaultdict(list)
    for c in cities:
        key = (
            c['cityname'].lower(),
            c['countrycode'],
            round(c['latitude'],  3),
            round(c['longitude'], 3),
        )
        groups[key].append(c)

    ids_to_delete = []
    stats = {'groups': 0, 'same_region': 0, 'diff_region': 0, 'no_centroid': 0}

    for key, group in groups.items():
        if len(group) < 2:
            continue
        stats['groups'] += 1

        # Tutti con la stessa regione → tieni MIN(cityid), elimina gli altri
        region_ids = {c['regionid'] for c in group}
        if len(region_ids) == 1:
            stats['same_region'] += 1
            keep = min(group, key=lambda c: c['cityid'])
            ids_to_delete.extend(c['cityid'] for c in group if c['cityid'] != keep['cityid'])
            continue

        # Regioni diverse → usa distanza centroide
        stats['diff_region'] += 1
        city_lat = group[0]['latitude']
        city_lon = group[0]['longitude']

        best, best_dist = None, float('inf')
        for c in group:
            k = (c['countrycode'], c['regionid'])
            if k not in centroids:
                continue
            clat, clon, _ = centroids[k]
            d = haversine(city_lat, city_lon, clat, clon)
            if d < best_dist:
                best_dist = d
                best = c

        if best is None:
            # Nessun centroide disponibile → tieni MIN(cityid)
            stats['no_centroid'] += 1
            keep = min(group, key=lambda c: c['cityid'])
            ids_to_delete.extend(c['cityid'] for c in group if c['cityid'] != keep['cityid'])
        else:
            ids_to_delete.extend(c['cityid'] for c in group if c['cityid'] != best['cityid'])

    return ids_to_delete, stats


# ── FASE 3: individua singoli con regione errata ──────────────────────────────

def find_wrong_region_updates(cities, centroids, ids_to_delete_set):
    """
    Per ogni città NON già marcata per delete:
    - calcola distanza dalla regione assegnata
    - trova la regione più vicina (stesso countrycode)
    - se dist_assegnata > MIN_SUSPICIOUS_KM
      e dist_assegnata > RATIO_THRESHOLD × dist_vicina
      → prepara UPDATE

    Restituisce lista di dict con i campi da aggiornare.
    """
    # Indice   countrycode → lista di (regionid, avg_lat, avg_lon)
    country_regions = defaultdict(list)
    for (cc, rid), (clat, clon, _) in centroids.items():
        country_regions[cc].append((rid, clat, clon))

    # Per ogni regione recupera i metadati canonici (stateprovince, slug_region)
    # usando i valori più frequenti (moda) tra le città non-outlier
    region_meta = {}  # (countrycode, regionid) → {stateprovince, slug_region, slug_country}
    meta_counts  = defaultdict(lambda: defaultdict(int))
    for c in cities:
        k = (c['countrycode'], c['regionid'])
        meta_counts[k][(c['stateprovince'], c['slug_region'], c['slug_country'])] += 1
    for k, counts in meta_counts.items():
        best_meta = max(counts, key=counts.get)
        region_meta[k] = {
            'stateprovince': best_meta[0],
            'slug_region':   best_meta[1],
            'slug_country':  best_meta[2],
        }

    updates = []
    for c in cities:
        if c['cityid'] in ids_to_delete_set:
            continue

        assigned_key = (c['countrycode'], c['regionid'])
        if assigned_key not in centroids:
            continue

        clat, clon, _ = centroids[assigned_key]
        dist_assigned = haversine(c['latitude'], c['longitude'], clat, clon)

        if dist_assigned < MIN_SUSPICIOUS_KM:
            continue  # Va bene così

        # Trova la regione più vicina nello stesso paese
        best_rid, best_dist = None, float('inf')
        for rid, rlat, rlon in country_regions[c['countrycode']]:
            if rid == c['regionid']:
                continue
            d = haversine(c['latitude'], c['longitude'], rlat, rlon)
            if d < best_dist:
                best_dist = d
                best_rid  = rid

        if best_rid is None:
            continue

        if dist_assigned < RATIO_THRESHOLD * best_dist:
            continue  # Differenza non abbastanza netta

        new_key = (c['countrycode'], best_rid)
        if new_key not in region_meta:
            continue

        meta = region_meta[new_key]
        updates.append({
            'cityid':        c['cityid'],
            'old_region':    c['stateprovince'],
            'new_regionid':  best_rid,
            'new_province':  meta['stateprovince'],
            'new_slug_reg':  meta['slug_region'],
            'slug_country':  meta['slug_country'],
            'dist_old_km':   round(dist_assigned),
            'dist_new_km':   round(best_dist),
            'cityname':      c['cityname'],
            'countrycode':   c['countrycode'],
        })

    return updates


# ── FASE 4: duplicati creati dagli UPDATE ────────────────────────────────────

# Distanza massima (km) entro cui due record con stesso nome+regione
# vengono considerati duplicati dello stesso luogo fisico
POST_UPDATE_MAX_KM = 50


def find_post_update_duplicates(cities, updates, phase2_delete_set):
    """
    Simula gli UPDATE della Fase 3 in memoria, poi raggruppa per
    (cityname_lower, countrycode, regionid_effettivo).
    Nelle coppie con distanza < POST_UPDATE_MAX_KM mantiene MIN(cityid),
    marca l'altro per DELETE.
    Restituisce (ids_to_delete, n_groups).
    """
    # Mappa cityid → regionid che avrà dopo gli UPDATE
    update_map = {u['cityid']: u['new_regionid'] for u in updates}

    groups = defaultdict(list)
    for c in cities:
        if c['cityid'] in phase2_delete_set:
            continue
        effective_region = update_map.get(c['cityid'], c['regionid'])
        key = (c['cityname'].lower(), c['countrycode'], effective_region)
        groups[key].append(c)

    ids_to_delete = []
    n_groups = 0
    for key, group in groups.items():
        if len(group) < 2:
            continue
        # Ordina per cityid; confronta ogni coppia
        group.sort(key=lambda c: c['cityid'])
        keep = group[0]
        for other in group[1:]:
            d = haversine(
                keep['latitude'], keep['longitude'],
                other['latitude'], other['longitude'],
            )
            if d < POST_UPDATE_MAX_KM:
                ids_to_delete.append(other['cityid'])
                n_groups += 1

    return ids_to_delete, n_groups


# ── REPORT ────────────────────────────────────────────────────────────────────

def print_report(dup_ids, dup_stats, updates, post_ids, post_groups):
    print("=" * 65)
    print("  fix_regions.py — REPORT" + ("  [DRY RUN]" if DRY_RUN else "  [APPLY]"))
    print("=" * 65)

    print(f"\n── FASE 2: Duplicati ──────────────────────────────────────────")
    print(f"  Gruppi duplicati totali   : {dup_stats['groups']:>8,}")
    print(f"  Stessa regione (triviali) : {dup_stats['same_region']:>8,}")
    print(f"  Regioni diverse           : {dup_stats['diff_region']:>8,}")
    print(f"  Senza centroide           : {dup_stats['no_centroid']:>8,}")
    print(f"  Record da DELETE          : {len(dup_ids):>8,}")

    print(f"\n── FASE 3: Singoli con regione errata ─────────────────────────")
    print(f"  Record da UPDATE          : {len(updates):>8,}")

    if updates:
        print(f"\n  Campione (prime 20 righe):")
        print(f"  {'cityname':<25} {'paese':<4} {'da':<25} {'a':<25} {'dist_da':>8} {'dist_a':>8}")
        print(f"  {'-'*25} {'-'*4} {'-'*25} {'-'*25} {'-'*8} {'-'*8}")
        for u in updates[:20]:
            print(
                f"  {u['cityname'][:24]:<25} {u['countrycode']:<4} "
                f"  {u['old_region'][:24]:<25} {u['new_province'][:24]:<25} "
                f"  {u['dist_old_km']:>6} km  {u['dist_new_km']:>6} km"
            )

    print(f"\n── FASE 4: Duplicati post-update ──────────────────────────────")
    print(f"  Gruppi con duplicati < {POST_UPDATE_MAX_KM} km : {post_groups:>6,}")
    print(f"  Record da DELETE (fase 4)          : {len(post_ids):>6,}")

    print(f"\n── TOTALE modifiche ───────────────────────────────────────────")
    print(f"  DELETE : {len(dup_ids) + len(post_ids):,}  (fase2={len(dup_ids):,}  fase4={len(post_ids):,})")
    print(f"  UPDATE : {len(updates):,}")
    print()


# ── APPLICAZIONE ──────────────────────────────────────────────────────────────

def apply_changes(conn, dup_ids, updates, post_ids):
    backup = DB_PATH + '.bak'
    print(f"Backup → {backup}")
    shutil.copy2(DB_PATH, backup)

    cur = conn.cursor()
    BATCH = 500

    def batch_delete(ids, label):
        print(f"Eliminazione {len(ids):,} {label}...")
        for i in range(0, len(ids), BATCH):
            chunk = ids[i:i+BATCH]
            placeholders = ','.join('?' * len(chunk))
            cur.execute(f"DELETE FROM cities WHERE cityid IN ({placeholders})", chunk)
        conn.commit()
        print(f"  ✓ DELETE completate")

    # Fase 2 — duplicati per coordinate
    batch_delete(dup_ids, "duplicati (fase 2)")

    # Fase 3 — correzione regione
    print(f"Correzione {len(updates):,} assegnazioni di regione (fase 3)...")
    for u in updates:
        cur.execute("""
            UPDATE cities
            SET    regionid      = ?,
                   stateprovince = ?,
                   slug_region   = ?
            WHERE  cityid = ?
        """, (u['new_regionid'], u['new_province'], u['new_slug_reg'], u['cityid']))
    conn.commit()
    print(f"  ✓ UPDATE completate")

    # Fase 4 — duplicati creati dagli UPDATE
    if post_ids:
        batch_delete(post_ids, "duplicati post-update (fase 4)")

    # Conta righe finali
    total = cur.execute("SELECT COUNT(*) FROM cities").fetchone()[0]
    print(f"\nRighe totali dopo pulizia: {total:,}")


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    print(f"DB: {DB_PATH}")
    if DRY_RUN:
        print("Modalità DRY RUN — usa --apply per applicare le modifiche\n")

    conn = get_conn()

    print("Caricamento città...", end=' ', flush=True)
    cities = load_cities(conn)
    print(f"{len(cities):,} record con coordinate")

    print("Calcolo centroidi (2 passaggi)...", end=' ', flush=True)
    centroids = compute_centroids(cities)
    print(f"{len(centroids):,} regioni")

    print("Analisi duplicati...", end=' ', flush=True)
    dup_ids, dup_stats = find_duplicate_deletes(cities, centroids)
    print(f"{len(dup_ids):,} da eliminare")

    dup_ids_set = set(dup_ids)

    print("Analisi assegnazioni errate...", end=' ', flush=True)
    updates = find_wrong_region_updates(cities, centroids, dup_ids_set)
    print(f"{len(updates):,} da correggere")

    print("Analisi duplicati post-update...", end=' ', flush=True)
    post_ids, post_groups = find_post_update_duplicates(cities, updates, dup_ids_set)
    print(f"{len(post_ids):,} da eliminare")

    print()
    print_report(dup_ids, dup_stats, updates, post_ids, post_groups)

    if not DRY_RUN:
        risposta = input("Confermi l'applicazione delle modifiche? [s/N] ").strip().lower()
        if risposta == 's':
            apply_changes(conn, dup_ids, updates, post_ids)
        else:
            print("Annullato.")

    conn.close()


if __name__ == '__main__':
    main()
