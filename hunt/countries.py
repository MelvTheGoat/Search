"""Find countries in free-text locations like "London, UK" or "Remote - EMEA"."""
import re

# country: (ISO code, other names, big cities)
COUNTRIES = {
    "Nigeria": ("NG", ["naija"], ["lagos", "abuja", "ibadan", "port harcourt", "ikeja", "lekki", "yaba", "victoria island", "kano", "enugu", "benin city"]),
    "Kenya": ("KE", [], ["nairobi", "mombasa"]),
    "Ghana": ("GH", [], ["accra", "kumasi"]),
    "South Africa": ("ZA", ["rsa"], ["cape town", "johannesburg", "pretoria", "durban", "stellenbosch", "sandton"]),
    "Egypt": ("EG", [], ["cairo", "alexandria"]),
    "Morocco": ("MA", [], ["casablanca", "rabat"]),
    "Rwanda": ("RW", [], ["kigali"]),
    "Uganda": ("UG", [], ["kampala"]),
    "Tanzania": ("TZ", [], ["dar es salaam"]),
    "Senegal": ("SN", [], ["dakar"]),
    "Cote d'Ivoire": ("CI", ["ivory coast", "cote divoire"], ["abidjan"]),
    "Ethiopia": ("ET", [], ["addis ababa"]),
    "Tunisia": ("TN", [], ["tunis"]),
    "United Kingdom": ("GB", ["uk", "u k", "england", "scotland", "wales", "great britain", "britain", "northern ireland"],
                       ["london", "manchester", "edinburgh", "cambridge", "oxford", "bristol", "leeds", "glasgow", "birmingham", "belfast", "cardiff", "reading"]),
    "Ireland": ("IE", [], ["dublin", "cork", "galway"]),
    "Netherlands": ("NL", ["the netherlands", "holland"], ["amsterdam", "rotterdam", "utrecht", "the hague", "eindhoven", "delft"]),
    "Germany": ("DE", ["deutschland"], ["berlin", "munich", "munchen", "hamburg", "frankfurt", "cologne", "koln", "stuttgart", "dusseldorf", "leipzig", "tubingen"]),
    "France": ("FR", [], ["paris", "lyon", "toulouse", "marseille", "nantes", "grenoble"]),
    "Spain": ("ES", ["espana"], ["madrid", "barcelona", "valencia", "malaga", "seville"]),
    "Portugal": ("PT", [], ["lisbon", "lisboa", "porto", "braga", "coimbra"]),
    "Italy": ("IT", [], ["milan", "milano", "rome", "roma", "turin", "torino"]),
    "Switzerland": ("CH", [], ["zurich", "geneva", "lausanne", "basel", "zug"]),
    "Austria": ("AT", [], ["vienna", "wien", "graz"]),
    "Belgium": ("BE", [], ["brussels", "antwerp", "ghent", "leuven"]),
    "Luxembourg": ("LU", [], []),
    "Denmark": ("DK", [], ["copenhagen", "aarhus"]),
    "Sweden": ("SE", [], ["stockholm", "gothenburg", "malmo"]),
    "Norway": ("NO", [], ["oslo", "bergen", "trondheim"]),
    "Finland": ("FI", [], ["helsinki", "espoo", "tampere"]),
    "Estonia": ("EE", [], ["tallinn", "tartu"]),
    "Latvia": ("LV", [], ["riga"]),
    "Lithuania": ("LT", [], ["vilnius", "kaunas"]),
    "Poland": ("PL", [], ["warsaw", "krakow", "wroclaw", "gdansk", "poznan"]),
    "Czechia": ("CZ", ["czech republic"], ["prague", "brno"]),
    "Hungary": ("HU", [], ["budapest"]),
    "Romania": ("RO", [], ["bucharest", "cluj"]),
    "Bulgaria": ("BG", [], ["sofia"]),
    "Greece": ("GR", [], ["athens", "thessaloniki"]),
    "Cyprus": ("CY", [], ["limassol", "nicosia"]),
    "Malta": ("MT", [], ["valletta"]),
    "Serbia": ("RS", [], ["belgrade", "novi sad"]),
    "Croatia": ("HR", [], ["zagreb"]),
    "Ukraine": ("UA", [], ["kyiv", "kiev", "lviv"]),
    "Turkey": ("TR", ["turkiye"], ["istanbul", "ankara"]),
    "Israel": ("IL", [], ["tel aviv", "jerusalem", "haifa", "herzliya"]),
    "United Arab Emirates": ("AE", ["uae", "u a e", "emirates"], ["dubai", "abu dhabi"]),
    "Saudi Arabia": ("SA", ["ksa"], ["riyadh", "jeddah", "dammam"]),
    "Qatar": ("QA", [], ["doha"]),
    "Bahrain": ("BH", [], ["manama"]),
    "Oman": ("OM", [], ["muscat"]),
    "Jordan": ("JO", [], ["amman"]),
    "United States": ("US", ["usa", "u s", "u s a", "united states of america", "america"],
                      ["new york", "nyc", "san francisco", "sf bay area", "bay area", "seattle", "boston", "austin", "chicago",
                       "los angeles", "mountain view", "palo alto", "menlo park", "sunnyvale", "san jose", "redwood city",
                       "washington dc", "denver", "atlanta", "miami", "dallas", "houston", "pittsburgh", "philadelphia",
                       "san diego", "salt lake city", "raleigh", "portland", "minneapolis", "detroit", "nashville", "cupertino",
                       "santa clara", "bellevue", "kirkland", "cambridge ma", "brooklyn", "south san francisco", "boulder"]),
    "Canada": ("CA", [], ["toronto", "montreal", "vancouver", "ottawa", "waterloo", "calgary", "edmonton", "kitchener", "quebec"]),
    "Mexico": ("MX", [], ["mexico city", "guadalajara", "monterrey"]),
    "Brazil": ("BR", ["brasil"], ["sao paulo", "rio de janeiro", "belo horizonte", "curitiba"]),
    "Argentina": ("AR", [], ["buenos aires"]),
    "Colombia": ("CO", [], ["bogota", "medellin"]),
    "Chile": ("CL", [], ["santiago"]),
    "Peru": ("PE", [], ["lima"]),
    "India": ("IN", [], ["bangalore", "bengaluru", "hyderabad", "mumbai", "pune", "delhi", "new delhi", "gurgaon", "gurugram", "noida", "chennai", "kolkata"]),
    "Pakistan": ("PK", [], ["karachi", "lahore", "islamabad"]),
    "Bangladesh": ("BD", [], ["dhaka"]),
    "Sri Lanka": ("LK", [], ["colombo"]),
    "Singapore": ("SG", [], []),
    "Malaysia": ("MY", [], ["kuala lumpur"]),
    "Indonesia": ("ID", [], ["jakarta", "bali"]),
    "Philippines": ("PH", [], ["manila", "cebu"]),
    "Vietnam": ("VN", ["viet nam"], ["ho chi minh", "hanoi"]),
    "Thailand": ("TH", [], ["bangkok"]),
    "Hong Kong": ("HK", [], []),
    "Taiwan": ("TW", [], ["taipei"]),
    "China": ("CN", ["prc"], ["beijing", "shanghai", "shenzhen", "hangzhou", "guangzhou"]),
    "Japan": ("JP", [], ["tokyo", "osaka", "kyoto"]),
    "South Korea": ("KR", ["korea", "republic of korea"], ["seoul"]),
    "Australia": ("AU", [], ["sydney", "melbourne", "brisbane", "perth", "adelaide", "canberra"]),
    "New Zealand": ("NZ", [], ["auckland", "wellington", "christchurch"]),
}

