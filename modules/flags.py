TEAM_FLAGS: dict[str, str] = {
    # Americas
    "Brasil": "br", "Brazil": "br",
    "Argentina": "ar",
    "Uruguai": "uy", "Uruguay": "uy",
    "Colombia": "co", "Colômbia": "co",
    "Equador": "ec", "Ecuador": "ec",
    "Peru": "pe",
    "Chile": "cl",
    "Paraguai": "py", "Paraguay": "py",
    "Bolivia": "bo", "Bolívia": "bo",
    "Venezuela": "ve",
    "Estados Unidos": "us", "USA": "us", "EUA": "us", "United States": "us",
    "México": "mx", "Mexico": "mx",
    "Canadá": "ca", "Canada": "ca",
    "Honduras": "hn",
    "Costa Rica": "cr",
    "Panamá": "pa", "Panama": "pa",
    "Jamaica": "jm",
    "Haiti": "ht",
    "Trinidad e Tobago": "tt",
    "El Salvador": "sv",
    "Curaçao": "cw", "Curacao": "cw",

    # Europa
    "França": "fr", "France": "fr",
    "Inglaterra": "gb-eng", "England": "gb-eng",
    "Alemanha": "de", "Germany": "de",
    "Espanha": "es", "Spain": "es",
    "Portugal": "pt",
    "Holanda": "nl", "Netherlands": "nl",
    "Bélgica": "be", "Belgium": "be",
    "Itália": "it", "Italy": "it",
    "Croácia": "hr", "Croatia": "hr",
    "Polônia": "pl", "Poland": "pl",
    "Suíça": "ch", "Switzerland": "ch",
    "Dinamarca": "dk", "Denmark": "dk",
    "Noruega": "no", "Norway": "no",
    "Áustria": "at", "Austria": "at",
    "Turquia": "tr", "Turkey": "tr",
    "Ucrânia": "ua", "Ukraine": "ua",
    "Sérvia": "rs", "Serbia": "rs",
    "Eslováquia": "sk", "Slovakia": "sk",
    "Eslovênia": "si", "Slovenia": "si",
    "Albânia": "al", "Albania": "al",
    "Geórgia": "ge", "Georgia": "ge",
    "Escócia": "gb-sct", "Scotland": "gb-sct",
    "Gales": "gb-wls", "Wales": "gb-wls",
    "Hungria": "hu", "Hungary": "hu",
    "Tchéquia": "cz", "Czech Republic": "cz",
    "Romênia": "ro", "Romania": "ro",
    "Grécia": "gr", "Greece": "gr",
    "Suécia": "se", "Sweden": "se",
    "Bósnia e Herzegovina": "ba", "Bosnia": "ba",

    # Africa
    "Marrocos": "ma", "Morocco": "ma",
    "Senegal": "sn",
    "Nigéria": "ng", "Nigeria": "ng",
    "Egito": "eg", "Egypt": "eg",
    "Camarões": "cm", "Cameroon": "cm",
    "Gana": "gh", "Ghana": "gh",
    "Costa do Marfim": "ci", "Ivory Coast": "ci",
    "Mali": "ml",
    "Tunísia": "tn", "Tunisia": "tn",
    "Argélia": "dz", "Algeria": "dz",
    "África do Sul": "za", "South Africa": "za",
    "RD Congo": "cd", "Congo DR": "cd",
    "Tanzânia": "tz", "Tanzania": "tz",
    "Zâmbia": "zm", "Zambia": "zm",
    "Zimbábue": "zw", "Zimbabwe": "zw",
    "Comoros": "km",
    "Uganda": "ug",
    "Cabo Verde": "cv", "Cape Verde": "cv",

    # Asia / Oceania
    "Japão": "jp", "Japan": "jp",
    "Coreia do Sul": "kr", "South Korea": "kr",
    "Arábia Saudita": "sa", "Saudi Arabia": "sa",
    "Irã": "ir", "Iran": "ir",
    "Austrália": "au", "Australia": "au",
    "Catar": "qa", "Qatar": "qa",
    "Uzbequistão": "uz", "Uzbekistan": "uz",
    "Jordânia": "jo", "Jordan": "jo",
    "Iraque": "iq", "Iraq": "iq",
    "China": "cn",
    "Indonésia": "id", "Indonesia": "id",
    "Nova Zelândia": "nz", "New Zealand": "nz",
    "Israel": "il",
}


def flag_url(team_name: str, size: int = 40) -> str:
    code = TEAM_FLAGS.get(team_name, "").lower()
    if not code:
        return ""
    return f"https://flagcdn.com/w{size}/{code}.png"


def flag_img_html(team_name: str, size: int = 32) -> str:
    url = flag_url(team_name, size)
    if not url:
        return ""
    return f'<img src="{url}" width="{size}" style="vertical-align:middle;border-radius:3px;margin-right:6px">'
