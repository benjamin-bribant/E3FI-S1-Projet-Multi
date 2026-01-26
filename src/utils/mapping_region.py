# Mapping des codes pays ISO-2 vers les régions géographiques pour notre histogramme analysant l'espérance de vie et de la pollution


REGION_MAPPING = {
    # Asie
    'IN': 'Asie du Sud',
    'PK': 'Asie du Sud',
    'BD': 'Asie du Sud',
    'NP': 'Asie du Sud',
    'LK': 'Asie du Sud',
    'AF': 'Asie du Sud',
    'BT': 'Asie du Sud',
    'MV': 'Asie du Sud',
    
    'CN': 'Asie de l\'Est',
    'JP': 'Asie de l\'Est',
    'KR': 'Asie de l\'Est',
    'KP': 'Asie de l\'Est',
    'TW': 'Asie de l\'Est',
    'MN': 'Asie de l\'Est',
    'HK': 'Asie de l\'Est',
    'MO': 'Asie de l\'Est',
    
    'TH': 'Asie du Sud-Est',
    'VN': 'Asie du Sud-Est',
    'ID': 'Asie du Sud-Est',
    'PH': 'Asie du Sud-Est',
    'MY': 'Asie du Sud-Est',
    'SG': 'Asie du Sud-Est',
    'MM': 'Asie du Sud-Est',
    'KH': 'Asie du Sud-Est',
    'LA': 'Asie du Sud-Est',
    'BN': 'Asie du Sud-Est',
    'TL': 'Asie du Sud-Est',
    
    # Moyen-Orient
    'SA': 'Moyen-Orient',
    'AE': 'Moyen-Orient',
    'IR': 'Moyen-Orient',
    'IQ': 'Moyen-Orient',
    'IL': 'Moyen-Orient',
    'JO': 'Moyen-Orient',
    'LB': 'Moyen-Orient',
    'SY': 'Moyen-Orient',
    'YE': 'Moyen-Orient',
    'OM': 'Moyen-Orient',
    'KW': 'Moyen-Orient',
    'QA': 'Moyen-Orient',
    'BH': 'Moyen-Orient',
    'PS': 'Moyen-Orient',
    'TR': 'Moyen-Orient',
    
    # Europe occidentale
    'FR': 'Europe occidentale',
    'DE': 'Europe occidentale',
    'GB': 'Europe occidentale',
    'IT': 'Europe occidentale',
    'ES': 'Europe occidentale',
    'PT': 'Europe occidentale',
    'NL': 'Europe occidentale',
    'BE': 'Europe occidentale',
    'CH': 'Europe occidentale',
    'AT': 'Europe occidentale',
    'IE': 'Europe occidentale',
    'LU': 'Europe occidentale',
    'MC': 'Europe occidentale',
    'LI': 'Europe occidentale',
    'AD': 'Europe occidentale',
    
    # Europe du Nord
    'SE': 'Europe du Nord',
    'NO': 'Europe du Nord',
    'DK': 'Europe du Nord',
    'FI': 'Europe du Nord',
    'IS': 'Europe du Nord',
    'EE': 'Europe du Nord',
    'LV': 'Europe du Nord',
    'LT': 'Europe du Nord',
    
    # Europe de l'Est
    'PL': 'Europe de l\'Est',
    'CZ': 'Europe de l\'Est',
    'SK': 'Europe de l\'Est',
    'HU': 'Europe de l\'Est',
    'RO': 'Europe de l\'Est',
    'BG': 'Europe de l\'Est',
    'UA': 'Europe de l\'Est',
    'BY': 'Europe de l\'Est',
    'MD': 'Europe de l\'Est',
    'RU': 'Europe de l\'Est',
    
    # Europe du Sud
    'GR': 'Europe du Sud',
    'HR': 'Europe du Sud',
    'SI': 'Europe du Sud',
    'BA': 'Europe du Sud',
    'RS': 'Europe du Sud',
    'ME': 'Europe du Sud',
    'MK': 'Europe du Sud',
    'AL': 'Europe du Sud',
    'XK': 'Europe du Sud',
    'CY': 'Europe du Sud',
    'MT': 'Europe du Sud',
    
    # Amérique du Nord
    'US': 'Amérique du Nord',
    'CA': 'Amérique du Nord',
    'MX': 'Amérique du Nord',
    
    # Amérique centrale et Caraïbes
    'GT': 'Amérique centrale',
    'HN': 'Amérique centrale',
    'SV': 'Amérique centrale',
    'NI': 'Amérique centrale',
    'CR': 'Amérique centrale',
    'PA': 'Amérique centrale',
    'BZ': 'Amérique centrale',
    'CU': 'Amérique centrale',
    'DO': 'Amérique centrale',
    'HT': 'Amérique centrale',
    'JM': 'Amérique centrale',
    'TT': 'Amérique centrale',
    'BB': 'Amérique centrale',
    'BS': 'Amérique centrale',
    
    # Amérique du Sud
    'BR': 'Amérique du Sud',
    'AR': 'Amérique du Sud',
    'CL': 'Amérique du Sud',
    'CO': 'Amérique du Sud',
    'PE': 'Amérique du Sud',
    'VE': 'Amérique du Sud',
    'EC': 'Amérique du Sud',
    'BO': 'Amérique du Sud',
    'PY': 'Amérique du Sud',
    'UY': 'Amérique du Sud',
    'GY': 'Amérique du Sud',
    'SR': 'Amérique du Sud',
    'GF': 'Amérique du Sud',
    
    # Afrique du Nord
    'EG': 'Afrique du Nord',
    'DZ': 'Afrique du Nord',
    'MA': 'Afrique du Nord',
    'TN': 'Afrique du Nord',
    'LY': 'Afrique du Nord',
    'SD': 'Afrique du Nord',
    
    # Afrique subsaharienne (Ouest)
    'NG': 'Afrique subsaharienne',
    'GH': 'Afrique subsaharienne',
    'CI': 'Afrique subsaharienne',
    'SN': 'Afrique subsaharienne',
    'ML': 'Afrique subsaharienne',
    'BF': 'Afrique subsaharienne',
    'NE': 'Afrique subsaharienne',
    'GN': 'Afrique subsaharienne',
    'SL': 'Afrique subsaharienne',
    'LR': 'Afrique subsaharienne',
    'TG': 'Afrique subsaharienne',
    'BJ': 'Afrique subsaharienne',
    
    # Afrique subsaharienne (Est)
    'KE': 'Afrique subsaharienne',
    'TZ': 'Afrique subsaharienne',
    'UG': 'Afrique subsaharienne',
    'ET': 'Afrique subsaharienne',
    'SO': 'Afrique subsaharienne',
    'RW': 'Afrique subsaharienne',
    'BI': 'Afrique subsaharienne',
    'DJ': 'Afrique subsaharienne',
    'ER': 'Afrique subsaharienne',
    'SS': 'Afrique subsaharienne',
    
    # Afrique subsaharienne (Sud)
    'ZA': 'Afrique subsaharienne',
    'ZW': 'Afrique subsaharienne',
    'ZM': 'Afrique subsaharienne',
    'MW': 'Afrique subsaharienne',
    'MZ': 'Afrique subsaharienne',
    'BW': 'Afrique subsaharienne',
    'NA': 'Afrique subsaharienne',
    'LS': 'Afrique subsaharienne',
    'SZ': 'Afrique subsaharienne',
    'AO': 'Afrique subsaharienne',
    
    # Afrique subsaharienne (Centre)
    'CD': 'Afrique subsaharienne',
    'CG': 'Afrique subsaharienne',
    'CM': 'Afrique subsaharienne',
    'CF': 'Afrique subsaharienne',
    'TD': 'Afrique subsaharienne',
    'GA': 'Afrique subsaharienne',
    'GQ': 'Afrique subsaharienne',
    
    # Océanie
    'AU': 'Océanie',
    'NZ': 'Océanie',
    'PG': 'Océanie',
    'FJ': 'Océanie',
    'SB': 'Océanie',
    'VU': 'Océanie',
    'NC': 'Océanie',
    'PF': 'Océanie',
    'WS': 'Océanie',
    'TO': 'Océanie',
    'KI': 'Océanie',
}

def get_region(country_code):
    """
    Retourne la région pour un code pays donné
    
    :param country_code: code pays ISO-2 (ex: 'FR', 'US')
    :returns str : Nom de la région ou 'Autre' si non trouvé
    return REGION_MAPPING.get(country_code, 'Autre')
    """

    return REGION_MAPPING.get(country_code, 'Autre')
        

def calculate_years_lost(pm25_concentration, seuil=5):
    """
    Calcule les années d'espérance de vie perdues selon la méthode AQLI
    
    :param pm25_concentration: Concentration de PM2.5 en µg/m³
    :param seuil: Seuil OMS (par défaut 5 µg/m³)
    
    :returns round(years_lost, 2): Nombre d'années perdues (0 si en-dessous du seuil)
    """

    if pm25_concentration <= seuil:
        return 0
    
    exces = pm25_concentration - seuil
    annee_perdue = exces * 0.098
    
    return round(annee_perdue, 2)