# Every other country, by name only (no cities), so no place is mistaken
# for "no limit".
EXTRA_COUNTRIES = """Afghanistan|Albania|Algeria|Andorra|Angola|Antigua and Barbuda|Armenia|Azerbaijan|Bahamas|Barbados|Belarus|Belize|Benin|Bhutan|Bolivia|Bosnia and Herzegovina|Botswana|Brunei|Burkina Faso|Burundi|Cabo Verde|Cape Verde|Cambodia|Cameroon|Central African Republic|Chad|Comoros|Congo|Costa Rica|Cuba|Djibouti|Dominica|Dominican Republic|Ecuador|El Salvador|Equatorial Guinea|Eritrea|Eswatini|Fiji|Gabon|Gambia|Georgia|Grenada|Guatemala|Guinea|Guinea-Bissau|Guyana|Haiti|Honduras|Iceland|Iran|Iraq|Jamaica|Kazakhstan|Kiribati|Kosovo|Kuwait|Kyrgyzstan|Laos|Lebanon|Lesotho|Liberia|Libya|Liechtenstein|Madagascar|Malawi|Maldives|Mali|Marshall Islands|Mauritania|Mauritius|Micronesia|Moldova|Monaco|Mongolia|Montenegro|Mozambique|Myanmar|Namibia|Nauru|Nepal|Nicaragua|Niger|North Macedonia|Palau|Palestine|Panama|Papua New Guinea|Paraguay|Puerto Rico|Saint Lucia|Samoa|San Marino|Sao Tome and Principe|Seychelles|Sierra Leone|Slovakia|Slovenia|Solomon Islands|Somalia|South Sudan|Sudan|Suriname|Syria|Tajikistan|Timor-Leste|Togo|Tonga|Trinidad and Tobago|Turkmenistan|Tuvalu|Uruguay|Uzbekistan|Vanuatu|Venezuela|Yemen|Zambia|Zimbabwe""".split("|")
for _name in EXTRA_COUNTRIES:
    COUNTRIES.setdefault(_name, ("", [], []))

US_STATES = ("AL AK AZ AR CA CO CT DE FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC "
             "ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY DC").split()
US_STATE_NAMES = ["california", "new york state", "texas", "washington state", "massachusetts", "colorado", "illinois",
                  "georgia", "florida", "virginia", "north carolina", "pennsylvania", "oregon", "utah", "arizona", "new jersey"]
CA_PROVINCES = "ON BC QC AB MB NS".split()

