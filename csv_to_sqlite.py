"""
Importa worldcities-geo.csv in cities.db (SQLite).
Uso: python csv_to_sqlite.py [percorso_csv] [percorso_db]

Default:
  CSV → worldcities-geo.csv
  DB  → cities.db
"""

import sqlite3
import csv
import unicodedata
import re
import sys
import time


CSV_PATH = sys.argv[1] if len(sys.argv) > 1 else 'worldcities-geo.csv'
DB_PATH  = sys.argv[2] if len(sys.argv) > 2 else 'cities.db'
BATCH    = 5_000


# ── Helpers ───────────────────────────────────────────────────────

def slugify(text):
    if not text:
        return ''
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    return re.sub(r'[-\s]+', '-', text)


def parse_float(val):
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


# ── Schema ────────────────────────────────────────────────────────

def init_db(conn):
    conn.execute('''
        CREATE TABLE IF NOT EXISTS cities (
            cityid        TEXT PRIMARY KEY,
            regionid      TEXT,
            countryid     TEXT,
            countryname   TEXT,
            countrycode   TEXT,
            continent     TEXT,
            stateprovince TEXT,
            cityname      TEXT,
            latitude      REAL,
            longitude     REAL,
            slug_city     TEXT,
            slug_country  TEXT,
            slug_region   TEXT
        )
    ''')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_country ON cities(slug_country)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_region  ON cities(slug_country, slug_region)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_city    ON cities(slug_country, slug_region, slug_city)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_coords  ON cities(latitude, longitude)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_cont    ON cities(continent)')
    conn.commit()


# ── Importazione ──────────────────────────────────────────────────

def run():
    print(f'CSV sorgente : {CSV_PATH}')
    print(f'Database     : {DB_PATH}')

    conn = sqlite3.connect(DB_PATH)
    init_db(conn)

    start   = time.time()
    batch   = []
    total   = 0
    skipped = 0

    INSERT = '''
        INSERT OR IGNORE INTO cities VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
    '''

    with open(CSV_PATH, encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for r in reader:
            # Riga senza cityid → saltiamo
            if not r.get('cityid', '').strip():
                skipped += 1
                continue

            batch.append((
                r['cityid'].strip(),
                r['regionid'].strip(),
                r['countryid'].strip(),
                r['countryname'].strip(),
                r['countrycode'].strip(),
                r['Continent'].strip(),
                r['StateProvinceName'].strip(),
                r['cityname'].strip(),
                parse_float(r['latitude']),
                parse_float(r['longitude']),
                slugify(r['cityname']),
                slugify(r['countryname']),
                slugify(r['StateProvinceName']),
            ))

            if len(batch) >= BATCH:
                conn.executemany(INSERT, batch)
                conn.commit()
                total += len(batch)
                batch = []
                elapsed = time.time() - start
                print(f'  {total:>8,} righe importate  ({elapsed:.1f}s)', end='\r')

    # Ultimo batch
    if batch:
        conn.executemany(INSERT, batch)
        conn.commit()
        total += len(batch)

    conn.close()
    elapsed = time.time() - start
    print(f'\nImportazione completata: {total:,} righe in {elapsed:.1f}s  ({skipped} skipped)')


if __name__ == '__main__':
    run()
