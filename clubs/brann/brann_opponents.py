# ("keyword"): ("image_name", "title"),
IMAGE_MAP_ELITESERIEN = {
    ("aalesund", "ålesund"): ("alesund.png", "Brann - Aalesund"),
    ("bodø",): ("bodoglimt.png", "Brann - Bodø/Glimt"),
    ("fredrikstad",): ("fredrikstad.png", "Brann - Fredrikstad"),
    ("hamkam", "hamar"): ("hamkam.png", "Brann - HamKam"),
    ("haugesund",): ("haugesund.png", "Brann - Haugesund"),
    ("kfum",): ("kfum.png", "Brann - KFUM Oslo"),
    ("kristiansund",): ("kristiansund.png", "Brann - Kristiansund"),
    ("lillestrøm",): ("lillestrom.png", "Brann - Lillestrøm"),
    ("molde",): ("molde.png", "Brann - Molde"),
    ("odd",): ("odd.png", "Brann - Odd"),
    ("rosenborg",): ("rosenborg.png", "Brann - Rosenborg"),
    ("sandefjord",): ("sandefjord.png", "Brann - Sandefjord"),
    ("sarpsborg",): ("sarpsborg.png", "Brann - Sarpsborg"),
    ("stabæk",): ("stabek.png", "Brann - Stabæk"),
    ("strømsgodset",): ("stromsgodset.png", "Brann - Strømsgodset"),
    ("tromsø",): ("tromso.png", "Brann - Tromsø"),
    ("vålerenga",): ("valrenga.png", "Brann - Vålerenga"),
    ("viking",): ("viking.png", "Brann - Viking"),
    ("partoutkort eliteserien",): ("eliteserien_logo.png", "\nPartoutkort Eliteserien 2024"),
}

IMAGE_MAP_TOPPSERIEN = {
    ("arna", "bjørnar", "bjornar"): ("arnabjornar.png", "Brann - Arna-Bjørnar"),
    ("kolbotn",): ("kolbotn.png", "Brann - Kolbotn"),
    ("kristiansund",): ("kristiansund.png", "Brann - Kristiansund"),
    ("lillestrøm", "lsk"): ("lskkvinner.png", "Brann - LSK Kvinner"),
    ("lyn",): ("lyn.png", "Brann - Lyn"),
    ("rosenborg",): ("rbkkvinner.png", "Brann - Rosenborg"),
    ("roa", "røa"): ("roa.png", "Brann - Røa"),
    ("stabæk",): ("stabek.png", "Brann - Stabæk"),
    ("vålerenga",): ("valrenga.png", "Brann - Vålerenga"),
    ("åsane", "aasane", "asane"): ("aasane.png", "Brann - Åsane"),
    ("partoutkort toppserien",): ("toppserien_logo.png", "\nPartoutkort Toppserien 2024"),
}

IMAGE_MAP = {
    ("alkmaar",): ("alkmaar.png", "Brann - AZ Alkmaar"),
    ("glasgow",): ("default.png", "UEFA CL Runde 2: Brann - Glasgow City"),
    ("praha",): ("default.png", "UEFA CL Group B: Brann - Slavia Praha"),
    ("lyon",): ("lyon.png", "UEFA CL Group B: Brann - Lyon"),
    ("pölten",): ("polten.png", "UEFA CL Group B: Brann - St. Pölten"),
    ("barcelona",): ("barcelona_femini.png", "UEFA CL Kvartfinale: Brann - Barcelona"),
    ("go ahead eagles", "gae",): ("gae.png", "Brann - Go Ahead Eagles"),
    ("mirren",): ("stmirren.png", "Brann - St. Mirren")
}


def get_league_and_background(title):
    if "eliteserien" in title:
        return "brann_herrer_bg.png", "Eliteserien", IMAGE_MAP_ELITESERIEN
    elif "toppserien" in title:
        return "brann_kvinner_bg.png", "Toppserien", IMAGE_MAP_TOPPSERIEN
    elif "cup" in title or "nm" in title:
        # Må finne en måte å skille mellom cup for herrer og kvinner
        return "brann_cup_bg.png", "NM", IMAGE_MAP_ELITESERIEN
    elif "champion" in title:
        return "brann_champ_bg.png", "Champions League", IMAGE_MAP
    elif "europa" in title:
        return "brann_europa_bg.png", "Europa League", IMAGE_MAP
    elif "conference" in title:
        return "brann_conf_bg.png", "Conference League", IMAGE_MAP
    else:
        return "brann_bg.png", "Error", None
