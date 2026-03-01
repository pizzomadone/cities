"""
Arricchisce cities.db con popolazione e altitudine.

  Popolazione  →  GeoNames cities500.txt  (matching INVERSO: per ogni città
                  GeoNames trova l'entry DB più vicina → quella e solo quella
                  diventa un centro abitato; musei, fiumi, ecc. rimangono POI)
  Altitudine   →  srtm.py  (tile SRTM NASA, ~90 m risoluzione, coordinate esatte)

Uso:
    python enrich_cities.py [opzioni]

    --db        cities.db       path al database SQLite
    --geonames  cities500.txt   path al dump GeoNames (scaricato se assente)
    --no-srtm                   salta SRTM: ricalcola solo popolazione/flag,
                                lascia elevation_m intatta
    --dry-run                   stampa statistiche senza scrivere nel DB

Dipendenze:
    pip install srtm.py

GeoNames (scaricato automaticamente se assente):
    https://download.geonames.org/export/dump/cities500.zip
"""

import argparse
import math
import os
import sqlite3
import sys
import time
import urllib.request
import zipfile

GEONAMES_URL = 'https://download.geonames.org/export/dump/cities500.zip'
GEONAMES_TXT = 'cities500.txt'

# Distanza massima entro cui un'entry DB può essere abbinata a una città GeoNames.
# Oltre questa soglia l'entry è trattata come POI.
MAX_SAME_PLACE_KM = 10

BATCH_SIZE = 2_000


# ── Geometria ─────────────────────────────────────────────────────

def haversine(lat1, lon1, lat2, lon2):
    R = 6_371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# ── Download ──────────────────────────────────────────────────────

def _progress_hook(count, block_size, total):
    done = count * block_size
    if total > 0:
        pct = min(done / total * 100, 100)
        mb  = done / 1_048_576
        sys.stdout.write(f'\r  {mb:.1f} MB  ({pct:.0f}%)')
        sys.stdout.flush()


def download_geonames(zip_path):
    print(f'Download {GEONAMES_URL}')
    urllib.request.urlretrieve(GEONAMES_URL, zip_path, _progress_hook)
    print()


# ── Indice spaziale delle entry DB ────────────────────────────────
#
# Struttura: { country_code: { (int_lat, int_lon): [(lat, lon, cityid)] } }
#
# Usato per il matching INVERSO: dato un punto GeoNames, trova l'entry
# DB più vicina nello stesso paese entro MAX_SAME_PLACE_KM.

def build_db_index(rows):
    index = {}
    for row in rows:
        lat = row['latitude']
        lon = row['longitude']
        cid = row['cityid']
        cc  = (row['countrycode'] or '').upper()
        cell = (int(lat), int(lon))
        cc_idx = index.setdefault(cc, {})
        cc_idx.setdefault(cell, []).append((lat, lon, cid))
    return index


def find_db_entry(db_index, g_lat, g_lon, g_cc):
    """
    Dato un punto GeoNames (lat, lon, country), restituisce (cityid, dist_km)
    dell'entry DB più vicina entro MAX_SAME_PLACE_KM, oppure None.
    """
    cc_idx = db_index.get(g_cc)
    if not cc_idx:
        return None

    ilat, ilon = int(g_lat), int(g_lon)
    best_dist = MAX_SAME_PLACE_KM + 1
    best_cid  = None

    for dlat in (-1, 0, 1):
        for dlon in (-1, 0, 1):
            for lat, lon, cid in cc_idx.get((ilat + dlat, ilon + dlon), ()):
                d = haversine(g_lat, g_lon, lat, lon)
                if d < best_dist:
                    best_dist = d
                    best_cid  = cid

    return (best_cid, best_dist) if best_cid is not None else None


# ── DB helpers ────────────────────────────────────────────────────

