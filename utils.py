import unicodedata
import re
import math
from datetime import datetime


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


# ── Mappe statiche ISO 3166-1 ──────────────────────────────────────

TLD_MAP = {
    'AF': '.af', 'AX': '.ax', 'AL': '.al', 'DZ': '.dz', 'AS': '.as',
    'AD': '.ad', 'AO': '.ao', 'AI': '.ai', 'AG': '.ag', 'AR': '.ar',
    'AM': '.am', 'AW': '.aw', 'AU': '.au', 'AT': '.at', 'AZ': '.az',
    'BS': '.bs', 'BH': '.bh', 'BD': '.bd', 'BB': '.bb', 'BY': '.by',
    'BE': '.be', 'BZ': '.bz', 'BJ': '.bj', 'BM': '.bm', 'BT': '.bt',
    'BO': '.bo', 'BA': '.ba', 'BW': '.bw', 'BR': '.br', 'IO': '.io',
    'BN': '.bn', 'BG': '.bg', 'BF': '.bf', 'BI': '.bi', 'KH': '.kh',
    'CM': '.cm', 'CA': '.ca', 'CV': '.cv', 'KY': '.ky', 'CF': '.cf',
    'TD': '.td', 'CL': '.cl', 'CN': '.cn', 'CX': '.cx', 'CC': '.cc',
    'CO': '.co', 'KM': '.km', 'CG': '.cg', 'CD': '.cd', 'CK': '.ck',
    'CR': '.cr', 'CI': '.ci', 'HR': '.hr', 'CU': '.cu', 'CY': '.cy',
    'CZ': '.cz', 'DK': '.dk', 'DJ': '.dj', 'DM': '.dm', 'DO': '.do',
    'EC': '.ec', 'EG': '.eg', 'SV': '.sv', 'GQ': '.gq', 'ER': '.er',
    'EE': '.ee', 'ET': '.et', 'FK': '.fk', 'FO': '.fo', 'FJ': '.fj',
    'FI': '.fi', 'FR': '.fr', 'GF': '.gf', 'PF': '.pf', 'GA': '.ga',
    'GM': '.gm', 'GE': '.ge', 'DE': '.de', 'GH': '.gh', 'GI': '.gi',
    'GR': '.gr', 'GL': '.gl', 'GD': '.gd', 'GP': '.gp', 'GU': '.gu',
    'GT': '.gt', 'GG': '.gg', 'GN': '.gn', 'GW': '.gw', 'GY': '.gy',
    'HT': '.ht', 'VA': '.va', 'HN': '.hn', 'HK': '.hk', 'HU': '.hu',
    'IS': '.is', 'IN': '.in', 'ID': '.id', 'IR': '.ir', 'IQ': '.iq',
    'IE': '.ie', 'IM': '.im', 'IL': '.il', 'IT': '.it', 'JM': '.jm',
    'JP': '.jp', 'JE': '.je', 'JO': '.jo', 'KZ': '.kz', 'KE': '.ke',
    'KI': '.ki', 'KP': '.kp', 'KR': '.kr', 'KW': '.kw', 'KG': '.kg',
    'LA': '.la', 'LV': '.lv', 'LB': '.lb', 'LS': '.ls', 'LR': '.lr',
    'LY': '.ly', 'LI': '.li', 'LT': '.lt', 'LU': '.lu', 'MO': '.mo',
    'MK': '.mk', 'MG': '.mg', 'MW': '.mw', 'MY': '.my', 'MV': '.mv',
    'ML': '.ml', 'MT': '.mt', 'MH': '.mh', 'MQ': '.mq', 'MR': '.mr',
    'MU': '.mu', 'YT': '.yt', 'MX': '.mx', 'FM': '.fm', 'MD': '.md',
    'MC': '.mc', 'MN': '.mn', 'ME': '.me', 'MS': '.ms', 'MA': '.ma',
    'MZ': '.mz', 'MM': '.mm', 'NA': '.na', 'NR': '.nr', 'NP': '.np',
    'NL': '.nl', 'NC': '.nc', 'NZ': '.nz', 'NI': '.ni', 'NE': '.ne',
    'NG': '.ng', 'NU': '.nu', 'NF': '.nf', 'MP': '.mp', 'NO': '.no',
    'OM': '.om', 'PK': '.pk', 'PW': '.pw', 'PS': '.ps', 'PA': '.pa',
    'PG': '.pg', 'PY': '.py', 'PE': '.pe', 'PH': '.ph', 'PN': '.pn',
    'PL': '.pl', 'PT': '.pt', 'PR': '.pr', 'QA': '.qa', 'RE': '.re',
    'RO': '.ro', 'RU': '.ru', 'RW': '.rw', 'BL': '.bl', 'SH': '.sh',
    'KN': '.kn', 'LC': '.lc', 'MF': '.mf', 'PM': '.pm', 'VC': '.vc',
    'WS': '.ws', 'SM': '.sm', 'ST': '.st', 'SA': '.sa', 'SN': '.sn',
    'RS': '.rs', 'SC': '.sc', 'SL': '.sl', 'SG': '.sg', 'SK': '.sk',
    'SI': '.si', 'SB': '.sb', 'SO': '.so', 'ZA': '.za', 'GS': '.gs',
    'ES': '.es', 'LK': '.lk', 'SD': '.sd', 'SR': '.sr', 'SJ': '.sj',
    'SZ': '.sz', 'SE': '.se', 'CH': '.ch', 'SY': '.sy', 'TW': '.tw',
    'TJ': '.tj', 'TZ': '.tz', 'TH': '.th', 'TL': '.tl', 'TG': '.tg',
    'TK': '.tk', 'TO': '.to', 'TT': '.tt', 'TN': '.tn', 'TR': '.tr',
    'TM': '.tm', 'TC': '.tc', 'TV': '.tv', 'UG': '.ug', 'UA': '.ua',
    'AE': '.ae', 'GB': '.uk', 'US': '.us', 'UY': '.uy', 'UZ': '.uz',
    'VU': '.vu', 'VE': '.ve', 'VN': '.vn', 'VG': '.vg', 'VI': '.vi',
    'WF': '.wf', 'EH': '.eh', 'YE': '.ye', 'ZM': '.zm', 'ZW': '.zw',
    'XK': '.xk', 'SS': '.ss', 'CW': '.cw', 'SX': '.sx', 'BQ': '.bq',
}

