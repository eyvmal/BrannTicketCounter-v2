# ("keyword"): ("image_name", "title"),
IMAGE_MAP_ELITESERIEN = {
    ("aalesund", "ålesund"): ("alesund.png", "Aalesund"),
    ("bodø",): ("bodoglimt.png", "Bodø/Glimt"),
    ("fredrikstad",): ("fredrikstad.png", "Fredrikstad"),
    ("hamkam", "hamar"): ("hamkam.png", "HamKam"),
    ("haugesund",): ("haugesund.png", "Haugesund"),
    ("kfum",): ("kfum.png", "KFUM Oslo"),
    ("kristiansund",): ("kristiansund.png", "Kristiansund"),
    ("lillestrøm",): ("lillestrom.png", "Lillestrøm"),
    ("molde",): ("molde.png", "Molde"),
    ("odd",): ("odd.png", "Odd"),
    ("rosenborg",): ("rosenborg.png", "Rosenborg"),
    ("sandefjord",): ("sandefjord.png", "Sandefjord"),
    ("sarpsborg",): ("sarpsborg.png", "Sarpsborg"),
    ("stabæk",): ("stabek.png", "Stabæk"),
    ("strømsgodset",): ("stromsgodset.png", "Strømsgodset"),
    ("tromsø",): ("tromso.png", "Tromsø"),
    ("vålerenga",): ("valrenga.png", "Vålerenga"),
    ("viking",): ("viking.png", "Viking"),
    ("partoutkort eliteserien",): ("eliteserien_logo.png", "\nPartoutkort Eliteserien 2024"),
}

IMAGE_MAP_TOPPSERIEN = {
    ("arna", "bjørnar", "bjornar"): ("arnabjornar.png", "Arna-Bjørnar"),
    ("kolbotn",): ("kolbotn.png", "Kolbotn"),
    ("kristiansund",): ("kristiansund.png", "Kristiansund"),
    ("lillestrøm", "lsk"): ("lskkvinner.png", "LSK Kvinner"),
    ("lyn",): ("lyn.png", "Lyn"),
    ("rosenborg",): ("rbkkvinner.png", "Rosenborg"),
    ("roa", "røa"): ("roa.png", "Røa"),
    ("stabæk",): ("stabek.png", "Stabæk"),
    ("vålerenga",): ("valrenga.png", "Vålerenga"),
    ("åsane", "aasane", "asane"): ("aasane.png", "Åsane"),
    ("partoutkort toppserien",): ("toppserien_logo.png", "\nPartoutkort Toppserien 2024"),
}

IMAGE_MAP = {
    ("alkmaar",): ("alkmaar.png", "AZ Alkmaar"),
    ("glasgow",): ("default.png", "Glasgow City"),
    ("praha",): ("default.png", "Slavia Praha"),
    ("lyon",): ("lyon.png", "Lyon"),
    ("pölten",): ("polten.png", "St. Pölten"),
    ("barcelona",): ("barcelona_femini.png", "Barcelona"),
    ("go ahead eagles", "gae",): ("gae.png", "Go Ahead Eagles"),
    ("mirren",): ("stmirren.png", "St. Mirren")
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
