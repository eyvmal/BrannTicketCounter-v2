# ("keyword"): ("image_name", "title"),
IMAGE_MAP_ELITESERIEN = {
    ("aalesund", "ålesund"): ("alesund.png", "Aalesund"),
    ("bodø",): ("bodoglimt.png", "Bodø/Glimt"),
    ("brann",): ("brann.png", "Brann"),
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
}


def get_league_and_background(title):
    if "eliteserien"in title:
        return "brann_herrer_bg.png", "Eliteserien", IMAGE_MAP_ELITESERIEN
    elif "toppserien"in title:
        return "brann_kvinner_bg.png", "Toppserien", IMAGE_MAP_TOPPSERIEN
    elif "cup"in title or "nm"in title:
        # Må finne en måte å skille mellom cup for herrer og kvinner
        return "brann_cup_bg.png", "NM", IMAGE_MAP_ELITESERIEN
    else:
        return