PHONE_MAP = {
    'AF': '+93',  'AL': '+355', 'DZ': '+213', 'AS': '+1',   'AD': '+376',
    'AO': '+244', 'AI': '+1',   'AG': '+1',   'AR': '+54',  'AM': '+374',
    'AW': '+297', 'AU': '+61',  'AT': '+43',  'AZ': '+994', 'BS': '+1',
    'BH': '+973', 'BD': '+880', 'BB': '+1',   'BY': '+375', 'BE': '+32',
    'BZ': '+501', 'BJ': '+229', 'BM': '+1',   'BT': '+975', 'BO': '+591',
    'BA': '+387', 'BW': '+267', 'BR': '+55',  'IO': '+246', 'BN': '+673',
    'BG': '+359', 'BF': '+226', 'BI': '+257', 'KH': '+855', 'CM': '+237',
    'CA': '+1',   'CV': '+238', 'KY': '+1',   'CF': '+236', 'TD': '+235',
    'CL': '+56',  'CN': '+86',  'CX': '+61',  'CC': '+61',  'CO': '+57',
    'KM': '+269', 'CG': '+242', 'CD': '+243', 'CK': '+682', 'CR': '+506',
    'CI': '+225', 'HR': '+385', 'CU': '+53',  'CY': '+357', 'CZ': '+420',
    'DK': '+45',  'DJ': '+253', 'DM': '+1',   'DO': '+1',   'EC': '+593',
    'EG': '+20',  'SV': '+503', 'GQ': '+240', 'ER': '+291', 'EE': '+372',
    'ET': '+251', 'FK': '+500', 'FO': '+298', 'FJ': '+679', 'FI': '+358',
    'FR': '+33',  'GF': '+594', 'PF': '+689', 'GA': '+241', 'GM': '+220',
    'GE': '+995', 'DE': '+49',  'GH': '+233', 'GI': '+350', 'GR': '+30',
    'GL': '+299', 'GD': '+1',   'GP': '+590', 'GU': '+1',   'GT': '+502',
    'GN': '+224', 'GW': '+245', 'GY': '+592', 'HT': '+509', 'VA': '+379',
    'HN': '+504', 'HK': '+852', 'HU': '+36',  'IS': '+354', 'IN': '+91',
    'ID': '+62',  'IR': '+98',  'IQ': '+964', 'IE': '+353', 'IL': '+972',
    'IT': '+39',  'JM': '+1',   'JP': '+81',  'JO': '+962', 'KZ': '+7',
    'KE': '+254', 'KI': '+686', 'KP': '+850', 'KR': '+82',  'KW': '+965',
    'KG': '+996', 'LA': '+856', 'LV': '+371', 'LB': '+961', 'LS': '+266',
    'LR': '+231', 'LY': '+218', 'LI': '+423', 'LT': '+370', 'LU': '+352',
    'MO': '+853', 'MK': '+389', 'MG': '+261', 'MW': '+265', 'MY': '+60',
    'MV': '+960', 'ML': '+223', 'MT': '+356', 'MH': '+692', 'MQ': '+596',
    'MR': '+222', 'MU': '+230', 'YT': '+262', 'MX': '+52',  'FM': '+691',
    'MD': '+373', 'MC': '+377', 'MN': '+976', 'ME': '+382', 'MS': '+1',
    'MA': '+212', 'MZ': '+258', 'MM': '+95',  'NA': '+264', 'NR': '+674',
    'NP': '+977', 'NL': '+31',  'NC': '+687', 'NZ': '+64',  'NI': '+505',
    'NE': '+227', 'NG': '+234', 'NU': '+683', 'NF': '+672', 'MP': '+1',
    'NO': '+47',  'OM': '+968', 'PK': '+92',  'PW': '+680', 'PS': '+970',
    'PA': '+507', 'PG': '+675', 'PY': '+595', 'PE': '+51',  'PH': '+63',
    'PN': '+64',  'PL': '+48',  'PT': '+351', 'PR': '+1',   'QA': '+974',
    'RE': '+262', 'RO': '+40',  'RU': '+7',   'RW': '+250', 'KN': '+1',
    'LC': '+1',   'PM': '+508', 'VC': '+1',   'WS': '+685', 'SM': '+378',
    'ST': '+239', 'SA': '+966', 'SN': '+221', 'RS': '+381', 'SC': '+248',
    'SL': '+232', 'SG': '+65',  'SK': '+421', 'SI': '+386', 'SB': '+677',
    'SO': '+252', 'ZA': '+27',  'SS': '+211', 'ES': '+34',  'LK': '+94',
    'SD': '+249', 'SR': '+597', 'SZ': '+268', 'SE': '+46',  'CH': '+41',
    'SY': '+963', 'TW': '+886', 'TJ': '+992', 'TZ': '+255', 'TH': '+66',
    'TL': '+670', 'TG': '+228', 'TK': '+690', 'TO': '+676', 'TT': '+1',
    'TN': '+216', 'TR': '+90',  'TM': '+993', 'TC': '+1',   'TV': '+688',
    'UG': '+256', 'UA': '+380', 'AE': '+971', 'GB': '+44',  'US': '+1',
    'UY': '+598', 'UZ': '+998', 'VU': '+678', 'VE': '+58',  'VN': '+84',
    'VG': '+1',   'VI': '+1',   'WF': '+681', 'YE': '+967', 'ZM': '+260',
    'ZW': '+263', 'XK': '+383', 'CW': '+599', 'SX': '+1',
}


def country_flag(code):
    """Emoji bandiera da codice ISO 3166-1 alpha-2."""
    if not code or len(code) != 2:
        return ''
    code = code.upper()
    return chr(ord(code[0]) + 127397) + chr(ord(code[1]) + 127397)


def get_tld(code):
    """Restituisce il ccTLD per il codice paese (es. 'IT' → '.it')."""
    return TLD_MAP.get((code or '').upper(), '')


def get_phone_prefix(code):
    """Restituisce il prefisso telefonico internazionale (es. 'IT' → '+39')."""
    return PHONE_MAP.get((code or '').upper(), '')


def approx_timezone(lon):
    """
    Stima l'offset UTC in ore dalla longitudine.
    Restituisce (offset_int, label_str), es. (1, 'UTC+1').
    """
    offset = round(lon / 15)
    if offset == 0:
        label = 'UTC+0'
    elif offset > 0:
        label = f'UTC+{offset}'
    else:
        label = f'UTC{offset}'
    return offset, label


def get_hemisphere(lat, lon):
    """
    Restituisce (emisfero_NS, emisfero_EW), es. ('Northern', 'Eastern').
    """
    ns = 'Northern' if lat >= 0 else 'Southern'
    ew = 'Eastern' if lon >= 0 else 'Western'
    return ns, ew


def antipode(lat, lon):
    """
    Calcola il punto antipodale (opposto sulla Terra).
    Restituisce (anti_lat, anti_lon) arrotondati a 4 decimali.
    """
    anti_lat = round(-lat, 4)
    anti_lon = lon - 180 if lon >= 0 else lon + 180
    anti_lon = round(anti_lon, 4)
    return anti_lat, anti_lon


def distance_from_equator(lat):
    """Distanza approssimata dall'equatore in km (1° ≈ 111.32 km)."""
    return round(abs(lat) * 111.32)


def _fmt_time(h):
    hh = int(h)
    mm = int(round((h - hh) * 60))
    if mm >= 60:
        hh = (hh + 1) % 24
        mm = 0
    return f'{hh:02d}:{mm:02d}'


def _fmt_duration(hours):
    h = int(hours)
    m = int(round((hours - h) * 60))
    if m >= 60:
        h += 1
        m = 0
    return f'{h}h {m:02d}m'


def _sun_calc(lat, lon, N):
    """
    Core del calcolo alba/tramonto dato il giorno dell'anno N (1–365).
    Restituisce (rise_h, set_h, day_length_hours) oppure
    ('midnight_sun', …) o ('polar_night', …) come stringa speciale nel primo valore.
    """
    decl = 23.45 * math.sin(math.radians(360 / 365 * (N - 81)))
    cos_H_num = (math.cos(math.radians(90.833)) -
                 math.sin(math.radians(lat)) * math.sin(math.radians(decl)))
    cos_H_den = (math.cos(math.radians(lat)) * math.cos(math.radians(decl)))
    if cos_H_den == 0:
        return 'na', None, None
    cos_H = cos_H_num / cos_H_den
    if cos_H < -1:
        return 'midnight_sun', None, None
    if cos_H > 1:
        return 'polar_night', None, None
    H = math.degrees(math.acos(cos_H))
    B = math.radians(360 / 365 * (N - 81))
    EoT = 9.87 * math.sin(2 * B) - 7.53 * math.cos(B) - 1.5 * math.sin(B)
    solar_noon = 12 - lon / 15 - EoT / 60
    H_hours = H / 15
    return (solar_noon - H_hours) % 24, (solar_noon + H_hours) % 24, 2 * H_hours


