MATCH_GROUP: dict[int, str] = {
    1001: "A", 1002: "A", 1025: "A", 1028: "A", 1053: "A", 1054: "A",
    1003: "B", 1005: "B", 1026: "B", 1027: "B", 1049: "B", 1050: "B",
    1006: "C", 1007: "C", 1030: "C", 1031: "C", 1051: "C", 1052: "C",
    1004: "D", 1008: "D", 1029: "D", 1032: "D", 1059: "D", 1060: "D",
    1009: "E", 1011: "E", 1034: "E", 1035: "E", 1055: "E", 1056: "E",
    1010: "F", 1012: "F", 1033: "F", 1036: "F", 1057: "F", 1058: "F",
    1014: "G", 1016: "G", 1038: "G", 1040: "G", 1065: "G", 1066: "G",
    1013: "H", 1015: "H", 1037: "H", 1039: "H", 1063: "H", 1064: "H",
    1017: "I", 1018: "I", 1042: "I", 1043: "I", 1061: "I", 1062: "I",
    1019: "J", 1020: "J", 1041: "J", 1044: "J", 1071: "J", 1072: "J",
    1021: "K", 1024: "K", 1045: "K", 1048: "K", 1069: "K", 1070: "K",
    1022: "L", 1023: "L", 1046: "L", 1047: "L", 1067: "L", 1068: "L",
}

# ISO 3166-1 alpha-2 por nome do time (em portugues)
TEAM_ISO: dict[str, str] = {
    "Brasil": "BR", "Argentina": "AR", "Uruguai": "UY", "Colômbia": "CO",
    "Equador": "EC", "Paraguai": "PY", "Peru": "PE", "Chile": "CL",
    "Bolívia": "BO", "Venezuela": "VE",
    "Estados Unidos": "US", "México": "MX", "Canadá": "CA",
    "Honduras": "HN", "Costa Rica": "CR", "Panamá": "PA",
    "Jamaica": "JM", "Haiti": "HT", "El Salvador": "SV", "Curaçao": "CW",
    "França": "FR", "Inglaterra": "GB", "Alemanha": "DE", "Espanha": "ES",
    "Portugal": "PT", "Holanda": "NL", "Bélgica": "BE", "Itália": "IT",
    "Croácia": "HR", "Polônia": "PL", "Suíça": "CH", "Dinamarca": "DK",
    "Noruega": "NO", "Áustria": "AT", "Turquia": "TR", "Ucrânia": "UA",
    "Sérvia": "RS", "Eslováquia": "SK", "Eslovênia": "SI", "Albânia": "AL",
    "Geórgia": "GE", "Escócia": "GB", "Gales": "GB", "Hungria": "HU",
    "Tchéquia": "CZ", "Romênia": "RO", "Grécia": "GR", "Suécia": "SE",
    "Bósnia e Herzegovina": "BA",
    "Marrocos": "MA", "Senegal": "SN", "Nigéria": "NG", "Egito": "EG",
    "Camarões": "CM", "Gana": "GH", "Costa do Marfim": "CI", "Mali": "ML",
    "Tunísia": "TN", "Argélia": "DZ", "África do Sul": "ZA",
    "RD Congo": "CD", "Cabo Verde": "CV",
    "Japão": "JP", "Coreia do Sul": "KR", "Arábia Saudita": "SA",
    "Irã": "IR", "Austrália": "AU", "Catar": "QA", "Uzbequistão": "UZ",
    "Jordânia": "JO", "Iraque": "IQ", "Nova Zelândia": "NZ",
}

# URLs Twemoji especiais para bandeiras de sub-regioes do Reino Unido
_SPECIAL: dict[str, str] = {
    "Escócia": "https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/svg/1f3f4-e0067-e0062-e0073-e0063-e0074-e007f.svg",
    "Inglaterra": "https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/svg/1f3f4-e0067-e0062-e0065-e006e-e0067-e007f.svg",
    "Gales": "https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/svg/1f3f4-e0067-e0062-e0077-e006c-e0073-e007f.svg",
}


def _twemoji_url(iso2: str) -> str:
    """Gera URL do SVG Twemoji a partir de um codigo ISO-2."""
    base = 0x1F1E6
    parts = [format(base + ord(c) - 65, 'x') for c in iso2.upper()]
    return f"https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/svg/{'-'.join(parts)}.svg"


def flag_img(team: str, size: int = 28) -> str:
    """Retorna tag <img> com a bandeira do time via Twemoji (funciona no Windows)."""
    if team in _SPECIAL:
        url = _SPECIAL[team]
    else:
        iso = TEAM_ISO.get(team, "")
        if not iso:
            return ""
        url = _twemoji_url(iso)
    return (
        f'<img src="{url}" width="{size}" height="{size}" '
        f'style="border-radius:3px;vertical-align:middle;margin:0 6px" '
        f'onerror="this.style.display=\'none\'">'
    )


def get_flag(team: str) -> str:
    """Alias mantido para compatibilidade."""
    return flag_img(team)
