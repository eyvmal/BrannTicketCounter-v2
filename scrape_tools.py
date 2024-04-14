from datetime import datetime
import re
import pytz
import requests
import json
import os
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
from bs4 import BeautifulSoup
from typing import List, Dict, Tuple, Optional, Any

SAVE_PATH = os.path.dirname(os.path.abspath(__file__)) + "/"

session = requests.Session()


def fetch_url(url: str) -> Optional[requests.Response]:
    """Fetch the HTML code for a webpage.
    Args:
        url (str):
            The URL of the webpage to scrape.
    Returns:
        Optional[requests.Response]:
            The HTML code of the webpage, or None if an error occurs.
    """
    try:
        response = session.get(url)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print("An error occurred:", e)
        return None


def get_upcoming_events(next_or_all: str, homepage_url: str, ignore_list) -> List[Dict]:
    """Fetch URLs of all upcoming events from the Brann main event page.
    Args:
        next_or_all (str):
            Determines whether to return all upcoming events or just the next one.
            Accepts values: 'next', 'all'.
        homepage_url (str):
            Link to the clubs main page of upcoming events
    Returns:
        List[Dict]:
            A list of dictionaries containing details of the next or all upcoming events.
    """
    print("Connecting to " + homepage_url)
    page_html = fetch_url(homepage_url).text
    if page_html is None:
        print("An error occurred: Couldn't fetch HTML")
        return []
    soup = BeautifulSoup(page_html, "html.parser")

    print("Getting events... ")
    event_list = []
    try:
        event_containers = soup.find_all("div", class_="tc-events-list--details")
    except AttributeError:
        print("Error: The HTML does not contain any divs with class 'tc-events-list--details'.")
        return []

    # Fetch all events from their event page
    for index, event in enumerate(event_containers, start=1):  # Start counting from 1 for human-readable indexing
        a_element = event.find("a", class_="tc-events-list--title")
        if not a_element:
            # If this error is thrown, the webpage layout may have changed.
            print(f"Couldn't find the title for the event at index {index}.")
            continue
        event_title = a_element.get_text(strip=True)

        if ignore_list and any(word in event_title.lower() for word in ignore_list):
            print(f"Ignoring event '{event_title}' due to ignore list.")
            continue

        # Attempt to find event_date_time. Not crucial to find
        place_time = event.find("div", class_="tc-events-list--place-time")
        event_date_time = place_time.get_text(strip=True) if place_time else None

        # Attempt to find the purchase url for the event. Crucial
        event_link = get_nested_link(a_element.get("href"), event_title)
        if event_link is None:
            continue

        event_list.append({
            "title": event_title,
            "time": event_date_time,
            "link": event_link
        })

        if next_or_all.lower() == "next":
            break

    events = event_list.__len__()
    print(f"Done! Added a total of {events} events.")
    return event_list


def get_nested_link(url: str, event_title: str) -> Optional[str]:
    """Find and return the ticket page URL from an event page.
    Args:
        url (str):
            The URL of the event page.
        event_title (str):
            The name of the event, used in error for debugging
    Returns:
        str:
            The URL of the ticket page.
    """
    try:
        page_html = fetch_url(url).text
        if page_html is None:
            print(f"An error occurred: Couldn't fetch HTML for {url}")
            return None
        soup = BeautifulSoup(page_html, "html.parser")
        event_url = soup.find("a", id="placeOrderLink")
        return event_url.get("href")
    except:
        # If this error is thrown its possibly missing nested event link or changed structure.
        print(f"Error fetching nested url for '{event_title}'. Skipping event.")
        return None