# Words that mean a remote job is open to someone in Nigeria.
OPEN_REGIONS = ["worldwide", "anywhere", "global", "globally", "all countries", "international", "emea", "africa",
                "west africa", "sub saharan", "middle east and africa", "europe middle east", "any location",
                "any country", "work from anywhere"]
# Multi-country regions that do not include Nigeria.
OTHER_REGIONS = ["europe", "eu", "european union", "eea", "americas", "north america", "latin america", "latam",
                 "south america", "apac", "asia pacific", "asia", "anz", "nordics", "dach", "benelux", "cee", "mena",
                 "gcc", "middle east", "uk and ireland", "uk i", "oceania", "southeast asia", "sea"]

# City names that also exist in the US or Canada, like Cambridge, MA or London, ON.
AMBIGUOUS_CITIES = {"cambridge", "london", "birmingham", "reading", "waterloo", "valencia", "athens", "perth"}

ISO_TO_COUNTRY = {v[0]: k for k, v in COUNTRIES.items() if v[0]}
ISO_TO_COUNTRY["UK"] = "United Kingdom"
# Two-letter codes that are usually something else in a location line:
# time zones (PT, ET, MT), "IT", "IN", "ID", "IS", "AT", "CO", "SE" and so on.
ISO_SKIP = {"PT", "ET", "MT", "IT", "IN", "ID", "IS", "AT", "CO", "SE", "NO", "DE", "ES", "HR", "PE", "MA", "SA",
            "CI", "OM", "BD", "PH", "TH", "LT", "CL", "AR", "BE"}


def _build_patterns():
    pats = []
    for country, (iso, aliases, cities) in COUNTRIES.items():
        for w in [country.lower().replace("'", ""), *aliases]:
            pats.append((re.compile(r"(?<![a-z])" + re.escape(w) + r"(?![a-z])"), country, False, "country"))
        for w in cities:
            pats.append((re.compile(r"(?<![a-z])" + re.escape(w) + r"(?![a-z])"), country, w in AMBIGUOUS_CITIES, "city"))
    return pats


_PATTERNS = _build_patterns()
_STATE_RE = re.compile(r"(?:,|\s-|\()\s*(" + "|".join(US_STATES) + r")\b(?!\.)")
_PROV_RE = re.compile(r"(?:,|\()\s*(" + "|".join(CA_PROVINCES) + r")\b")
_ISO_RE = re.compile(r"(?:^|[,(\s-])(" + "|".join(sorted(set(ISO_TO_COUNTRY) - ISO_SKIP)) + r")(?:$|[,)\s-])(?!\s*(?:hours|time|/))")
# Parts of a location line about working hours, not places.
_HOURS_RE = re.compile(r"\(\s*[^)]*\b(overlap|hours)\b[^)]*\)|\b(overlap with|hours in|working hours|time ?zones?)\b.*", re.I)


def _clean(s):
    from .text import norm
    return " " + norm(s.replace("'", "")) + " "


def find_places(location):
    """Return [(country, kind)] in the order found. kind is "country" when
    the country itself is named, or "city" when only a city or state is."""
    if not location:
        return []
    location = _HOURS_RE.sub(" ", location)
    text = _clean(location)
    hits = []
    state_hit = bool(_STATE_RE.search(location) or _PROV_RE.search(location))
    for pat, country, ambiguous, kind in _PATTERNS:
        if ambiguous and state_hit:
            continue
        m = pat.search(text)
        if m:
            hits.append((m.start(), country, kind))
    other = any(c != "United States" for _, c, _ in hits)
    for m in _STATE_RE.finditer(location):
        # "Berlin, DE" is Germany, not Delaware.
        if other and m.group(1) in {"DE", "IN", "ID", "CO", "AR", "PA", "MA", "GA", "SC", "AL", "IL", "NE", "ME", "MT", "SD"}:
            continue
        hits.append((m.start() + 1000, "United States", "city"))
    for name in US_STATE_NAMES:
        i = text.find(" " + name + " ")
        if i >= 0:
            hits.append((i, "United States", "city"))
    for m in _PROV_RE.finditer(location):
        hits.append((m.start() + 1000, "Canada", "city"))
    for m in _ISO_RE.finditer(location):
        code = m.group(1)
        if state_hit and (code in US_STATES or code in CA_PROVINCES):
            continue
        hits.append((m.start() + 2000, ISO_TO_COUNTRY[code], "country"))
    out = []
    for _, country, kind in sorted(hits):
        if (country, kind) not in out:
            out.append((country, kind))
    return out


def find_countries(location):
    """Return countries named in a location string, in the order found."""
    found = []
    for country, _ in find_places(location):
        if country not in found:
            found.append(country)
    return found


def has_city(location):
    return any(kind == "city" for _, kind in find_places(location))


def has_region(location, regions):
    text = _clean(location)
    # "South Africa" is a country, not the Africa region; "anywhere in
    # France" is France only.
    text = text.replace(" south africa ", " ")
    text = re.sub(r" anywhere in [a-z ]+", " ", text)
    text = re.sub(r" [a-z]+ anywhere ", " ", text) if re.search(r" anywhere ", text) and find_countries(location) else text
    return any(f" {r} " in text for r in regions)