def ensure_columns(conn):
    existing = {row[1] for row in conn.execute('PRAGMA table_info(cities)')}
    changed = False
    if 'population' not in existing:
        conn.execute('ALTER TABLE cities ADD COLUMN population INTEGER')
        print('Colonna population aggiunta.')
        changed = True
    if 'elevation_m' not in existing:
        conn.execute('ALTER TABLE cities ADD COLUMN elevation_m INTEGER')
        print('Colonna elevation_m aggiunta.')
        changed = True
    if 'is_populated_place' not in existing:
        conn.execute('ALTER TABLE cities ADD COLUMN is_populated_place INTEGER DEFAULT 0')
        print('Colonna is_populated_place aggiunta.')
        changed = True
    if changed:
        conn.commit()


def _fmt_duration(seconds):
    """Formatta una durata in secondi come stringa leggibile (es. '2h 34m 12s')."""
    seconds = int(seconds)
    h, remainder = divmod(seconds, 3600)
    m, s = divmod(remainder, 60)
    if h:
        return f'{h}h {m:02d}m {s:02d}s'
    if m:
        return f'{m}m {s:02d}s'
    return f'{s}s'


# ── Fase 1: Popolazione + is_populated_place ──────────────────────

def run_population(conn, geonames_txt, dry_run):
    """
    Matching INVERSO: per ogni città in cities500.txt trova l'entry DB
    più vicina entro MAX_SAME_PLACE_KM. Quella entry e solo quella riceve
    is_populated_place=1 e la popolazione reale. Tutte le altre vengono
    resettate a population=NULL, is_populated_place=0.

    In questo modo musei, fiumi e qualsiasi POI vicino a una città reale
    non ereditano mai la popolazione della città.
    """
    t0 = time.time()

    rows = conn.execute(
        'SELECT cityid, latitude, longitude, countrycode FROM cities '
        'WHERE latitude IS NOT NULL AND longitude IS NOT NULL'
    ).fetchall()
    total_db = len(rows)
    print(f'Entry DB con coordinate: {total_db:,}')

    print('Costruzione indice spaziale DB …')
    db_index = build_db_index(rows)

    # city_matches: cityid → (population, dist_km)
    # Se più città GeoNames puntano alla stessa entry DB, vince la più vicina.
    city_matches = {}
    n_geonames   = 0

    print(f'Matching GeoNames → DB (soglia {MAX_SAME_PLACE_KM} km) …')
    with open(geonames_txt, encoding='utf-8') as f:
        for line in f:
            fields = line.rstrip('\n').split('\t')
            if len(fields) < 17 or fields[6] != 'P':
                continue
            try:
                g_lat = float(fields[4])
                g_lon = float(fields[5])
                g_pop = int(fields[14]) if fields[14] else 0
                g_cc  = fields[8].upper()
            except (ValueError, IndexError):
                continue

            n_geonames += 1
            result = find_db_entry(db_index, g_lat, g_lon, g_cc)
            if result:
                cid, dist = result
                if cid not in city_matches or dist < city_matches[cid][1]:
                    city_matches[cid] = (g_pop, dist)

    n_cities   = len(city_matches)
    n_with_pop = sum(1 for pop, _ in city_matches.values() if pop and pop > 0)
    print(f'  {n_geonames:,} città GeoNames elaborate')
    print(f'  {n_cities:,} entry DB identificate come centri abitati')
    print(f'  {n_with_pop:,} con popolazione > 0')

    if dry_run:
        print('[dry-run] Nessuna scrittura.\n')
        return

    # Reset globale: tutti i record tornano a POI
    print('Reset population e is_populated_place …')
    conn.execute('UPDATE cities SET population = NULL, is_populated_place = 0')
    conn.commit()

    # Scrittura dei centri abitati identificati
    print('Scrittura centri abitati …')
    batch = []
    for cid, (pop, _) in city_matches.items():
        batch.append((pop if pop and pop > 0 else None, cid))
        if len(batch) >= BATCH_SIZE:
            conn.executemany(
                'UPDATE cities SET population = ?, is_populated_place = 1 WHERE cityid = ?',
                batch
            )
            conn.commit()
            batch = []
    if batch:
        conn.executemany(
            'UPDATE cities SET population = ?, is_populated_place = 1 WHERE cityid = ?',
            batch
        )
        conn.commit()

    elapsed = time.time() - t0
    print(f'Popolazione completata in {_fmt_duration(elapsed)}')
    print(f'  Centri abitati : {n_cities:,} / {total_db:,} ({n_cities/total_db*100:.1f}%)')
    print(f'  Con popolazione: {n_with_pop:,} / {n_cities:,} ({n_with_pop/n_cities*100:.1f}% dei centri abitati)')


