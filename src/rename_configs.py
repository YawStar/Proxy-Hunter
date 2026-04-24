import json
import base64
import sys
import os
from typing import Dict, Optional, List, Tuple
from urllib.parse import urlparse, parse_qs, unquote
import logging
import re
import binascii
import config_parser as parser

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

COUNTRY_CODES = {
    'Afghanistan': 'AF', 'Albania': 'AL', 'Algeria': 'DZ', 'Andorra': 'AD', 'Angola': 'AO',
    'Antigua and Barbuda': 'AG', 'Argentina': 'AR', 'Armenia': 'AM', 'Australia': 'AU', 'Austria': 'AT',
    'Azerbaijan': 'AZ', 'Bahamas': 'BS', 'Bahrain': 'BH', 'Bangladesh': 'BD', 'Barbados': 'BB',
    'Belarus': 'BY', 'Belgium': 'BE', 'Belize': 'BZ', 'Benin': 'BJ', 'Bhutan': 'BT',
    'Bolivia': 'BO', 'Bosnia and Herzegovina': 'BA', 'Botswana': 'BW', 'Brazil': 'BR', 'Brunei': 'BN',
    'Bulgaria': 'BG', 'Burkina Faso': 'BF', 'Burundi': 'BI', 'Cambodia': 'KH', 'Cameroon': 'CM',
    'Canada': 'CA', 'Cape Verde': 'CV', 'Central African Republic': 'CF', 'Chad': 'TD', 'Chile': 'CL',
    'China': 'CN', 'Colombia': 'CO', 'Comoros': 'KM', 'Congo': 'CG', 'Costa Rica': 'CR',
    'Croatia': 'HR', 'Cuba': 'CU', 'Cyprus': 'CY', 'Czech Republic': 'CZ', 'Czechia': 'CZ',
    'Denmark': 'DK', 'Djibouti': 'DJ', 'Dominica': 'DM', 'Dominican Republic': 'DO', 'East Timor': 'TL',
    'Ecuador': 'EC', 'Egypt': 'EG', 'El Salvador': 'SV', 'Equatorial Guinea': 'GQ', 'Eritrea': 'ER',
    'Estonia': 'EE', 'Ethiopia': 'ET', 'Fiji': 'FJ', 'Finland': 'FI', 'France': 'FR',
    'Gabon': 'GA', 'Gambia': 'GM', 'Georgia': 'GE', 'Germany': 'DE', 'Ghana': 'GH',
    'Greece': 'GR', 'Grenada': 'GD', 'Guatemala': 'GT', 'Guinea': 'GN', 'Guinea-Bissau': 'GW',
    'Guyana': 'GY', 'Haiti': 'HT', 'Honduras': 'HN', 'Hungary': 'HU', 'Iceland': 'IS',
    'India': 'IN', 'Indonesia': 'ID', 'Iran': 'IR', 'Iraq': 'IQ', 'Ireland': 'IE',
    'Israel': 'IL', 'Italy': 'IT', 'Ivory Coast': 'CI', 'Jamaica': 'JM', 'Japan': 'JP',
    'Jordan': 'JO', 'Kazakhstan': 'KZ', 'Kenya': 'KE', 'Kiribati': 'KI', 'North Korea': 'KP',
    'South Korea': 'KR', 'Kosovo': 'XK', 'Kuwait': 'KW', 'Kyrgyzstan': 'KG', 'Laos': 'LA',
    'Latvia': 'LV', 'Lebanon': 'LB', 'Lesotho': 'LS', 'Liberia': 'LR', 'Libya': 'LY',
    'Liechtenstein': 'LI', 'Lithuania': 'LT', 'Luxembourg': 'LU', 'Macedonia': 'MK', 'Madagascar': 'MG',
    'Malawi': 'MW', 'Malaysia': 'MY', 'Maldives': 'MV', 'Mali': 'ML', 'Malta': 'MT',
    'Marshall Islands': 'MH', 'Mauritania': 'MR', 'Mauritius': 'MU', 'Mexico': 'MX', 'Micronesia': 'FM',
    'Moldova': 'MD', 'Monaco': 'MC', 'Mongolia': 'MN', 'Montenegro': 'ME', 'Morocco': 'MA',
    'Mozambique': 'MZ', 'Myanmar': 'MM', 'Namibia': 'NA', 'Nauru': 'NR', 'Nepal': 'NP',
    'Netherlands': 'NL', 'New Zealand': 'NZ', 'Nicaragua': 'NI', 'Niger': 'NE', 'Nigeria': 'NG',
    'Norway': 'NO', 'Oman': 'OM', 'Pakistan': 'PK', 'Palau': 'PW', 'Palestine': 'PS',
    'Panama': 'PA', 'Papua New Guinea': 'PG', 'Paraguay': 'PY', 'Peru': 'PE', 'Philippines': 'PH',
    'Poland': 'PL', 'Portugal': 'PT', 'Puerto Rico': 'PR', 'Qatar': 'QA', 'Romania': 'RO',
    'Russia': 'RU', 'Rwanda': 'RW', 'Saint Kitts and Nevis': 'KN', 'Saint Lucia': 'LC',
    'Saint Vincent': 'VC', 'Samoa': 'WS', 'San Marino': 'SM', 'Sao Tome and Principe': 'ST',
    'Saudi Arabia': 'SA', 'Senegal': 'SN', 'Serbia': 'RS', 'Seychelles': 'SC', 'Sierra Leone': 'SL',
    'Singapore': 'SG', 'Slovakia': 'SK', 'Slovenia': 'SI', 'Solomon Islands': 'SB', 'Somalia': 'SO',
    'South Africa': 'ZA', 'South Sudan': 'SS', 'Spain': 'ES', 'Sri Lanka': 'LK', 'Sudan': 'SD',
    'Suriname': 'SR', 'Swaziland': 'SZ', 'Sweden': 'SE', 'Switzerland': 'CH', 'Syria': 'SY',
    'Taiwan': 'TW', 'Tajikistan': 'TJ', 'Tanzania': 'TZ', 'Thailand': 'TH', 'Togo': 'TG',
    'Tonga': 'TO', 'Trinidad and Tobago': 'TT', 'Tunisia': 'TN', 'Turkey': 'TR', 'Turkiye': 'TR',
    'Turkmenistan': 'TM', 'Tuvalu': 'TV', 'Uganda': 'UG', 'Ukraine': 'UA', 'United Arab Emirates': 'AE',
    'UAE': 'AE', 'United Kingdom': 'GB', 'UK': 'GB', 'United States': 'US', 'USA': 'US',
    'Uruguay': 'UY', 'Uzbekistan': 'UZ', 'Vanuatu': 'VU', 'Vatican City': 'VA', 'Venezuela': 'VE',
    'Vietnam': 'VN', 'Viet Nam': 'VN', 'Yemen': 'YE', 'Zambia': 'ZM', 'Zimbabwe': 'ZW',
    'Hong Kong': 'HK', 'Macao': 'MO', 'Macau': 'MO', 'Greenland': 'GL', 'Faroe Islands': 'FO',
    'French Guiana': 'GF', 'French Polynesia': 'PF', 'Guadeloupe': 'GP', 'Martinique': 'MQ',
    'Reunion': 'RE', 'Mayotte': 'YT', 'New Caledonia': 'NC', 'Guam': 'GU', 'American Samoa': 'AS',
    'Northern Mariana Islands': 'MP', 'US Virgin Islands': 'VI', 'British Virgin Islands': 'VG',
    'Cayman Islands': 'KY', 'Bermuda': 'BM', 'Turks and Caicos': 'TC', 'Aruba': 'AW',
    'Curacao': 'CW', 'Sint Maarten': 'SX', 'Bonaire': 'BQ', 'Anguilla': 'AI', 'Montserrat': 'MS',
    'Gibraltar': 'GI', 'Jersey': 'JE', 'Guernsey': 'GG', 'Isle of Man': 'IM', 'Aland Islands': 'AX',
    'Svalbard': 'SJ', 'Cook Islands': 'CK', 'Niue': 'NU', 'Tokelau': 'TK', 'Pitcairn Islands': 'PN',
    'Saint Helena': 'SH', 'Falkland Islands': 'FK', 'South Georgia': 'GS', 'Bouvet Island': 'BV',
    'Heard Island': 'HM', 'Christmas Island': 'CX', 'Cocos Islands': 'CC', 'Norfolk Island': 'NF',
    'Western Sahara': 'EH', 'Antarctica': 'AQ',
    'United States of America': 'US', 'Kingdom of the Netherlands': 'NL', 'The Netherlands': 'NL',
    'Holland': 'NL', 'United Kingdom of Great Britain and Northern Ireland': 'GB',
    'Taiwan (Province of China)': 'TW', 'Republic of Korea': 'KR', 'Korea': 'KR',
    'Democratic Republic of the Congo': 'CD', 'Republic of the Congo': 'CG', 'DR Congo': 'CD',
    'Congo-Kinshasa': 'CD', 'Congo-Brazzaville': 'CG', 'Timor-Leste': 'TL',
    'Unknown': 'XX'
}