def sunrise_sunset(lat, lon):
    """
    Calcola alba e tramonto approssimati (UTC) per oggi.
    Restituisce (sunrise_str, sunset_str, day_length_str, date_str).
    """
    today = datetime.utcnow()
    N = today.timetuple().tm_yday
    date_str = today.strftime('%B %d, %Y')
    rise, sset, length = _sun_calc(lat, lon, N)
    if rise == 'midnight_sun':
        return 'Midnight Sun', 'Midnight Sun', '24h 00m', date_str
    if rise == 'polar_night':
        return 'Polar Night', 'Polar Night', '0h 00m', date_str
    if rise == 'na':
        return 'N/A', 'N/A', 'N/A', date_str
    return _fmt_time(rise) + ' UTC', _fmt_time(sset) + ' UTC', _fmt_duration(length), date_str


def sunrise_sunset_for_date(lat, lon, year, month, day):
    """
    Calcola alba e tramonto per una data specifica.
    Restituisce (sunrise_str, sunset_str, day_length_str) senza ' UTC' suffix.
    """
    from datetime import date as _date
    N = _date(year, month, day).timetuple().tm_yday
    rise, sset, length = _sun_calc(lat, lon, N)
    if rise == 'midnight_sun':
        return '☀️ all day', '—', '24h 00m'
    if rise == 'polar_night':
        return '—', '🌑 all day', '0h 00m'
    if rise == 'na':
        return 'N/A', 'N/A', 'N/A'
    return _fmt_time(rise), _fmt_time(sset), _fmt_duration(length)


def build_sun_calendar(lat, lon):
    """
    Costruisce il calendario alba/tramonto per 3 mesi: precedente, corrente, successivo.
    Restituisce una lista di 3 dict con chiavi: year, month, month_name, days.
    Ogni giorno: {day, dow, date_iso, sunrise, sunset, day_length, is_today}.
    """
    import calendar as _cal
    from datetime import date as _date

    today = datetime.utcnow().date()
    result = []

    for delta in (-1, 0, 1):
        m = today.month + delta
        y = today.year
        if m < 1:
            m += 12
            y -= 1
        elif m > 12:
            m -= 12
            y += 1
        _, days_in_month = _cal.monthrange(y, m)
        month_name = _date(y, m, 1).strftime('%B')
        days = []
        for d in range(1, days_in_month + 1):
            date_obj = _date(y, m, d)
            rise, sset, length = sunrise_sunset_for_date(lat, lon, y, m, d)
            days.append({
                'day':        d,
                'dow':        date_obj.strftime('%a'),
                'date_iso':   date_obj.isoformat(),
                'sunrise':    rise,
                'sunset':     sset,
                'day_length': length,
                'is_today':   date_obj == today,
                'moon':       _moon_emoji_for_date(y, m, d),
            })
        result.append({
            'year':       y,
            'month':      m,
            'month_name': month_name,
            'days':       days,
        })
    return result


# ---------------------------------------------------------------------------
# FASE LUNARE
# ---------------------------------------------------------------------------

def _moon_emoji_for_date(year, month, day):
    """Emoji della fase lunare per una data specifica (mezzogiorno UTC)."""
    SYNODIC = 29.53058867
    REF_NEW_MOON = datetime(2000, 1, 6, 18, 14)
    d = datetime(year, month, day, 12, 0)
    age = (d - REF_NEW_MOON).total_seconds() / 86400 % SYNODIC
    if age < 1.85:   return '🌑'
    elif age < 7.38: return '🌒'
    elif age < 9.22: return '🌓'
    elif age < 14.77: return '🌔'
    elif age < 16.61: return '🌕'
    elif age < 22.15: return '🌖'
    elif age < 23.99: return '🌗'
    else:             return '🌘'


def moon_phase():
    """Fase lunare di oggi. Restituisce dict con name, emoji, illumination, age, days_to_full, days_to_new."""
    SYNODIC = 29.53058867
    REF_NEW_MOON = datetime(2000, 1, 6, 18, 14)
    now = datetime.utcnow()
    age = (now - REF_NEW_MOON).total_seconds() / 86400 % SYNODIC
    illumination = round((1 - math.cos(math.radians(age / SYNODIC * 360))) / 2 * 100)
    if age < 1.85:    name, emoji = 'New Moon', '🌑'
    elif age < 7.38:  name, emoji = 'Waxing Crescent', '🌒'
    elif age < 9.22:  name, emoji = 'First Quarter', '🌓'
    elif age < 14.77: name, emoji = 'Waxing Gibbous', '🌔'
    elif age < 16.61: name, emoji = 'Full Moon', '🌕'
    elif age < 22.15: name, emoji = 'Waning Gibbous', '🌖'
    elif age < 23.99: name, emoji = 'Last Quarter', '🌗'
    else:             name, emoji = 'Waning Crescent', '🌘'
    days_to_full = (SYNODIC / 2 - age) % SYNODIC
    days_to_new  = (SYNODIC - age) % SYNODIC
    return {
        'age': round(age, 1),
        'name': name,
        'emoji': emoji,
        'illumination': illumination,
        'days_to_full': round(days_to_full, 1),
        'days_to_new':  round(days_to_new, 1),
    }


# ---------------------------------------------------------------------------
# GOLDEN HOUR & BLUE HOUR
# ---------------------------------------------------------------------------

def _time_at_elevation(lat, lon, elev_deg, N, morning=True):
    """Ora UTC (float) in cui il sole raggiunge elev_deg gradi di elevazione.
    morning=True per l'evento mattutino, False per quello serale.
    Restituisce None se il sole non raggiunge quell'elevazione."""
    decl = 23.45 * math.sin(math.radians(360 / 365 * (N - 81)))
    cos_H_num = (math.sin(math.radians(elev_deg)) -
                 math.sin(math.radians(lat)) * math.sin(math.radians(decl)))
    cos_H_den = (math.cos(math.radians(lat)) * math.cos(math.radians(decl)))
    if cos_H_den == 0:
        return None
    cos_H = cos_H_num / cos_H_den
    if abs(cos_H) > 1:
        return None
    H = math.degrees(math.acos(cos_H))
    B = math.radians(360 / 365 * (N - 81))
    EoT = 9.87 * math.sin(2 * B) - 7.53 * math.cos(B) - 1.5 * math.sin(B)
    solar_noon = 12 - lon / 15 - EoT / 60
    return (solar_noon - H / 15) % 24 if morning else (solar_noon + H / 15) % 24


def golden_hour(lat, lon):
    """Calcola golden hour e blue hour per oggi.
    Restituisce dict con chiavi golden_morning_*, golden_evening_*, blue_morning_*, blue_evening_*."""
    today = datetime.utcnow()
    N = today.timetuple().tm_yday

    def fmt(h):
        return _fmt_time(h) if h is not None else 'N/A'

    return {
        'golden_morning_start': fmt(_time_at_elevation(lat, lon, -0.833, N, morning=True)),
        'golden_morning_end':   fmt(_time_at_elevation(lat, lon, 6.0,   N, morning=True)),
        'golden_evening_start': fmt(_time_at_elevation(lat, lon, 6.0,   N, morning=False)),
        'golden_evening_end':   fmt(_time_at_elevation(lat, lon, -0.833, N, morning=False)),
        'blue_morning_start':   fmt(_time_at_elevation(lat, lon, -6.0,  N, morning=True)),
        'blue_morning_end':     fmt(_time_at_elevation(lat, lon, -4.0,  N, morning=True)),
        'blue_evening_start':   fmt(_time_at_elevation(lat, lon, -4.0,  N, morning=False)),
        'blue_evening_end':     fmt(_time_at_elevation(lat, lon, -6.0,  N, morning=False)),
    }


# ---------------------------------------------------------------------------
# STAGIONE CORRENTE
# ---------------------------------------------------------------------------