# ── Fase 2: Altitudine SRTM ───────────────────────────────────────

def run_elevation(conn, dry_run):
    """
    Calcola l'altitudine per ogni entry con coordinate usando SRTM
    (tile NASA, ~90 m risoluzione). Valido per qualsiasi feature geografica:
    città, fiumi, laghi, cime, musei, ecc. — usa le coordinate esatte.
    """
    try:
        import srtm
    except ImportError:
        print('ATTENZIONE: srtm.py non installato — altitudine saltata.')
        print('  Installa con: pip install srtm.py')
        return

    srtm_data = srtm.get_data()
    print('srtm.py pronto.')

    rows = conn.execute(
        'SELECT cityid, latitude, longitude FROM cities '
        'WHERE latitude IS NOT NULL AND longitude IS NOT NULL'
    ).fetchall()
    total = len(rows)
    print(f'Calcolo altitudine per {total:,} entry …')

    t0      = time.time()
    found   = 0
    updates = []

    for i, row in enumerate(rows, 1):
        elev = srtm_data.get_elevation(row['latitude'], row['longitude'])
        if elev is not None:
            found += 1
        updates.append((elev, row['cityid']))

        if i % BATCH_SIZE == 0 or i == total:
            if not dry_run:
                conn.executemany(
                    'UPDATE cities SET elevation_m = ? WHERE cityid = ?',
                    updates
                )
                conn.commit()
            updates = []
            elapsed = time.time() - t0
            speed   = i / elapsed if elapsed > 0 else 0
            eta     = (total - i) / speed if speed > 0 else 0
            print(
                f'  {i:>8,}/{total:,}  trovate:{found:,}  '
                f'{speed:.0f} entry/s  '
                f'trascorso {_fmt_duration(elapsed)}  '
                f'ETA {_fmt_duration(eta)}',
                end='\r'
            )

    print()
    elapsed = time.time() - t0
    print(f'Altitudine completata in {_fmt_duration(elapsed)}')
    print(f'  Altitudine trovata: {found:,} / {total:,} ({found/total*100:.1f}%)')


# ── Entry point ───────────────────────────────────────────────────

def run(db_path, geonames_txt, use_srtm, dry_run):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    ensure_columns(conn)

    print('\n=== FASE 1: Popolazione ===')
    run_population(conn, geonames_txt, dry_run)

    if use_srtm:
        print('\n=== FASE 2: Altitudine SRTM ===')
        run_elevation(conn, dry_run)
    else:
        print('\n[--no-srtm] Altitudine esistente lasciata invariata.')

    conn.close()


def main():
    parser = argparse.ArgumentParser(
        description='Arricchisce cities.db con popolazione (GeoNames) e altitudine (SRTM).'
    )
    parser.add_argument('--db',       default='cities.db',  help='Path al DB SQLite')
    parser.add_argument('--geonames', default=GEONAMES_TXT, help='Path a cities500.txt')
    parser.add_argument('--no-srtm',  action='store_true',
                        help='Salta SRTM: ricalcola solo popolazione/flag, '
                             'elevation_m rimane invariata')
    parser.add_argument('--dry-run',  action='store_true',  help='Non scrive nel DB')
    args = parser.parse_args()

    if not os.path.exists(args.geonames):
        zip_path = os.path.splitext(args.geonames)[0] + '.zip'
        if not os.path.exists(zip_path):
            download_geonames(zip_path)
        print(f'Estrazione {zip_path} …')
        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall(os.path.dirname(args.geonames) or '.')
        print(f'  → {args.geonames}')

    run(args.db, args.geonames, not args.no_srtm, args.dry_run)


if __name__ == '__main__':
    main()
