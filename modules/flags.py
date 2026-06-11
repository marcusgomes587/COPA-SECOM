# Mapeamento de nome do time -> codigo ISO 3166-1 alpha-2
# Usado para buscar bandeiras em flagcdn.com

TEAM_FLAGS: dict[str, str] = {
    # Americas
    "Brazil": "br", "Brasil": "br",
    "Argentina": "ar",
    "Uruguay": "uy", "Uruguai": "uy",
    "Colombia": "co", "Colombia": "co",
    "Ecuador": "ec", "Equador": "ec",
    "Peru": "pe",
    "Chile": "cl",
    "Paraguay": "py", "Paraguai": "py",
    "Bolivia": "bo", "Bolivia": "bo",
    "Venezuela": "ve",
    "United States": "us", "USA": "us", "EUA": "us",
    "Mexico": "mx", "Mexico": "mx",
    "Canada": "ca",
    "Honduras": "hn",
    "Costa Rica": "cr",
    "Panama": "pa", "Panama": "pa",
    "Jamaica": "jm",
    "Trinidad and Tobago": "tt",
    "El Salvador": "sv",

    # Europa
    "France": "fr", "Franca": "fr",
    "England": "gb-eng", "Inglaterra": "gb-eng",
    "Germany": "de", "Alemanha": "de",
    "Spain": "es", "Espanha": "es",
    "Portugal": "pt",
    "Netherlands": "nl", "Holanda": "nl", "Holland": "nl",
    "Belgium": "be", "Belgica": "be",
    "Italy": "it", "Italia": "it",
    "Croatia": "hr", "Croacia": "hr",
    "Poland": "pl", "Polonia": "pl",
    "Switzerland": "ch", "Suica": "ch",
    "Denmark": "dk", "Dinamarca": "dk",
    "Norway": "no", "Noruega": "no",
    "Austria": "at",
    "Turkey": "tr", "Turquia": "tr",
    "Ukraine": "ua", "Ucrania": "ua",
    "Serbia": "rs",
    "Slovakia": "sk", "Eslovaquia": "sk",
    "Slovenia": "si", "Eslovenia": "si",
    "Albania": "al",
    "Georgia": "ge",
    "Scotland": "gb-sct", "Escocia": "gb-sct",
    "Wales": "gb-wls", "Gales": "gb-wls",
    "Hungary": "hu", "Hungria": "hu",
    "Czech Republic": "cz", "Republica Tcheca": "cz",
    "Romania": "ro", "Romania": "ro",
    "Greece": "gr", "Grecia": "gr",

    # Africa
    "Morocco": "ma", "Marrocos": "ma",
    "Senegal": "sn",
    "Nigeria": "ng",
    "Egypt": "eg", "Egito": "eg",
    "Cameroon": "cm", "Camaroes": "cm",
    "Ghana": "gh",
    "Ivory Coast": "ci", "Costa do Marfim": "ci",
    "Mali": "ml",
    "Tunisia": "tn", "Tunisia": "tn",
    "Algeria": "dz", "Algeria": "dz",
    "South Africa": "za", "Africa do Sul": "za",
    "Congo DR": "cd", "Congo": "cd",
    "Tanzania": "tz",
    "Zambia": "zm",
    "Zimbabwe": "zw",
    "Comoros": "km",
    "Uganda": "ug",
    "Cape Verde": "cv", "Cabo Verde": "cv",

    # Asia
    "Japan": "jp", "Japao": "jp",
    "South Korea": "kr", "Coreia do Sul": "kr",
    "Saudi Arabia": "sa", "Arabia Saudita": "sa",
    "Iran": "ir", "Ira": "ir",
    "Australia": "au",
    "Qatar": "qa", "Catar": "qa",
    "Uzbekistan": "uz", "Uzbequistao": "uz",
    "Jordan": "jo", "Jordania": "jo",
    "Iraq": "iq",
    "China": "cn",
    "Indonesia": "id",
    "New Zealand": "nz", "Nova Zelandia": "nz",

    # Oriente Medio
    "Israel": "il",
    "UAE": "ae", "Emirados Arabes": "ae",
}


def flag_url(team_name: str, size: int = 40) -> str:
    """Retorna URL da bandeira para o time. Tamanho em px (20, 40, 80, 160)."""
    code = TEAM_FLAGS.get(team_name, "").lower()
    if not code:
        return ""
    return f"https://flagcdn.com/w{size}/{code}.png"


def flag_img_html(team_name: str, size: int = 32) -> str:
    """Retorna tag <img> HTML com a bandeira do time."""
    url = flag_url(team_name, size)
    if not url:
        return ""
    return f'<img src="{url}" width="{size}" style="vertical-align:middle;border-radius:3px;margin-right:6px">'