def current_season(lat):
    """Restituisce (name, emoji, hemisphere_note) per la stagione corrente."""
    month = datetime.utcnow().month
    if month in (3, 4, 5):
        n_name, n_emoji, s_name, s_emoji = 'Spring', '🌸', 'Autumn', '🍂'
        n_months, s_months = 'March – May', 'September – November'
    elif month in (6, 7, 8):
        n_name, n_emoji, s_name, s_emoji = 'Summer', '☀️', 'Winter', '❄️'
        n_months, s_months = 'June – August', 'December – February'
    elif month in (9, 10, 11):
        n_name, n_emoji, s_name, s_emoji = 'Autumn', '🍂', 'Spring', '🌸'
        n_months, s_months = 'September – November', 'March – May'
    else:
        n_name, n_emoji, s_name, s_emoji = 'Winter', '❄️', 'Summer', '☀️'
        n_months, s_months = 'December – February', 'June – August'

    if lat >= 0:
        return {'name': n_name, 'emoji': n_emoji, 'months': n_months,
                'hemisphere': 'Northern Hemisphere'}
    else:
        return {'name': s_name, 'emoji': s_emoji, 'months': s_months,
                'hemisphere': 'Southern Hemisphere'}


# ---------------------------------------------------------------------------
# TABELLA LUCE ANNUALE (12 mesi)
# ---------------------------------------------------------------------------

def annual_daylight(lat, lon):
    """Restituisce lista di 12 dict con dati alba/tramonto per il 15 di ogni mese."""
    year = datetime.utcnow().year
    result = []
    for m in range(1, 13):
        rise, sset, length = sunrise_sunset_for_date(lat, lon, year, m, 15)
        result.append({
            'month': m,
            'month_name': datetime(year, m, 15).strftime('%B'),
            'month_short': datetime(year, m, 15).strftime('%b'),
            'sunrise': rise,
            'sunset': sset,
            'day_length': length,
        })
    return result


# ---------------------------------------------------------------------------
# DATI PAESE (capitale, lingua, valuta)
# ---------------------------------------------------------------------------

