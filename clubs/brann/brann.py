from image_creator import ImageCreator
from scrape_tools import *
from clubs.brann.brann_opponents import *
from datetime import datetime
from twitter import create_tweet

HOMEPAGE_URL = "https://brann.ticketco.events/no/nb"
FILENAME = "brann"
STADIUM = "Brann Stadion"
IGNORE_LIST = {
    "partoutkort",
    "sesongkort",
    "gavekort",
    "em"
}
CUSTOM_GAMES = [{'title': 'Brann - Go Ahead Eagles, Conference League',
                 'time': '01.08.2024 19:00\n@\nBrann Stadion',
                 'link': 'https://brann.ticketco.events/no/nb/events/639986/seating_arrangement/'}]


def add_custom_games(custom_games, event_list):
    print('Adding custom events')
    for game in custom_games:
        if {game['link'] not in event_list}:
            print('Adding ' + game['link'])
            event_list.append(game)
    return event_list


def custom_event_filter(e_list):
    filtered_list = []
    sorted_events = sorted(e_list, key=lambda x: datetime.strptime(x['time'].split(' ', 1)[0], "%d.%m.%Y"))

    for e in sorted_events:
        updated_time = e['time'].replace("\n@\n", " @ ")
        europe = get_europe_from_event_title(e['title'])
        venue = updated_time.split(' @ ', 1)[1]
        date = datetime.strptime(updated_time.split(' ', 1)[0], "%d.%m.%Y").date().strftime("%d.%m.%y")
        time = updated_time.split(' ', 2)[1]

        updated_event = {
            'title': e['title'],
            'time': time,
            'date': date,
            'venue': venue,
            'link': e['link'],
            'europe': europe
        }
        filtered_list.append(updated_event)
    return filtered_list


def update_totals(category, section, category_totals):
    category_totals[category]["section_amount"] += section["section_amount"]
    category_totals[category]["sold_seats"] += section["sold_seats"]
    category_totals[category]["available_seats"] += section["available_seats"]
    category_totals[category]["locked_seats"] += section["locked_seats"]


def brann_stadion(data, event_title: str, event_date: str, europa: bool) -> Dict:
    time_now = get_time_formatted("human")
    category_totals = {
        "GENERAL": {"title": event_title, "date": event_date, "time": time_now},
        "FRYDENBØ": {"section_amount": 0, "sold_seats": 0, "available_seats": 0, "locked_seats": 0},
        "SPV": {"section_amount": 0, "sold_seats": 0, "available_seats": 0, "locked_seats": 0},
        "BT": {"section_amount": 0, "sold_seats": 0, "available_seats": 0, "locked_seats": 0},
        "FJORDKRAFT": {"section_amount": 0, "sold_seats": 0, "available_seats": 0, "locked_seats": 0},
        "VIP": {"section_amount": 0, "sold_seats": 0, "available_seats": 0, "locked_seats": 0},
        "TOTALT": {"section_amount": 0, "sold_seats": 0, "available_seats": 0, "locked_seats": 0}
    }

    section_category_mapping = {
        "spv": "SPV",
        "bob": "BT",
        "bt": "BT",
        "frydenbø": "FRYDENBØ",
        "fjordkraft": "FJORDKRAFT",
        "vip": "VIP"
    }

    for section in data:
        section_name = section["section_name"].lower()
        visibility = section["visible"]
        sold_seats = section["sold_seats"]

        # Skip section if no seats are sold and visibility is False
        if sold_seats == 0 and not visibility:
            continue

        # General exclusions applicable to all categories, spesific for 'Brann Stadion'
        if any(exclusion in section_name for exclusion in ["press", "gangen", "stå",
                                                           "fjordkraft felt a", "fjordkraft felt b"]):
            continue

        for key, category in section_category_mapping.items():
            if key in section_name:
                update_totals(category, section, category_totals)
                update_totals("TOTALT", section, category_totals)
                break  # Break if we've found a matching category to avoid double counting

    if not europa and category_totals["FRYDENBØ"]["section_amount"] > 0:
        percentage = round((category_totals["FRYDENBØ"]["sold_seats"] / category_totals["FRYDENBØ"]["section_amount"]), 2)
        sold_seats = round(1000 * percentage)
        category_totals["FRYDENBØ"]["sold_seats"] += sold_seats
        category_totals["FRYDENBØ"]["section_amount"] += 1000
        category_totals["FRYDENBØ"]["available_seats"] += 1000 - sold_seats
        update_totals("TOTALT", {"section_amount": 1000, "sold_seats": sold_seats,
                                 "available_seats": 1000 - sold_seats, "locked_seats": 0}, category_totals)
    return category_totals


def run_brann(option: str, use_local_data: bool, debug: bool):
    print(f"Starting fetching data for {FILENAME}... ")
    temp_event_list = get_upcoming_events(option, HOMEPAGE_URL, IGNORE_LIST)
    event_list = add_custom_games(CUSTOM_GAMES, temp_event_list)

    filtered_event_list = custom_event_filter(event_list)
    pic_number = 0
    image_path_list = []

    for event in filtered_event_list:
        event_title = event["title"]
        if event['venue'] == STADIUM:
            if use_local_data:
                path, path_simple = get_directory_path(event["title"])  # Function to get path of local data
                print(f"\nFetched local data from {path_simple}")
            else:
                results = get_ticket_info(event["link"], event_title)
                if debug:
                    save_new_json("debug", results)
                    continue
                else:
                    date_time_venue = f'{event["date"]} {event["time"]} @ {event["venue"]}'
                    grouped_results = brann_stadion(results, event["title"], date_time_venue, event["europe"])
                    path = save_new_json(event["title"], grouped_results)

            # Prepare text for image creation
            background_path, league, image_map = get_league_and_background(event_title.lower())
            image_creator = ImageCreator(f"images/{background_path}", f"images/{FILENAME}.png")
            image_text = create_string(path)
            final_image = image_creator.create_image(image_text, image_map, league)
            if final_image:
                image_path = f"clubs/{FILENAME}/picture{pic_number}.png"
                image_path_list.append(image_creator.save_image(final_image, image_path))
                pic_number = pic_number + 1
        else:
            print(f"Error: Unknown stadium for {event_title}")

    if image_path_list.__len__() > 0:
        tweet_header = ("Info om billettsalget for Brann sine kommende hjemmekamper!"
                        "\nTallene er ikke offisielle og kan variere fra reelle tall.")
        # create_tweet(tweet_header, image_path_list)
    else:
        print("Image list is empty")