def get_ticket_info(event_url: str, event_title: str) -> list[Any]:
    """Gather and save ticket information for a given event.
    Args:
        event_url (str):
            The URL to find ticket information for the event.
        event_title (str):
            The title of the event.
    Returns:
        str:
            The directory path where the results are saved.
    """
    json_url = event_url + "item_types.json"
    print("\nUpdating ticket information for: " + event_title)
    json_data = fetch_url(json_url).json()

    # Check if the fetch operation was successful
    if json_data is None:
        print("Failed to fetch data from:", json_url)
        return []

    # Check if 'json_data' is a dictionary containing 'item_types', and it's not empty
    if not isinstance(json_data, dict) or 'item_types' not in json_data or not json_data['item_types']:
        print("Error in json response structure.")
        return []

    voksen_item_type = next(item for item in json_data["item_types"] if item["title"] == "Voksen")
    voksen_sections = [
        {"section_id": section["id"], "has_available_tickets": section["has_available_tickets"]}
        for section in voksen_item_type["sections"]
    ]
    results = []
    if voksen_sections.__len__() > 0:
        # sections = [section["id"] for section in json_data["item_types"][0]["sections"]]
        progress_bar = tqdm(total=len(voksen_sections), desc="Counting sections", unit="section")
        with ThreadPoolExecutor() as executor:
            ticket_info = [executor.submit(get_section_tickets, section, event_url, progress_bar) for section in
                           voksen_sections]
        results = [info.result() for info in ticket_info]
        progress_bar.close()
    else:
        print("Couldn't find section 'voksen' in the json_data")
    return results


def get_section_tickets(section, event_url: str, progressbar) -> Optional[Dict]:
    """Fetch and organize seat information for a specific section of the arena.
    Args:
        section:
            The ID of the arena section to fetch ticket information for.
        event_url (str):
            The URL of the event.
        progressbar:
            The progress bar object to update during execution.
    Returns:
        Optional[Dict]:
            A dictionary containing organized stats and details of all seats in the section.
    """
    section_id = section['section_id']  # This expects a dictionary with a 'section_id' key
    visibility = section['has_available_tickets']

    json_url = event_url + "sections/" + str(section_id) + ".json"
    try:
        json_data = fetch_url(json_url).json()
    except (json.JSONDecodeError, AttributeError):
        print(f"Failed to decode JSON from URL: {json_url}")
        return None

    section_name = json_data["seating_arrangements"]["section_name"]
    section_total = json_data["seating_arrangements"]["section_amount"]

    if "stå" in str(section_name).lower():
        sold_seats = 0
        available_seats = 0
        locked_seats = 0
        phantom_seats = 0
        available_seats_object = None
    else:
        seats = [seat for seat in json_data["seating_arrangements"]["seats"]]
        sold_seats = len([seat for seat in seats if seat["status"] == "sold"])
        available_seats_object = [seat for seat in seats if seat["status"] == "available"]
        available_seats = len(available_seats_object)
        locked_seats = len([seat for seat in seats if seat["status"] == "locked"])
        phantom_seats = len([seat for seat in seats if float(seat["x"]) <= 0 and seat["status"] == "available"])
        available_seats -= phantom_seats
        section_total -= phantom_seats
    progressbar.update(1)
    return {
        "section_name": section_name,
        "section_id": section_id,
        "section_amount": section_total,
        "sold_seats": sold_seats,
        "available_seats": available_seats,
        "locked_seats": locked_seats,
        "phantom_seats": phantom_seats,
        # "seats": available_seats_object,
        "visible": visibility
    }


def save_new_json(event_title, data) -> str:
    dir_path, dir_path_simple = get_directory_path(event_title)
    time_now = get_time_formatted("computer")
    filename = f"results_{time_now}.json"

    file_path = os.path.join(dir_path, filename)
    with open(file_path, "w") as json_file:
        json.dump(data, json_file)
        print(f"Json file saved to {dir_path_simple}")
    return dir_path


def get_directory_path(event_name: str):
    valid_dir_name = (re.sub(r'[<>:"/\\|?*]', '', event_name)
                      .replace(' ', '')
                      .replace('\n', ''))
    dir_path = os.path.join(SAVE_PATH, f"matches/{valid_dir_name}")
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    return dir_path, f"matches/{valid_dir_name}"