COUNTRY_DATA = {
    'AF': {'capital': 'Kabul',              'language': 'Dari, Pashto',             'currency_code': 'AFN', 'currency_name': 'Afghan afghani',                'currency_symbol': '؋'},
    'AL': {'capital': 'Tirana',             'language': 'Albanian',                 'currency_code': 'ALL', 'currency_name': 'Albanian lek',                  'currency_symbol': 'L'},
    'DZ': {'capital': 'Algiers',            'language': 'Arabic, Berber',           'currency_code': 'DZD', 'currency_name': 'Algerian dinar',                'currency_symbol': 'DZD'},
    'AD': {'capital': 'Andorra la Vella',   'language': 'Catalan',                  'currency_code': 'EUR', 'currency_name': 'Euro',                          'currency_symbol': '€'},
    'AO': {'capital': 'Luanda',             'language': 'Portuguese',               'currency_code': 'AOA', 'currency_name': 'Angolan kwanza',                'currency_symbol': 'Kz'},
    'AG': {'capital': "Saint John's",       'language': 'English',                  'currency_code': 'XCD', 'currency_name': 'East Caribbean dollar',         'currency_symbol': 'EC$'},
    'AR': {'capital': 'Buenos Aires',       'language': 'Spanish',                  'currency_code': 'ARS', 'currency_name': 'Argentine peso',                'currency_symbol': '$'},
    'AM': {'capital': 'Yerevan',            'language': 'Armenian',                 'currency_code': 'AMD', 'currency_name': 'Armenian dram',                 'currency_symbol': '֏'},
    'AU': {'capital': 'Canberra',           'language': 'English',                  'currency_code': 'AUD', 'currency_name': 'Australian dollar',             'currency_symbol': 'A$'},
    'AT': {'capital': 'Vienna',             'language': 'German',                   'currency_code': 'EUR', 'currency_name': 'Euro',                          'currency_symbol': '€'},
    'AZ': {'capital': 'Baku',              'language': 'Azerbaijani',               'currency_code': 'AZN', 'currency_name': 'Azerbaijani manat',             'currency_symbol': '₼'},
    'BS': {'capital': 'Nassau',             'language': 'English',                  'currency_code': 'BSD', 'currency_name': 'Bahamian dollar',               'currency_symbol': 'B$'},
    'BH': {'capital': 'Manama',             'language': 'Arabic',                   'currency_code': 'BHD', 'currency_name': 'Bahraini dinar',                'currency_symbol': 'BD'},
    'BD': {'capital': 'Dhaka',              'language': 'Bengali',                  'currency_code': 'BDT', 'currency_name': 'Bangladeshi taka',              'currency_symbol': '৳'},
    'BB': {'capital': 'Bridgetown',         'language': 'English',                  'currency_code': 'BBD', 'currency_name': 'Barbadian dollar',              'currency_symbol': 'Bds$'},
    'BY': {'capital': 'Minsk',              'language': 'Belarusian, Russian',      'currency_code': 'BYN', 'currency_name': 'Belarusian ruble',              'currency_symbol': 'Br'},
    'BE': {'capital': 'Brussels',           'language': 'Dutch, French, German',    'currency_code': 'EUR', 'currency_name': 'Euro',                          'currency_symbol': '€'},
    'BZ': {'capital': 'Belmopan',           'language': 'English',                  'currency_code': 'BZD', 'currency_name': 'Belize dollar',                 'currency_symbol': 'BZ$'},
    'BJ': {'capital': 'Porto-Novo',         'language': 'French',                   'currency_code': 'XOF', 'currency_name': 'West African CFA franc',        'currency_symbol': 'Fr'},
    'BT': {'capital': 'Thimphu',            'language': 'Dzongkha',                 'currency_code': 'BTN', 'currency_name': 'Bhutanese ngultrum',            'currency_symbol': 'Nu'},
    'BO': {'capital': 'Sucre',              'language': 'Spanish',                  'currency_code': 'BOB', 'currency_name': 'Bolivian boliviano',            'currency_symbol': 'Bs'},
    'BA': {'capital': 'Sarajevo',           'language': 'Bosnian, Serbian, Croatian','currency_code': 'BAM','currency_name': 'Convertible mark',             'currency_symbol': 'KM'},
    'BW': {'capital': 'Gaborone',           'language': 'English, Tswana',          'currency_code': 'BWP', 'currency_name': 'Botswanan pula',                'currency_symbol': 'P'},
    'BR': {'capital': 'Brasília',           'language': 'Portuguese',               'currency_code': 'BRL', 'currency_name': 'Brazilian real',                'currency_symbol': 'R$'},
    'BN': {'capital': 'Bandar Seri Begawan','language': 'Malay',                    'currency_code': 'BND', 'currency_name': 'Brunei dollar',                 'currency_symbol': 'B$'},
    'BG': {'capital': 'Sofia',              'language': 'Bulgarian',                'currency_code': 'BGN', 'currency_name': 'Bulgarian lev',                 'currency_symbol': 'лв'},
    'BF': {'capital': 'Ouagadougou',        'language': 'French',                   'currency_code': 'XOF', 'currency_name': 'West African CFA franc',        'currency_symbol': 'Fr'},
    'BI': {'capital': 'Gitega',             'language': 'Kirundi, French',          'currency_code': 'BIF', 'currency_name': 'Burundian franc',               'currency_symbol': 'Fr'},
    'CV': {'capital': 'Praia',              'language': 'Portuguese',               'currency_code': 'CVE', 'currency_name': 'Cape Verdean escudo',           'currency_symbol': '$'},
    'KH': {'capital': 'Phnom Penh',         'language': 'Khmer',                    'currency_code': 'KHR', 'currency_name': 'Cambodian riel',                'currency_symbol': '៛'},
    'CM': {'capital': 'Yaoundé',            'language': 'French, English',          'currency_code': 'XAF', 'currency_name': 'Central African CFA franc',     'currency_symbol': 'Fr'},
    'CA': {'capital': 'Ottawa',             'language': 'English, French',          'currency_code': 'CAD', 'currency_name': 'Canadian dollar',               'currency_symbol': 'C$'},
    'CF': {'capital': 'Bangui',             'language': 'Sango, French',            'currency_code': 'XAF', 'currency_name': 'Central African CFA franc',     'currency_symbol': 'Fr'},
    'TD': {'capital': "N'Djamena",          'language': 'Arabic, French',           'currency_code': 'XAF', 'currency_name': 'Central African CFA franc',     'currency_symbol': 'Fr'},
    'CL': {'capital': 'Santiago',           'language': 'Spanish',                  'currency_code': 'CLP', 'currency_name': 'Chilean peso',                  'currency_symbol': '$'},
    'CN': {'capital': 'Beijing',            'language': 'Mandarin Chinese',         'currency_code': 'CNY', 'currency_name': 'Chinese yuan',                  'currency_symbol': '¥'},
    'CO': {'capital': 'Bogotá',             'language': 'Spanish',                  'currency_code': 'COP', 'currency_name': 'Colombian peso',                'currency_symbol': '$'},
    'KM': {'capital': 'Moroni',             'language': 'Comorian, Arabic, French', 'currency_code': 'KMF', 'currency_name': 'Comorian franc',                'currency_symbol': 'Fr'},
    'CG': {'capital': 'Brazzaville',        'language': 'French',                   'currency_code': 'XAF', 'currency_name': 'Central African CFA franc',     'currency_symbol': 'Fr'},
    'CD': {'capital': 'Kinshasa',           'language': 'French',                   'currency_code': 'CDF', 'currency_name': 'Congolese franc',               'currency_symbol': 'Fr'},
    'CR': {'capital': 'San José',           'language': 'Spanish',                  'currency_code': 'CRC', 'currency_name': 'Costa Rican colón',             'currency_symbol': '₡'},
    'CI': {'capital': 'Yamoussoukro',       'language': 'French',                   'currency_code': 'XOF', 'currency_name': 'West African CFA franc',        'currency_symbol': 'Fr'},
    'HR': {'capital': 'Zagreb',             'language': 'Croatian',                 'currency_code': 'EUR', 'currency_name': 'Euro',                          'currency_symbol': '€'},
    'CU': {'capital': 'Havana',             'language': 'Spanish',                  'currency_code': 'CUP', 'currency_name': 'Cuban peso',                    'currency_symbol': '$'},
    'CY': {'capital': 'Nicosia',            'language': 'Greek, Turkish',           'currency_code': 'EUR', 'currency_name': 'Euro',                          'currency_symbol': '€'},
    'CZ': {'capital': 'Prague',             'language': 'Czech',                    'currency_code': 'CZK', 'currency_name': 'Czech koruna',                  'currency_symbol': 'Kč'},
    'DK': {'capital': 'Copenhagen',         'language': 'Danish',                   'currency_code': 'DKK', 'currency_name': 'Danish krone',                  'currency_symbol': 'kr'},
    'DJ': {'capital': 'Djibouti',           'language': 'French, Arabic',           'currency_code': 'DJF', 'currency_name': 'Djiboutian franc',              'currency_symbol': 'Fr'},
    'DM': {'capital': 'Roseau',             'language': 'English',                  'currency_code': 'XCD', 'currency_name': 'East Caribbean dollar',         'currency_symbol': 'EC$'},
    'DO': {'capital': 'Santo Domingo',      'language': 'Spanish',                  'currency_code': 'DOP', 'currency_name': 'Dominican peso',                'currency_symbol': 'RD$'},
    'EC': {'capital': 'Quito',              'language': 'Spanish',                  'currency_code': 'USD', 'currency_name': 'US dollar',                     'currency_symbol': '$'},
    'EG': {'capital': 'Cairo',              'language': 'Arabic',                   'currency_code': 'EGP', 'currency_name': 'Egyptian pound',                'currency_symbol': '£'},
    'SV': {'capital': 'San Salvador',       'language': 'Spanish',                  'currency_code': 'USD', 'currency_name': 'US dollar',                     'currency_symbol': '$'},
    'GQ': {'capital': 'Malabo',             'language': 'Spanish, French',          'currency_code': 'XAF', 'currency_name': 'Central African CFA franc',     'currency_symbol': 'Fr'},
    'ER': {'capital': 'Asmara',             'language': 'Tigrinya, Arabic',         'currency_code': 'ERN', 'currency_name': 'Eritrean nakfa',                'currency_symbol': 'Nfk'},
    'EE': {'capital': 'Tallinn',            'language': 'Estonian',                 'currency_code': 'EUR', 'currency_name': 'Euro',                          'currency_symbol': '€'},
    'SZ': {'capital': 'Mbabane',            'language': 'Swati, English',           'currency_code': 'SZL', 'currency_name': 'Swazi lilangeni',               'currency_symbol': 'L'},
    'ET': {'capital': 'Addis Ababa',        'language': 'Amharic',                  'currency_code': 'ETB', 'currency_name': 'Ethiopian birr',                'currency_symbol': 'Br'},
    'FJ': {'capital': 'Suva',               'language': 'English, Fijian, Hindi',   'currency_code': 'FJD', 'currency_name': 'Fijian dollar',                 'currency_symbol': 'FJ$'},
    'FI': {'capital': 'Helsinki',           'language': 'Finnish, Swedish',         'currency_code': 'EUR', 'currency_name': 'Euro',                          'currency_symbol': '€'},
    'FR': {'capital': 'Paris',              'language': 'French',                   'currency_code': 'EUR', 'currency_name': 'Euro',                          'currency_symbol': '€'},
    'GA': {'capital': 'Libreville',         'language': 'French',                   'currency_code': 'XAF', 'currency_name': 'Central African CFA franc',     'currency_symbol': 'Fr'},
    'GM': {'capital': 'Banjul',             'language': 'English',                  'currency_code': 'GMD', 'currency_name': 'Gambian dalasi',                'currency_symbol': 'D'},
    'GE': {'capital': 'Tbilisi',            'language': 'Georgian',                 'currency_code': 'GEL', 'currency_name': 'Georgian lari',                 'currency_symbol': '₾'},
    'DE': {'capital': 'Berlin',             'language': 'German',                   'currency_code': 'EUR', 'currency_name': 'Euro',                          'currency_symbol': '€'},
    'GH': {'capital': 'Accra',              'language': 'English',                  'currency_code': 'GHS', 'currency_name': 'Ghanaian cedi',                 'currency_symbol': '₵'},
    'GR': {'capital': 'Athens',             'language': 'Greek',                    'currency_code': 'EUR', 'currency_name': 'Euro',                          'currency_symbol': '€'},
    'GD': {'capital': "Saint George's",     'language': 'English',                  'currency_code': 'XCD', 'currency_name': 'East Caribbean dollar',         'currency_symbol': 'EC$'},
    'GT': {'capital': 'Guatemala City',     'language': 'Spanish',                  'currency_code': 'GTQ', 'currency_name': 'Guatemalan quetzal',            'currency_symbol': 'Q'},
    'GN': {'capital': 'Conakry',            'language': 'French',                   'currency_code': 'GNF', 'currency_name': 'Guinean franc',                 'currency_symbol': 'Fr'},
    'GW': {'capital': 'Bissau',             'language': 'Portuguese',               'currency_code': 'XOF', 'currency_name': 'West African CFA franc',        'currency_symbol': 'Fr'},
    'GY': {'capital': 'Georgetown',         'language': 'English',                  'currency_code': 'GYD', 'currency_name': 'Guyanese dollar',               'currency_symbol': 'G$'},
    'HT': {'capital': 'Port-au-Prince',     'language': 'Haitian Creole, French',   'currency_code': 'HTG', 'currency_name': 'Haitian gourde',                'currency_symbol': 'G'},
    'VA': {'capital': 'Vatican City',       'language': 'Italian, Latin',           'currency_code': 'EUR', 'currency_name': 'Euro',                          'currency_symbol': '€'},
    'HN': {'capital': 'Tegucigalpa',        'language': 'Spanish',                  'currency_code': 'HNL', 'currency_name': 'Honduran lempira',              'currency_symbol': 'L'},
    'HK': {'capital': 'Hong Kong',          'language': 'Chinese, English',         'currency_code': 'HKD', 'currency_name': 'Hong Kong dollar',              'currency_symbol': 'HK$'},
    'HU': {'capital': 'Budapest',           'language': 'Hungarian',                'currency_code': 'HUF', 'currency_name': 'Hungarian forint',              'currency_symbol': 'Ft'},
    'IS': {'capital': 'Reykjavík',          'language': 'Icelandic',                'currency_code': 'ISK', 'currency_name': 'Icelandic króna',               'currency_symbol': 'kr'},
    'IN': {'capital': 'New Delhi',          'language': 'Hindi, English',           'currency_code': 'INR', 'currency_name': 'Indian rupee',                  'currency_symbol': '₹'},
    'ID': {'capital': 'Jakarta',            'language': 'Indonesian',               'currency_code': 'IDR', 'currency_name': 'Indonesian rupiah',             'currency_symbol': 'Rp'},
    'IR': {'capital': 'Tehran',             'language': 'Persian',                  'currency_code': 'IRR', 'currency_name': 'Iranian rial',                  'currency_symbol': '﷼'},
    'IQ': {'capital': 'Baghdad',            'language': 'Arabic, Kurdish',          'currency_code': 'IQD', 'currency_name': 'Iraqi dinar',                   'currency_symbol': 'IQD'},
    'IE': {'capital': 'Dublin',             'language': 'Irish, English',           'currency_code': 'EUR', 'currency_name': 'Euro',                          'currency_symbol': '€'},
    'IL': {'capital': 'Jerusalem',          'language': 'Hebrew, Arabic',           'currency_code': 'ILS', 'currency_name': 'Israeli new shekel',            'currency_symbol': '₪'},
    'IT': {'capital': 'Rome',               'language': 'Italian',                  'currency_code': 'EUR', 'currency_name': 'Euro',                          'currency_symbol': '€'},
    'JM': {'capital': 'Kingston',           'language': 'English',                  'currency_code': 'JMD', 'currency_name': 'Jamaican dollar',               'currency_symbol': 'J$'},
    'JP': {'capital': 'Tokyo',              'language': 'Japanese',                 'currency_code': 'JPY', 'currency_name': 'Japanese yen',                  'currency_symbol': '¥'},
    'JO': {'capital': 'Amman',              'language': 'Arabic',                   'currency_code': 'JOD', 'currency_name': 'Jordanian dinar',               'currency_symbol': 'JD'},
    'KZ': {'capital': 'Astana',             'language': 'Kazakh, Russian',          'currency_code': 'KZT', 'currency_name': 'Kazakhstani tenge',             'currency_symbol': '₸'},
    'KE': {'capital': 'Nairobi',            'language': 'Swahili, English',         'currency_code': 'KES', 'currency_name': 'Kenyan shilling',               'currency_symbol': 'KSh'},
    'KI': {'capital': 'South Tarawa',       'language': 'English, Gilbertese',      'currency_code': 'AUD', 'currency_name': 'Australian dollar',             'currency_symbol': 'A$'},
    'KP': {'capital': 'Pyongyang',          'language': 'Korean',                   'currency_code': 'KPW', 'currency_name': 'North Korean won',              'currency_symbol': '₩'},
    'KR': {'capital': 'Seoul',              'language': 'Korean',                   'currency_code': 'KRW', 'currency_name': 'South Korean won',              'currency_symbol': '₩'},
    'KW': {'capital': 'Kuwait City',        'language': 'Arabic',                   'currency_code': 'KWD', 'currency_name': 'Kuwaiti dinar',                 'currency_symbol': 'KD'},
    'KG': {'capital': 'Bishkek',            'language': 'Kyrgyz, Russian',          'currency_code': 'KGS', 'currency_name': 'Kyrgyzstani som',              'currency_symbol': 'с'},
    'LA': {'capital': 'Vientiane',          'language': 'Lao',                      'currency_code': 'LAK', 'currency_name': 'Lao kip',                       'currency_symbol': '₭'},
    'LV': {'capital': 'Riga',               'language': 'Latvian',                  'currency_code': 'EUR', 'currency_name': 'Euro',                          'currency_symbol': '€'},
    'LB': {'capital': 'Beirut',             'language': 'Arabic',                   'currency_code': 'LBP', 'currency_name': 'Lebanese pound',                'currency_symbol': 'L£'},
    'LS': {'capital': 'Maseru',             'language': 'Sesotho, English',         'currency_code': 'LSL', 'currency_name': 'Lesotho loti',                  'currency_symbol': 'L'},
    'LR': {'capital': 'Monrovia',           'language': 'English',                  'currency_code': 'LRD', 'currency_name': 'Liberian dollar',               'currency_symbol': 'L$'},
    'LY': {'capital': 'Tripoli',            'language': 'Arabic',                   'currency_code': 'LYD', 'currency_name': 'Libyan dinar',                  'currency_symbol': 'LD'},
    'LI': {'capital': 'Vaduz',              'language': 'German',                   'currency_code': 'CHF', 'currency_name': 'Swiss franc',                   'currency_symbol': 'Fr'},
    'LT': {'capital': 'Vilnius',            'language': 'Lithuanian',               'currency_code': 'EUR', 'currency_name': 'Euro',                          'currency_symbol': '€'},
    'LU': {'capital': 'Luxembourg City',    'language': 'Luxembourgish, French, German','currency_code': 'EUR','currency_name': 'Euro',                       'currency_symbol': '€'},
    'MO': {'capital': 'Macau',              'language': 'Chinese, Portuguese',      'currency_code': 'MOP', 'currency_name': 'Macanese pataca',               'currency_symbol': 'P'},
    'MG': {'capital': 'Antananarivo',       'language': 'Malagasy, French',         'currency_code': 'MGA', 'currency_name': 'Malagasy ariary',               'currency_symbol': 'Ar'},
    'MW': {'capital': 'Lilongwe',           'language': 'Chichewa, English',        'currency_code': 'MWK', 'currency_name': 'Malawian kwacha',               'currency_symbol': 'MK'},
    'MY': {'capital': 'Kuala Lumpur',       'language': 'Malay',                    'currency_code': 'MYR', 'currency_name': 'Malaysian ringgit',             'currency_symbol': 'RM'},
    'MV': {'capital': 'Malé',               'language': 'Dhivehi',                  'currency_code': 'MVR', 'currency_name': 'Maldivian rufiyaa',             'currency_symbol': 'Rf'},
    'ML': {'capital': 'Bamako',             'language': 'French',                   'currency_code': 'XOF', 'currency_name': 'West African CFA franc',        'currency_symbol': 'Fr'},
    'MT': {'capital': 'Valletta',           'language': 'Maltese, English',         'currency_code': 'EUR', 'currency_name': 'Euro',                          'currency_symbol': '€'},
    'MH': {'capital': 'Majuro',             'language': 'Marshallese, English',     'currency_code': 'USD', 'currency_name': 'US dollar',                     'currency_symbol': '$'},
    'MR': {'capital': 'Nouakchott',         'language': 'Arabic',                   'currency_code': 'MRU', 'currency_name': 'Mauritanian ouguiya',           'currency_symbol': 'UM'},
    'MU': {'capital': 'Port Louis',         'language': 'English, French',          'currency_code': 'MUR', 'currency_name': 'Mauritian rupee',               'currency_symbol': '₨'},
    'MX': {'capital': 'Mexico City',        'language': 'Spanish',                  'currency_code': 'MXN', 'currency_name': 'Mexican peso',                  'currency_symbol': '$'},
    'FM': {'capital': 'Palikir',            'language': 'English',                  'currency_code': 'USD', 'currency_name': 'US dollar',                     'currency_symbol': '$'},
    'MD': {'capital': 'Chișinău',           'language': 'Romanian',                 'currency_code': 'MDL', 'currency_name': 'Moldovan leu',                  'currency_symbol': 'L'},
    'MC': {'capital': 'Monaco',             'language': 'French',                   'currency_code': 'EUR', 'currency_name': 'Euro',                          'currency_symbol': '€'},
    'MN': {'capital': 'Ulaanbaatar',        'language': 'Mongolian',                'currency_code': 'MNT', 'currency_name': 'Mongolian tögrög',              'currency_symbol': '₮'},
    'ME': {'capital': 'Podgorica',          'language': 'Montenegrin',              'currency_code': 'EUR', 'currency_name': 'Euro',                          'currency_symbol': '€'},
    'MA': {'capital': 'Rabat',              'language': 'Arabic, Berber',           'currency_code': 'MAD', 'currency_name': 'Moroccan dirham',               'currency_symbol': 'MAD'},
    'MZ': {'capital': 'Maputo',             'language': 'Portuguese',               'currency_code': 'MZN', 'currency_name': 'Mozambican metical',            'currency_symbol': 'MT'},
    'MM': {'capital': 'Naypyidaw',          'language': 'Burmese',                  'currency_code': 'MMK', 'currency_name': 'Burmese kyat',                  'currency_symbol': 'K'},
    'NA': {'capital': 'Windhoek',           'language': 'English',                  'currency_code': 'NAD', 'currency_name': 'Namibian dollar',               'currency_symbol': 'N$'},
    'NR': {'capital': 'Yaren',              'language': 'Nauruan, English',         'currency_code': 'AUD', 'currency_name': 'Australian dollar',             'currency_symbol': 'A$'},
    'NP': {'capital': 'Kathmandu',          'language': 'Nepali',                   'currency_code': 'NPR', 'currency_name': 'Nepalese rupee',                'currency_symbol': '₨'},
    'NL': {'capital': 'Amsterdam',          'language': 'Dutch',                    'currency_code': 'EUR', 'currency_name': 'Euro',                          'currency_symbol': '€'},
    'NZ': {'capital': 'Wellington',         'language': 'English, Māori',           'currency_code': 'NZD', 'currency_name': 'New Zealand dollar',            'currency_symbol': 'NZ$'},
    'NI': {'capital': 'Managua',            'language': 'Spanish',                  'currency_code': 'NIO', 'currency_name': 'Nicaraguan córdoba',            'currency_symbol': 'C$'},
    'NE': {'capital': 'Niamey',             'language': 'French',                   'currency_code': 'XOF', 'currency_name': 'West African CFA franc',        'currency_symbol': 'Fr'},
    'NG': {'capital': 'Abuja',              'language': 'English',                  'currency_code': 'NGN', 'currency_name': 'Nigerian naira',                'currency_symbol': '₦'},
    'MK': {'capital': 'Skopje',             'language': 'Macedonian, Albanian',     'currency_code': 'MKD', 'currency_name': 'Macedonian denar',              'currency_symbol': 'den'},
    'NO': {'capital': 'Oslo',               'language': 'Norwegian',                'currency_code': 'NOK', 'currency_name': 'Norwegian krone',               'currency_symbol': 'kr'},
    'OM': {'capital': 'Muscat',             'language': 'Arabic',                   'currency_code': 'OMR', 'currency_name': 'Omani rial',                    'currency_symbol': '﷼'},
    'PK': {'capital': 'Islamabad',          'language': 'Urdu, English',            'currency_code': 'PKR', 'currency_name': 'Pakistani rupee',               'currency_symbol': '₨'},
    'PW': {'capital': 'Ngerulmud',          'language': 'Palauan, English',         'currency_code': 'USD', 'currency_name': 'US dollar',                     'currency_symbol': '$'},
    'PA': {'capital': 'Panama City',        'language': 'Spanish',                  'currency_code': 'PAB', 'currency_name': 'Panamanian balboa',             'currency_symbol': 'B/.'},
    'PG': {'capital': 'Port Moresby',       'language': 'English, Tok Pisin',       'currency_code': 'PGK', 'currency_name': 'Papua New Guinean kina',        'currency_symbol': 'K'},
    'PY': {'capital': 'Asunción',           'language': 'Spanish, Guaraní',         'currency_code': 'PYG', 'currency_name': 'Paraguayan guaraní',            'currency_symbol': '₲'},
    'PE': {'capital': 'Lima',               'language': 'Spanish',                  'currency_code': 'PEN', 'currency_name': 'Peruvian sol',                  'currency_symbol': 'S/'},
    'PH': {'capital': 'Manila',             'language': 'Filipino, English',        'currency_code': 'PHP', 'currency_name': 'Philippine peso',               'currency_symbol': '₱'},
    'PL': {'capital': 'Warsaw',             'language': 'Polish',                   'currency_code': 'PLN', 'currency_name': 'Polish złoty',                  'currency_symbol': 'zł'},
    'PT': {'capital': 'Lisbon',             'language': 'Portuguese',               'currency_code': 'EUR', 'currency_name': 'Euro',                          'currency_symbol': '€'},
    'QA': {'capital': 'Doha',               'language': 'Arabic',                   'currency_code': 'QAR', 'currency_name': 'Qatari riyal',                  'currency_symbol': '﷼'},
    'RO': {'capital': 'Bucharest',          'language': 'Romanian',                 'currency_code': 'RON', 'currency_name': 'Romanian leu',                  'currency_symbol': 'lei'},
    'RU': {'capital': 'Moscow',             'language': 'Russian',                  'currency_code': 'RUB', 'currency_name': 'Russian ruble',                 'currency_symbol': '₽'},
    'RW': {'capital': 'Kigali',             'language': 'Kinyarwanda, English, French','currency_code': 'RWF','currency_name': 'Rwandan franc',               'currency_symbol': 'Fr'},
    'KN': {'capital': 'Basseterre',         'language': 'English',                  'currency_code': 'XCD', 'currency_name': 'East Caribbean dollar',         'currency_symbol': 'EC$'},
    'LC': {'capital': 'Castries',           'language': 'English',                  'currency_code': 'XCD', 'currency_name': 'East Caribbean dollar',         'currency_symbol': 'EC$'},
    'VC': {'capital': 'Kingstown',          'language': 'English',                  'currency_code': 'XCD', 'currency_name': 'East Caribbean dollar',         'currency_symbol': 'EC$'},
    'WS': {'capital': 'Apia',               'language': 'Samoan, English',          'currency_code': 'WST', 'currency_name': 'Samoan tālā',                   'currency_symbol': 'T'},
    'SM': {'capital': 'San Marino',         'language': 'Italian',                  'currency_code': 'EUR', 'currency_name': 'Euro',                          'currency_symbol': '€'},
    'ST': {'capital': 'São Tomé',           'language': 'Portuguese',               'currency_code': 'STN', 'currency_name': 'São Tomé dobra',                'currency_symbol': 'Db'},
    'SA': {'capital': 'Riyadh',             'language': 'Arabic',                   'currency_code': 'SAR', 'currency_name': 'Saudi riyal',                   'currency_symbol': '﷼'},
    'SN': {'capital': 'Dakar',              'language': 'French',                   'currency_code': 'XOF', 'currency_name': 'West African CFA franc',        'currency_symbol': 'Fr'},
    'RS': {'capital': 'Belgrade',           'language': 'Serbian',                  'currency_code': 'RSD', 'currency_name': 'Serbian dinar',                 'currency_symbol': 'din'},
    'SC': {'capital': 'Victoria',           'language': 'Seychellois Creole, French, English','currency_code': 'SCR','currency_name': 'Seychellois rupee',    'currency_symbol': '₨'},
    'SL': {'capital': 'Freetown',           'language': 'English',                  'currency_code': 'SLL', 'currency_name': 'Sierra Leonean leone',           'currency_symbol': 'Le'},
    'SG': {'capital': 'Singapore',          'language': 'English, Malay, Mandarin, Tamil','currency_code': 'SGD','currency_name': 'Singapore dollar',         'currency_symbol': 'S$'},
    'SK': {'capital': 'Bratislava',         'language': 'Slovak',                   'currency_code': 'EUR', 'currency_name': 'Euro',                          'currency_symbol': '€'},
    'SI': {'capital': 'Ljubljana',          'language': 'Slovenian',                'currency_code': 'EUR', 'currency_name': 'Euro',                          'currency_symbol': '€'},
    'SB': {'capital': 'Honiara',            'language': 'English',                  'currency_code': 'SBD', 'currency_name': 'Solomon Islands dollar',        'currency_symbol': 'SI$'},
    'SO': {'capital': 'Mogadishu',          'language': 'Somali, Arabic',           'currency_code': 'SOS', 'currency_name': 'Somali shilling',               'currency_symbol': 'Sh'},
    'ZA': {'capital': 'Pretoria',           'language': 'Zulu, Xhosa, Afrikaans, English','currency_code': 'ZAR','currency_name': 'South African rand',       'currency_symbol': 'R'},
    'SS': {'capital': 'Juba',               'language': 'English',                  'currency_code': 'SSP', 'currency_name': 'South Sudanese pound',          'currency_symbol': '£'},
    'ES': {'capital': 'Madrid',             'language': 'Spanish',                  'currency_code': 'EUR', 'currency_name': 'Euro',                          'currency_symbol': '€'},
    'LK': {'capital': 'Sri Jayawardenepura Kotte','language': 'Sinhala, Tamil',     'currency_code': 'LKR', 'currency_name': 'Sri Lankan rupee',              'currency_symbol': '₨'},
    'SD': {'capital': 'Khartoum',           'language': 'Arabic, English',          'currency_code': 'SDG', 'currency_name': 'Sudanese pound',                'currency_symbol': 'SDG'},
    'SR': {'capital': 'Paramaribo',         'language': 'Dutch',                    'currency_code': 'SRD', 'currency_name': 'Surinamese dollar',             'currency_symbol': 'SR$'},
    'SE': {'capital': 'Stockholm',          'language': 'Swedish',                  'currency_code': 'SEK', 'currency_name': 'Swedish krona',                 'currency_symbol': 'kr'},
    'CH': {'capital': 'Bern',               'language': 'German, French, Italian, Romansh','currency_code': 'CHF','currency_name': 'Swiss franc',             'currency_symbol': 'Fr'},
    'SY': {'capital': 'Damascus',           'language': 'Arabic',                   'currency_code': 'SYP', 'currency_name': 'Syrian pound',                  'currency_symbol': '£'},
    'TW': {'capital': 'Taipei',             'language': 'Mandarin Chinese',         'currency_code': 'TWD', 'currency_name': 'New Taiwan dollar',             'currency_symbol': 'NT$'},
    'TJ': {'capital': 'Dushanbe',           'language': 'Tajik',                    'currency_code': 'TJS', 'currency_name': 'Tajikistani somoni',            'currency_symbol': 'SM'},
    'TZ': {'capital': 'Dodoma',             'language': 'Swahili, English',         'currency_code': 'TZS', 'currency_name': 'Tanzanian shilling',            'currency_symbol': 'TSh'},
    'TH': {'capital': 'Bangkok',            'language': 'Thai',                     'currency_code': 'THB', 'currency_name': 'Thai baht',                     'currency_symbol': '฿'},
    'TL': {'capital': 'Dili',               'language': 'Tetum, Portuguese',        'currency_code': 'USD', 'currency_name': 'US dollar',                     'currency_symbol': '$'},
    'TG': {'capital': 'Lomé',               'language': 'French',                   'currency_code': 'XOF', 'currency_name': 'West African CFA franc',        'currency_symbol': 'Fr'},
    'TO': {'capital': "Nuku'alofa",         'language': 'Tongan, English',          'currency_code': 'TOP', 'currency_name': "Tongan paʻanga",                'currency_symbol': 'T$'},
    'TT': {'capital': 'Port of Spain',      'language': 'English',                  'currency_code': 'TTD', 'currency_name': 'Trinidad and Tobago dollar',    'currency_symbol': 'TT$'},
    'TN': {'capital': 'Tunis',              'language': 'Arabic',                   'currency_code': 'TND', 'currency_name': 'Tunisian dinar',                'currency_symbol': 'DT'},
    'TR': {'capital': 'Ankara',             'language': 'Turkish',                  'currency_code': 'TRY', 'currency_name': 'Turkish lira',                  'currency_symbol': '₺'},
    'TM': {'capital': 'Ashgabat',           'language': 'Turkmen',                  'currency_code': 'TMT', 'currency_name': 'Turkmenistani manat',           'currency_symbol': 'T'},
    'TV': {'capital': 'Funafuti',           'language': 'Tuvaluan, English',        'currency_code': 'AUD', 'currency_name': 'Australian dollar',             'currency_symbol': 'A$'},
    'UG': {'capital': 'Kampala',            'language': 'English, Swahili',         'currency_code': 'UGX', 'currency_name': 'Ugandan shilling',              'currency_symbol': 'USh'},
    'UA': {'capital': 'Kyiv',               'language': 'Ukrainian',                'currency_code': 'UAH', 'currency_name': 'Ukrainian hryvnia',             'currency_symbol': '₴'},
    'AE': {'capital': 'Abu Dhabi',          'language': 'Arabic',                   'currency_code': 'AED', 'currency_name': 'UAE dirham',                    'currency_symbol': 'AED'},
    'GB': {'capital': 'London',             'language': 'English',                  'currency_code': 'GBP', 'currency_name': 'Pound sterling',                'currency_symbol': '£'},
    'US': {'capital': 'Washington, D.C.',   'language': 'English',                  'currency_code': 'USD', 'currency_name': 'US dollar',                     'currency_symbol': '$'},
    'UY': {'capital': 'Montevideo',         'language': 'Spanish',                  'currency_code': 'UYU', 'currency_name': 'Uruguayan peso',                'currency_symbol': '$U'},
    'UZ': {'capital': 'Tashkent',           'language': 'Uzbek',                    'currency_code': 'UZS', 'currency_name': 'Uzbekistani soʻm',              'currency_symbol': 'soʻm'},
    'VU': {'capital': 'Port Vila',          'language': 'Bislama, English, French', 'currency_code': 'VUV', 'currency_name': 'Vanuatu vatu',                  'currency_symbol': 'Vt'},
    'VE': {'capital': 'Caracas',            'language': 'Spanish',                  'currency_code': 'VES', 'currency_name': 'Venezuelan bolívar soberano',   'currency_symbol': 'Bs.S'},
    'VN': {'capital': 'Hanoi',              'language': 'Vietnamese',               'currency_code': 'VND', 'currency_name': 'Vietnamese đồng',               'currency_symbol': '₫'},
    'YE': {'capital': "Sana'a",             'language': 'Arabic',                   'currency_code': 'YER', 'currency_name': 'Yemeni rial',                   'currency_symbol': '﷼'},
    'ZM': {'capital': 'Lusaka',             'language': 'English',                  'currency_code': 'ZMW', 'currency_name': 'Zambian kwacha',                'currency_symbol': 'ZK'},
    'ZW': {'capital': 'Harare',             'language': 'English, Shona, Ndebele',  'currency_code': 'ZWL', 'currency_name': 'Zimbabwean dollar',             'currency_symbol': 'Z$'},
    'XK': {'capital': 'Pristina',           'language': 'Albanian, Serbian',        'currency_code': 'EUR', 'currency_name': 'Euro',                          'currency_symbol': '€'},
}


def get_country_info(country_code):
    """Restituisce i dati del paese (capitale, lingua, valuta) per codice ISO2. None se non trovato."""
    return COUNTRY_DATA.get((country_code or '').upper())