FLAG_TO_CODE = {
    '🇦🇫': 'AF', '🇦🇱': 'AL', '🇩🇿': 'DZ', '🇦🇩': 'AD', '🇦🇴': 'AO',
    '🇦🇬': 'AG', '🇦🇷': 'AR', '🇦🇲': 'AM', '🇦🇺': 'AU', '🇦🇹': 'AT',
    '🇦🇿': 'AZ', '🇧🇸': 'BS', '🇧🇭': 'BH', '🇧🇩': 'BD', '🇧🇧': 'BB',
    '🇧🇾': 'BY', '🇧🇪': 'BE', '🇧🇿': 'BZ', '🇧🇯': 'BJ', '🇧🇹': 'BT',
    '🇧🇴': 'BO', '🇧🇦': 'BA', '🇧🇼': 'BW', '🇧🇷': 'BR', '🇧🇳': 'BN',
    '🇧🇬': 'BG', '🇧🇫': 'BF', '🇧🇮': 'BI', '🇰🇭': 'KH', '🇨🇲': 'CM',
    '🇨🇦': 'CA', '🇨🇻': 'CV', '🇨🇫': 'CF', '🇹🇩': 'TD', '🇨🇱': 'CL',
    '🇨🇳': 'CN', '🇨🇴': 'CO', '🇰🇲': 'KM', '🇨🇬': 'CG', '🇨🇷': 'CR',
    '🇭🇷': 'HR', '🇨🇺': 'CU', '🇨🇾': 'CY', '🇨🇿': 'CZ', '🇩🇰': 'DK',
    '🇩🇯': 'DJ', '🇩🇲': 'DM', '🇩🇴': 'DO', '🇹🇱': 'TL', '🇪🇨': 'EC',
    '🇪🇬': 'EG', '🇸🇻': 'SV', '🇬🇶': 'GQ', '🇪🇷': 'ER', '🇪🇪': 'EE',
    '🇪🇹': 'ET', '🇫🇯': 'FJ', '🇫🇮': 'FI', '🇫🇷': 'FR', '🇬🇦': 'GA',
    '🇬🇲': 'GM', '🇬🇪': 'GE', '🇩🇪': 'DE', '🇬🇭': 'GH', '🇬🇷': 'GR',
    '🇬🇩': 'GD', '🇬🇹': 'GT', '🇬🇳': 'GN', '🇬🇼': 'GW', '🇬🇾': 'GY',
    '🇭🇹': 'HT', '🇭🇳': 'HN', '🇭🇺': 'HU', '🇮🇸': 'IS', '🇮🇳': 'IN',
    '🇮🇩': 'ID', '🇮🇷': 'IR', '🇮🇶': 'IQ', '🇮🇪': 'IE', '🇮🇱': 'IL',
    '🇮🇹': 'IT', '🇨🇮': 'CI', '🇯🇲': 'JM', '🇯🇵': 'JP', '🇯🇴': 'JO',
    '🇰🇿': 'KZ', '🇰🇪': 'KE', '🇰🇮': 'KI', '🇰🇵': 'KP', '🇰🇷': 'KR',
    '🇽🇰': 'XK', '🇰🇼': 'KW', '🇰🇬': 'KG', '🇱🇦': 'LA', '🇱🇻': 'LV',
    '🇱🇧': 'LB', '🇱🇸': 'LS', '🇱🇷': 'LR', '🇱🇾': 'LY', '🇱🇮': 'LI',
    '🇱🇹': 'LT', '🇱🇺': 'LU', '🇲🇰': 'MK', '🇲🇬': 'MG', '🇲🇼': 'MW',
    '🇲🇾': 'MY', '🇲🇻': 'MV', '🇲🇱': 'ML', '🇲🇹': 'MT', '🇲🇭': 'MH',
    '🇲🇷': 'MR', '🇲🇺': 'MU', '🇲🇽': 'MX', '🇫🇲': 'FM', '🇲🇩': 'MD',
    '🇲🇨': 'MC', '🇲🇳': 'MN', '🇲🇪': 'ME', '🇲🇦': 'MA', '🇲🇿': 'MZ',
    '🇲🇲': 'MM', '🇳🇦': 'NA', '🇳🇷': 'NR', '🇳🇵': 'NP', '🇳🇱': 'NL',
    '🇳🇿': 'NZ', '🇳🇮': 'NI', '🇳🇪': 'NE', '🇳🇬': 'NG', '🇳🇴': 'NO',
    '🇴🇲': 'OM', '🇵🇰': 'PK', '🇵🇼': 'PW', '🇵🇸': 'PS', '🇵🇦': 'PA',
    '🇵🇬': 'PG', '🇵🇾': 'PY', '🇵🇪': 'PE', '🇵🇭': 'PH', '🇵🇱': 'PL',
    '🇵🇹': 'PT', '🇵🇷': 'PR', '🇶🇦': 'QA', '🇷🇴': 'RO', '🇷🇺': 'RU',
    '🇷🇼': 'RW', '🇰🇳': 'KN', '🇱🇨': 'LC', '🇻🇨': 'VC', '🇼🇸': 'WS',
    '🇸🇲': 'SM', '🇸🇹': 'ST', '🇸🇦': 'SA', '🇸🇳': 'SN', '🇷🇸': 'RS',
    '🇸🇨': 'SC', '🇸🇱': 'SL', '🇸🇬': 'SG', '🇸🇰': 'SK', '🇸🇮': 'SI',
    '🇸🇧': 'SB', '🇸🇴': 'SO', '🇿🇦': 'ZA', '🇸🇸': 'SS', '🇪🇸': 'ES',
    '🇱🇰': 'LK', '🇸🇩': 'SD', '🇸🇷': 'SR', '🇸🇿': 'SZ', '🇸🇪': 'SE',
    '🇨🇭': 'CH', '🇸🇾': 'SY', '🇹🇼': 'TW', '🇹🇯': 'TJ', '🇹🇿': 'TZ',
    '🇹🇭': 'TH', '🇹🇬': 'TG', '🇹🇴': 'TO', '🇹🇹': 'TT', '🇹🇳': 'TN',
    '🇹🇷': 'TR', '🇹🇲': 'TM', '🇹🇻': 'TV', '🇺🇬': 'UG', '🇺🇦': 'UA',
    '🇦🇪': 'AE', '🇬🇧': 'GB', '🇺🇸': 'US', '🇺🇾': 'UY', '🇺🇿': 'UZ',
    '🇻🇺': 'VU', '🇻🇦': 'VA', '🇻🇪': 'VE', '🇻🇳': 'VN', '🇾🇪': 'YE',
    '🇿🇲': 'ZM', '🇿🇼': 'ZW', '🇭🇰': 'HK', '🇲🇴': 'MO', '🇨🇩': 'CD',
    '🇬🇱': 'GL', '🇫🇴': 'FO', '🇬🇫': 'GF', '🇵🇫': 'PF', '🇬🇵': 'GP',
    '🇲🇶': 'MQ', '🇷🇪': 'RE', '🇾🇹': 'YT', '🇳🇨': 'NC', '🇬🇺': 'GU',
    '🇦🇸': 'AS', '🇲🇵': 'MP', '🇻🇮': 'VI', '🇻🇬': 'VG', '🇰🇾': 'KY',
    '🇧🇲': 'BM', '🇹🇨': 'TC', '🇦🇼': 'AW', '🇨🇼': 'CW', '🇸🇽': 'SX',
    '🇧🇶': 'BQ', '🇦🇮': 'AI', '🇲🇸': 'MS', '🇬🇮': 'GI', '🇯🇪': 'JE',
    '🇬🇬': 'GG', '🇮🇲': 'IM', '🇦🇽': 'AX', '🇸🇯': 'SJ', '🇨🇰': 'CK',
    '🇳🇺': 'NU', '🇹🇰': 'TK', '🇵🇳': 'PN', '🇸🇭': 'SH', '🇫🇰': 'FK',
    '🇬🇸': 'GS', '🇧🇻': 'BV', '🇭🇲': 'HM', '🇨🇽': 'CX', '🇨🇨': 'CC',
    '🇳🇫': 'NF', '🇪🇭': 'EH', '🇦🇶': 'AQ', '🏳️': 'XX'
}

