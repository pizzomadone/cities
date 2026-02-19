import unicodedata
import re
import math


def slugify(text):
    if not text:
        return ''
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    return re.sub(r'[-\s]+', '-', text)


def haversine(lat1, lon1, lat2, lon2):
    """Distanza in km tra due coordinate geografiche (formula Haversine)."""
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return round(2 * R * math.asin(math.sqrt(a)), 1)


def to_dms(deg, pos_label, neg_label):
    """Converte gradi decimali in formato DMS (Gradi°Minuti'Secondi\")."""
    d = int(abs(deg))
    m = int((abs(deg) - d) * 60)
    s = round(((abs(deg) - d) * 60 - m) * 60, 2)
    card = pos_label if deg >= 0 else neg_label
    return f"{d}°{m}'{s}\" {card}"


def format_coords(lat, lon):
    """Restituisce una tupla (lat_dms, lon_dms) leggibile."""
    return to_dms(lat, 'N', 'S'), to_dms(lon, 'E', 'W')


def paginate(total, page, per_page):
    """Calcola metadati di paginazione."""
    total_pages = max(1, math.ceil(total / per_page))
    return {
        'page': page,
        'per_page': per_page,
        'total': total,
        'total_pages': total_pages,
        'has_prev': page > 1,
        'has_next': page < total_pages,
    }
