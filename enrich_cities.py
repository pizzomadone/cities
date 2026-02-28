"""
Arricchisce cities.db con popolazione e altitudine.

  Popolazione  →  GeoNames cities500.txt  (match per coordinate + country)
  Altitudine   →  srtm.py                 (tile SRTM NASA, ~90 m risoluzione)
                  fallback: campo 'dem' di GeoNames (GTOPO30, ~1 km)

Uso:
    python enrich_cities.py [opzioni]

    --db        cities.db       path al database SQLite
    --geonames  cities500.txt   path al dump GeoNames (scaricato se assente)
    --no-srtm                   salta srtm.py (usa solo il dem di GeoNames)
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
GEONAMES_ZIP = 'cities500.zip'
GEONAMES_TXT = 'cities500.txt'

# Raggio di ricerca: quanto lontano cercare un punto GeoNames.
MAX_MATCH_KM = 50

# Soglia "stesso luogo": entro questa distanza il punto GeoNames è
# considerato lo stesso insediamento → popolazione e DEM sono validi.
# Oltre questa soglia l'entry potrebbe essere un fiume, un lago, una
# cima o qualsiasi POI non abitato: non gli assegniamo la popolazione
# né l'altitudine della città più vicina (che sarebbe fuorviante).
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


# ── Indice spaziale GeoNames ───────────────────────────────────────
#
# Struttura:  { country_code: { (int_lat, int_lon): [(lat, lon, pop, dem)] } }
#
# La cella (int_lat, int_lon) copre un grado quadrato (~111 km lato).
# Il matching cerca nelle 9 celle adiacenti (±1°), garantendo copertura
# fino a ~157 km dalla cella centrale — ben oltre MAX_MATCH_KM=50 km.

def load_geonames(txt_path):
    print(f'Caricamento {txt_path} …')
    index = {}   # cc → { (ilat, ilon): [(lat, lon, pop, dem)] }
    n = 0
    with open(txt_path, encoding='utf-8') as f:
        for line in f:
            fields = line.rstrip('\n').split('\t')
            if len(fields) < 17:
                continue
            if fields[6] != 'P':        # solo centri abitati
                continue
            try:
                lat = float(fields[4])
                lon = float(fields[5])
                pop = int(fields[14]) if fields[14] else 0
                dem = int(fields[16]) if fields[16] else None
                cc  = fields[8].upper()
            except (ValueError, IndexError):
                continue

            cell = (int(lat), int(lon))
            cc_idx = index.setdefault(cc, {})
            cc_idx.setdefault(cell, []).append((lat, lon, pop, dem))
            n += 1

    print(f'  {n:,} centri abitati  ({len(index)} paesi)')
    return index


def find_match(index, lat, lon, cc):
    """
    Restituisce (pop, dem) del punto GeoNames più vicino nello stesso paese,
    entro MAX_MATCH_KM km. Ritorna None se non trovato.

    Sia pop che dem vengono restituiti come None se la distanza supera
    MAX_SAME_PLACE_KM: oltre quella soglia il punto GeoNames non è lo stesso
    insediamento, quindi la sua popolazione e il suo DEM non sono valori
    applicabili all'entry corrente (che potrebbe essere un fiume, un lago,
    una vetta, ecc.).
    SRTM, essendo calcolato sulle coordinate esatte, rimane invece sempre
    valido indipendentemente dalla distanza dal punto GeoNames.
    """
    cc_idx = index.get(cc)
    if not cc_idx:
        return None

    ilat, ilon = int(lat), int(lon)
    best_dist = MAX_MATCH_KM + 1
    best = None

    for dlat in (-1, 0, 1):
        for dlon in (-1, 0, 1):
            for g_lat, g_lon, pop, dem in cc_idx.get((ilat + dlat, ilon + dlon), ()):
                d = haversine(lat, lon, g_lat, g_lon)
                if d < best_dist:
                    best_dist = d
                    best = (pop, dem, d)

    if best is None:
        return None

    pop, dem, dist = best

    # Oltre MAX_SAME_PLACE_KM il punto GeoNames non coincide con la nostra
    # entry: azzeriamo i valori derivati da quel punto specifico.
    if dist > MAX_SAME_PLACE_KM:
        pop = None
        dem = None

    return pop, dem


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
    if changed:
        conn.commit()


# ── Core ──────────────────────────────────────────────────────────

def run(db_path, geonames_txt, use_srtm, dry_run):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    ensure_columns(conn)

    geonames = load_geonames(geonames_txt)

    # Carica srtm se disponibile
    srtm_data = None
    if use_srtm:
        try:
            import srtm
            srtm_data = srtm.get_data()
            print('srtm.py pronto (tile scaricati on-demand).')
        except ImportError:
            print('ATTENZIONE: srtm.py non installato — altitudine da dem GeoNames.')
            print('  Installa con: pip install srtm.py')

    rows = conn.execute(
        'SELECT cityid, latitude, longitude, countrycode FROM cities '
        'WHERE latitude IS NOT NULL AND longitude IS NOT NULL'
    ).fetchall()

    total = len(rows)
    print(f'\nCittà con coordinate: {total:,}')
    if dry_run:
        print('[dry-run] Nessuna scrittura nel DB.\n')

    matched_pop  = 0
    matched_elev = 0
    updates      = []
    t0 = time.time()

    for i, row in enumerate(rows, 1):
        cid = row['cityid']
        lat = row['latitude']
        lon = row['longitude']
        cc  = (row['countrycode'] or '').upper()

        pop  = None
        elev = None

        # 1. GeoNames → popolazione + dem come fallback altitudine
        match = find_match(geonames, lat, lon, cc)
        if match:
            g_pop, g_dem = match
            if g_pop and g_pop > 0:
                pop = g_pop
                matched_pop += 1
            elev = g_dem  # fallback, può rimanere None

        # 2. srtm.py → altitudine precisa (sovrascrive dem GeoNames)
        if srtm_data:
            s = srtm_data.get_elevation(lat, lon)
            if s is not None:
                elev = s
                matched_elev += 1

        updates.append((pop, elev, cid))

        if i % BATCH_SIZE == 0 or i == total:
            if not dry_run:
                conn.executemany(
                    'UPDATE cities SET population=?, elevation_m=? WHERE cityid=?',
                    updates
                )
                conn.commit()
            updates = []
            elapsed = time.time() - t0
            speed = i / elapsed if elapsed > 0 else 0
            eta   = (total - i) / speed if speed > 0 else 0
            print(
                f'  {i:>8,}/{total:,}  '
                f'pop:{matched_pop:,}  elev:{matched_elev:,}  '
                f'{speed:.0f} città/s  ETA {eta:.0f}s',
                end='\r'
            )

    print()
    elapsed = time.time() - t0
    print(f'\nCompletato in {elapsed:.1f}s')
    print(f'  Popolazione trovata : {matched_pop:,} / {total:,} '
          f'({matched_pop/total*100:.1f}%)')
    print(f'  Altitudine trovata  : {matched_elev:,} / {total:,} '
          f'({matched_elev/total*100:.1f}%)')

    conn.close()


# ── Entry point ───────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='Arricchisce cities.db con popolazione (GeoNames) e altitudine (srtm.py).'
    )
    parser.add_argument('--db',       default='cities.db',  help='Path al DB SQLite')
    parser.add_argument('--geonames', default=GEONAMES_TXT, help='Path a cities500.txt')
    parser.add_argument('--no-srtm',  action='store_true',  help='Usa solo dem GeoNames')
    parser.add_argument('--dry-run',  action='store_true',  help='Non scrive nel DB')
    args = parser.parse_args()

    # Scarica e/o estrae GeoNames se assente
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
