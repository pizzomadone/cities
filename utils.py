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


def sunrise_sunset(lat, lon):
    """
    Calcola alba e tramonto approssimati (UTC) per oggi usando algoritmo NOAA semplificato.
    Restituisce (sunrise_str, sunset_str, day_length_str, date_str).
    Casi speciali: 'Midnight Sun' o 'Polar Night'.
    """
    today = datetime.utcnow()
    N = today.timetuple().tm_yday
    date_str = today.strftime('%B %d, %Y')

    # Declinazione solare
    decl = 23.45 * math.sin(math.radians(360 / 365 * (N - 81)))

    # Angolo orario al sorgere/tramonto (zenith = 90.833° per rifrazione)
    cos_H_num = (math.cos(math.radians(90.833)) -
                 math.sin(math.radians(lat)) * math.sin(math.radians(decl)))
    cos_H_den = (math.cos(math.radians(lat)) * math.cos(math.radians(decl)))

    if cos_H_den == 0:
        return 'N/A', 'N/A', 'N/A', date_str

    cos_H = cos_H_num / cos_H_den

    if cos_H < -1:
        return 'Midnight Sun', 'Midnight Sun', '24h 00m', date_str
    if cos_H > 1:
        return 'Polar Night', 'Polar Night', '0h 00m', date_str

    H = math.degrees(math.acos(cos_H))  # gradi

    # Equazione del tempo (minuti)
    B = math.radians(360 / 365 * (N - 81))
    EoT = 9.87 * math.sin(2 * B) - 7.53 * math.cos(B) - 1.5 * math.sin(B)

    # Mezzogiorno solare in UTC
    solar_noon = 12 - lon / 15 - EoT / 60
    H_hours = H / 15

    rise_h = (solar_noon - H_hours) % 24
    set_h  = (solar_noon + H_hours) % 24
    day_length = 2 * H_hours

    def fmt_time(h):
        hh = int(h)
        mm = int(round((h - hh) * 60))
        if mm >= 60:
            hh = (hh + 1) % 24
            mm = 0
        return f'{hh:02d}:{mm:02d} UTC'

    def fmt_duration(hours):
        h = int(hours)
        m = int(round((hours - h) * 60))
        if m >= 60:
            h += 1
            m = 0
        return f'{h}h {m:02d}m'

    return fmt_time(rise_h), fmt_time(set_h), fmt_duration(day_length), date_str