class ConfigRenamer:
    def __init__(self, location_file: str):
        self.location_cache: Dict[str, Tuple] = {}
        self.load_location_cache(location_file)
        self.normalized_country_codes = {str(k).lower().strip(): v for k, v in COUNTRY_CODES.items()}

    def load_location_cache(self, location_file: str):
        try:
            with open(location_file, 'r', encoding='utf-8') as f:
                raw_cache = json.load(f)
                for key, value in raw_cache.items():
                    if isinstance(value, (list, tuple)) and len(value) >= 2:
                        self.location_cache[key] = tuple(value[:2])
                    else:
                        logger.warning(f"Invalid cache entry for {key}: {value}")
            logger.info(f"Loaded {len(self.location_cache)} location entries from cache")
        except FileNotFoundError:
            logger.error(f"{location_file} not found!")
        except Exception as e:
            logger.error(f"Error loading location cache: {e}")

    def get_country_code_from_flag(self, flag: str) -> str:
        return FLAG_TO_CODE.get(flag, 'XX')

    def get_country_code_from_name(self, country_name: str) -> str:
        if not country_name:
            return 'XX'
        country_lower = str(country_name).lower().strip()
        code = self.normalized_country_codes.get(country_lower)
        if code:
            return code
        if len(country_name) == 2 and country_name.isupper():
            return country_name
        for pattern in ['the ', 'republic of ', 'kingdom of ']:
            if country_lower.startswith(pattern):
                clean_name = country_lower[len(pattern):]
                code = self.normalized_country_codes.get(clean_name)
                if code:
                    return code
        return 'XX'

    def get_location(self, address: str) -> Tuple[str, str]:
        if not address:
            return "🏳️", "XX"
        if address in self.location_cache:
            cache_entry = self.location_cache[address]
            flag = str(cache_entry[0]) if cache_entry[0] else "🏳️"
            country = str(cache_entry[1]) if cache_entry[1] else ""
            country_code = self.get_country_code_from_flag(flag)
            if country_code == 'XX' and country:
                country_code = self.get_country_code_from_name(country)
            return flag, country_code
        return "🏳️", "XX"

    def build_protocol_info(self, protocol_type: str, data: Dict) -> List[str]:
        info_parts = [protocol_type]
        
        if protocol_type == "VMess":
            net_type = data.get('net', 'tcp').lower()
            tls = data.get('tls', 'none').lower()
            
            if net_type == 'ws':
                info_parts.append('WS')
            elif net_type == 'grpc':
                info_parts.append('GRPC')
            elif net_type in ('http', 'h2'):
                info_parts.append('HTTP2')
            elif net_type == 'quic':
                info_parts.append('QUIC')
            elif net_type == 'kcp':
                info_parts.append('KCP')
            elif net_type == 'splithttp':
                info_parts.append('SPLITHTTP')
            elif net_type == 'xhttp':
                info_parts.append('XHTTP')
            elif net_type == 'httpupgrade':
                info_parts.append('HTTPUPGRADE')
            
            if tls == 'tls':
                info_parts.append('TLS')
            
            if data.get('fp'):
                info_parts.append('UTLS')
        
        elif protocol_type == "VLESS":
            transport_type = data.get('type', 'tcp').lower()
            security = data.get('security', 'none').lower()
            flow = data.get('flow', '').lower()
            
            if transport_type == 'ws':
                info_parts.append('WS')
            elif transport_type == 'grpc':
                info_parts.append('GRPC')
            elif transport_type in ('http', 'h2'):
                info_parts.append('HTTP2')
            elif transport_type == 'quic':
                info_parts.append('QUIC')
            elif transport_type == 'kcp':
                info_parts.append('KCP')
            elif transport_type == 'splithttp':
                info_parts.append('SPLITHTTP')
            elif transport_type == 'xhttp':
                info_parts.append('XHTTP')
            elif transport_type == 'httpupgrade':
                info_parts.append('HTTPUPGRADE')
            elif transport_type == 'raw':
                info_parts.append('RAW')

            if security == 'reality':
                info_parts.append('REALITY')
                if data.get('pbk'):
                    info_parts.append('PBK')
                if data.get('sid'):
                    info_parts.append('SID')
            elif security == 'tls':
                info_parts.append('TLS')
            elif security == 'xtls':
                info_parts.append('XTLS')
            
            if 'vision' in flow:
                info_parts.append('VISION')
            elif 'xtls-rprx-direct' in flow:
                info_parts.append('DIRECT')
            elif 'xtls' in flow:
                info_parts.append('XTLS-FLOW')
            
            if data.get('fp'):
                info_parts.append('UTLS')
        
        elif protocol_type == "Trojan":
            transport_type = data.get('type', 'tcp').lower()
            flow = data.get('flow', '').lower()
            
            if transport_type == 'ws':
                info_parts.append('WS')
            elif transport_type == 'grpc':
                info_parts.append('GRPC')
            elif transport_type == 'quic':
                info_parts.append('QUIC')
            elif transport_type == 'kcp':
                info_parts.append('KCP')
            elif transport_type == 'splithttp':
                info_parts.append('SPLITHTTP')
            elif transport_type == 'xhttp':
                info_parts.append('XHTTP')
            elif transport_type == 'httpupgrade':
                info_parts.append('HTTPUPGRADE')
            elif transport_type in ('http', 'h2'):
                info_parts.append('HTTP2')
                
            info_parts.append('TLS')
            
            if 'vision' in flow:
                info_parts.append('VISION')
            elif 'xtls' in flow:
                info_parts.append('XTLS')
            
            if data.get('fp'):
                info_parts.append('UTLS')
        
        elif protocol_type == "Hysteria2":
            info_parts.append('QUIC')
            obfs = data.get('obfs', '')
            if obfs:
                info_parts.append('OBFS')
        
        elif protocol_type == "SS":
            method = data.get('method', '').lower()
            if '2022' in method:
                info_parts.append('2022')
                if 'blake3' in method:
                    info_parts.append('BLAKE3')
            elif 'gcm' in method or 'poly1305' in method:
                info_parts.append('AEAD')
            else:
                info_parts.append('STREAM')
        
        return info_parts

    def rename_config(self, config: str, index: int, protocol_type: str) -> Optional[str]:
        try:
            config_lower = config.lower()
            
            if config_lower.startswith('vmess://'):
                data = parser.decode_vmess(config)
                if not data or not all(k in data for k in ['add', 'port', 'id']):
                    logger.warning(f"Could not parse VMess config at index {index}")
                    return config
                flag, country_code = self.get_location(data['add'])
                protocol_info = self.build_protocol_info(protocol_type, data)
                protocol_str = '/'.join(protocol_info)
                new_name = f"{flag} {index} - {country_code} - {protocol_str} - {data['port']}"
                data['ps'] = new_name
                encoded = base64.b64encode(json.dumps(data, ensure_ascii=False).encode('utf-8')).decode('utf-8')
                return f"vmess://{encoded}"
            
            elif config_lower.startswith('vless://'):
                data = parser.parse_vless(config)
                if not data:
                    logger.warning(f"Could not parse VLESS config at index {index}")
                    return config
                flag, country_code = self.get_location(data['address'])
                protocol_info = self.build_protocol_info(protocol_type, data)
                protocol_str = '/'.join(protocol_info)
                new_name = f"{flag} {index} - {country_code} - {protocol_str} - {data['port']}"
                url = urlparse(config)
                params = parse_qs(url.query)
                query_parts = []
                for k, v in params.items():
                    if isinstance(v, list) and v:
                        query_parts.append(f"{k}={v[0]}")
                query_string = '&'.join(query_parts)
                new_config = f"vless://{data['uuid']}@{data['address']}:{data['port']}?{query_string}#{new_name}"
                return new_config
            
            elif config_lower.startswith('trojan://'):
                data = parser.parse_trojan(config)
                if not data:
                    logger.warning(f"Could not parse Trojan config at index {index}")
                    return config
                flag, country_code = self.get_location(data['address'])
                protocol_info = self.build_protocol_info(protocol_type, data)
                protocol_str = '/'.join(protocol_info)
                new_name = f"{flag} {index} - {country_code} - {protocol_str} - {data['port']}"
                url = urlparse(config)
                params = parse_qs(url.query)
                query_parts = []
                for k, v in params.items():
                    if isinstance(v, list) and v:
                        query_parts.append(f"{k}={v[0]}")
                query_string = '&'.join(query_parts)
                new_config = f"trojan://{data['password']}@{data['address']}:{data['port']}?{query_string}#{new_name}"
                return new_config
            
            elif config_lower.startswith(('hysteria2://', 'hy2://')):
                data = parser.parse_hysteria2(config)
                if not data:
                    logger.warning(f"Could not parse Hysteria2 config at index {index}")
                    return config
                flag, country_code = self.get_location(data['address'])
                protocol_info = self.build_protocol_info(protocol_type, data)
                protocol_str = '/'.join(protocol_info)
                new_name = f"{flag} {index} - {country_code} - {protocol_str} - {data['port']}"
                url = urlparse(config)
                query_string = url.query
                protocol = 'hysteria2' if config_lower.startswith('hysteria2://') else 'hy2'
                new_config = f"{protocol}://{data['password']}@{data['address']}:{data['port']}?{query_string}#{new_name}"
                return new_config
            
            elif config_lower.startswith('ss://'):
                data = parser.parse_shadowsocks(config)
                if not data:
                    logger.warning(f"Could not parse Shadowsocks config at index {index}")
                    return config
                flag, country_code = self.get_location(data['address'])
                protocol_info = self.build_protocol_info(protocol_type, data)
                protocol_str = '/'.join(protocol_info)
                new_name = f"{flag} {index} - {country_code} - {protocol_str} - {data['port']}"
                method_pass = f"{data['method']}:{data['password']}"
                encoded = base64.b64encode(method_pass.encode('utf-8')).decode('utf-8').replace('+', '-').replace('/', '_').rstrip('=')
                new_config = f"ss://{encoded}@{data['address']}:{data['port']}#{new_name}"
                return new_config
            
            return config
        except Exception as e:
            logger.error(f"Failed to rename config at index {index}: {e}")
            return config

    def process_configs(self, input_file: str, output_file: str):
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except FileNotFoundError:
            logger.error(f"{input_file} not found!")
            return
        except Exception as e:
            logger.error(f"Error reading {input_file}: {e}")
            return

        renamed_configs = []
        header_lines = []
        configs = []
        
        for line in lines:
            line = line.strip()
            if line.startswith('//') or not line:
                if not configs:
                    header_lines.append(line)
            else:
                configs.append(line)

        counters = {"VLESS": 1, "Trojan": 1, "VMess": 1, "SS": 1, "Hysteria2": 1}
        protocol_map = {'vless': 'VLESS', 'trojan': 'Trojan', 'vmess': 'VMess', 'ss': 'SS', 'hysteria2': 'Hysteria2', 'hy2': 'Hysteria2'}

        for config in configs:
            protocol_key = config.split('://')[0].lower()
            protocol_name = protocol_map.get(protocol_key)
            
            if protocol_name:
                renamed = self.rename_config(config, counters[protocol_name], protocol_name)
                if renamed:
                    renamed_configs.append(renamed)
                    counters[protocol_name] += 1
                else:
                    logger.warning(f"Could not parse or rename config, appending as-is: {config[:40]}...")
                    renamed_configs.append(config)
            else:
                renamed_configs.append(config)

        try:
            os.makedirs(os.path.dirname(output_file) or '.', exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                for header in header_lines:
                    f.write(header + '\n')
                if header_lines and renamed_configs:
                    f.write('\n')
                for config in renamed_configs:
                    f.write(config + '\n\n')
            logger.info(f"Successfully renamed {len(renamed_configs)} configs and saved to {output_file}")
        except IOError as e:
            logger.error(f"Failed to write output file: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")


def main():
    if len(sys.argv) < 4:
        print("Usage: python rename_configs.py <location.json> <input.txt> <output.txt>")
        sys.exit(1)
    
    location_file = sys.argv[1]
    input_file = sys.argv[2]
    output_file = sys.argv[3]

    renamer = ConfigRenamer(location_file)
    renamer.process_configs(input_file, output_file)

if __name__ == '__main__':
    main()