def get_time_formatted(computer_or_human: str) -> str:
    """Formats the current time in a specified format.

    This function returns the current time formatted either for easy chronological file sorting
    ('computer' option) or in a human-readable format with Norwegian timezone and formatting
    ('human' option).
    Args:
        computer_or_human (str):
            The format specification, accepts 'computer' or 'human'.
    Returns:
        str:
            The formatted current time as a string.
    """
    norway_timezone = pytz.timezone("Europe/Oslo")
    current_datetime = datetime.now(norway_timezone)

    if computer_or_human.lower() == "computer":
        return str(current_datetime.strftime("%Y-%m-%d_%H-%M-%S"))
    else:
        return str(current_datetime.strftime("%H:%M %d/%m/%Y"))


def get_europe_from_event_title(event_title):
    event_title_lower = event_title.lower()
    # If there are special requirements for UEFA matches.
    if "conference" in event_title_lower or "europa" in event_title_lower or "champions" in event_title_lower:
        return True
    return False


def get_venue_from_event_date(event_date: str) -> str:
    """Extracts the venue from the event date string."""
    venue_start_index = event_date.find("@") + 1
    venue = event_date[venue_start_index:].strip()
    return venue


def get_latest_file(dir_path: str) -> Tuple[Dict, Optional[Dict]]:
    """Fetches the two most recent files in a directory.

    The function returns the data of the two most recently edited files in a directory.
    If there is only one file, the second element in the tuple will be None.
    Args:
        dir_path (str):
            The path to the directory.
    Returns:
        Tuple[Dict, Optional[Dict]]:
            The most recent and the second most recent file data, if available.
    """
    files = os.listdir(dir_path)
    sorted_files = sorted(files, key=lambda x: os.path.getmtime(os.path.join(dir_path, x)), reverse=True)
    if len(sorted_files) > 1:
        latest_file_path = os.path.join(dir_path, sorted_files[0])
        prior_file_path = os.path.join(dir_path, sorted_files[1])
        with open(latest_file_path, "r") as json_file:
            latest_file = json.load(json_file)
        with open(prior_file_path, "r") as json_file:
            prior_file = json.load(json_file)
        return latest_file, prior_file
    else:
        latest_file_path = os.path.join(dir_path, sorted_files[0])
        with open(latest_file_path, "r") as json_file:
            return json.load(json_file), None


def create_string(dir_path: str) -> str:
    """Creates a formatted string with ticket information for a tweet.

    The function generates a string with ticket information, including differences in ticket sales
    compared to the previous data point, ready to be posted as a tweet.
    Args:
        dir_path (str):
            The path to the event directory.
    Returns:
        str:
            A string containing the formatted ticket information.
    """
    latest, prior = get_latest_file(dir_path)
    time = "NaN"
    return_value = ""

    for category, data in latest.items():
        if "GENERAL" in category:
            return_value = data["title"] + "\n" + data["date"] + "\n\n"
            time = data["time"]
            continue

        available_seats = data["available_seats"]
        total_capacity = data["section_amount"]
        sold_seats = total_capacity - available_seats
        percentage_sold = (sold_seats / total_capacity) * 100 if total_capacity != 0 else 0

        if category.lower() == "totalt":  # Adds newline before the totals
            return_value += "\n"

        if prior is not None:
            prior_available_seats = prior[category]["available_seats"]
            prior_total_capacity = prior[category]["section_amount"]
            prior_sold_seats = prior_total_capacity - prior_available_seats

            diff_sold_seats = sold_seats - prior_sold_seats
            if diff_sold_seats == 0:
                return_value += f"{category.ljust(10)} {f'{sold_seats}/{total_capacity}'.ljust(12)}" \
                                f"{f''.ljust(7)} {percentage_sold:.1f}%\n"
            else:
                return_value += f"{category.ljust(10)} {f'{sold_seats}/{total_capacity}'.ljust(12)}" \
                                f"{f'{diff_sold_seats:+}'.ljust(7)} {percentage_sold:.1f}%\n"
        else:
            return_value += (f"{category.ljust(10)} {f'{sold_seats}/{total_capacity}'.ljust(12)} "
                             f"{percentage_sold:.1f}%\n")
    return_value += f"\n\nOppdatert: {time}\n "
    return return_value
