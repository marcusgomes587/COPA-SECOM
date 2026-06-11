FLAG_EMOJI: dict[str, str] = {
    # Grupo A
    "México": "🇲🇽", "África do Sul": "🇿🇦",
    "Coreia do Sul": "🇰🇷", "Tchéquia": "🇨🇿",
    # Grupo B
    "Canadá": "🇨🇦", "Bósnia e Herzegovina": "🇧🇦",
    "Catar": "🇶🇦", "Suíça": "🇨🇭",
    # Grupo C
    "Brasil": "🇧🇷", "Marrocos": "🇲🇦",
    "Haiti": "🇭🇹", "Escócia": "🏴󠁧󠁢󠁳󠁣󠁴󠁿",
    # Grupo D
    "Estados Unidos": "🇺🇸", "Paraguai": "🇵🇾",
    "Austrália": "🇦🇺", "Turquia": "🇹🇷",
    # Grupo E
    "Alemanha": "🇩🇪", "Curaçao": "🇨🇼",
    "Costa do Marfim": "🇨🇮", "Equador": "🇪🇨",
    # Grupo F
    "Holanda": "🇳🇱", "Japão": "🇯🇵",
    "Suécia": "🇸🇪", "Tunísia": "🇹🇳",
    # Grupo G
    "Bélgica": "🇧🇪", "Egito": "🇪🇬",
    "Irã": "🇮🇷", "Nova Zelândia": "🇳🇿",
    # Grupo H
    "Espanha": "🇪🇸", "Cabo Verde": "🇨🇻",
    "Arábia Saudita": "🇸🇦", "Uruguai": "🇺🇾",
    # Grupo I
    "França": "🇫🇷", "Senegal": "🇸🇳",
    "Iraque": "🇮🇶", "Noruega": "🇳🇴",
    # Grupo J
    "Argentina": "🇦🇷", "Argélia": "🇩🇿",
    "Áustria": "🇦🇹", "Jordânia": "🇯🇴",
    # Grupo K
    "Portugal": "🇵🇹", "RD Congo": "🇨🇩",
    "Uzbequistão": "🇺🇿", "Colômbia": "🇨🇴",
    # Grupo L
    "Inglaterra": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "Croácia": "🇭🇷",
    "Gana": "🇬🇭", "Panamá": "🇵🇦",
    # Genéricos
    "A Definir": "🏳️",
}

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


def get_flag(team: str) -> str:
    return FLAG_EMOJI.get(team, "")
