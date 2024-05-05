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
    """
    Sends a GET request to the specified URL.
    Parameters:
        url (str): The URL to fetch.
    Returns:
        requests.Response | None: The server's response to the request.
    """
    try:
        response = session.get(url)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching {url}: {e}")
        return None


def get_upcoming_events(next_or_all: str, homepage_url: str, ignore_list: set[str]) -> List[Dict[str, Any]]:
    """
    Retrieves a list of upcoming events from the specified homepage URL.
    Parameters:
        next_or_all (str): Specifies whether to fetch 'next' or 'all' events.
        homepage_url (str): The URL of the homepage from which to scrape events.
        ignore_list (set[str]): A set of words to ignore in event titles.
    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing event details.
    """
    print(f"Connecting to {homepage_url}")
    page_html = fetch_url(homepage_url)
    if page_html is None:
        print("An error occurred: Couldn't fetch HTML")
        return []

    soup = BeautifulSoup(page_html.text, "html.parser")
    event_list = []
    try:
        event_containers = soup.find_all("div", class_="tc-events-list--details")
    except AttributeError:
        print("Error: The HTML does not contain any divs with class 'tc-events-list--details'.")
        return []

    for index, event in enumerate(event_containers, start=1):
        a_element = event.find("a", class_="tc-events-list--title")
        if not a_element:
            print(f"Couldn't find the title for the event at index {index}.")
            continue
        event_title = a_element.get_text(strip=True)

        if ignore_list and any(word in event_title.lower() for word in ignore_list):
            print(f"Ignoring event '{event_title}' due to ignore list.")
            continue

        place_time = event.find("div", class_="tc-events-list--place-time")
        event_date_time = place_time.get_text(strip=True) if place_time else None

        event_link = get_nested_link(a_element.get("href"), event_title)
        if event_link is None:
            continue

        event_list.append({"title": event_title, "time": event_date_time, "link": event_link})

        if next_or_all.lower() == "next":
            break

    events = len(event_list)
    print(f"Done! Added a total of {events} events.")
    return event_list


def get_nested_link(url: str, event_title: str) -> Optional[str]:
    """
    Fetches the nested URL from a given event URL which links directly to the purchase page.
    Parameters:
        url (str): URL of the event's page to scrape.
        event_title (str): Title of the event, used for logging purposes.
    Returns:
        Optional[str]: URL of the purchase page, or None if not found or an error occurs.
    """
    try:
        page_html = fetch_url(url)
        if page_html is None:
            print(f"An error occurred: Couldn't fetch HTML for {url}")
            return None
        soup = BeautifulSoup(page_html.text, "html.parser")
        event_url = soup.find("a", id="placeOrderLink")
        if event_url is not None:
            return event_url.get("href")
    except Exception as e:
        print(f"Error fetching nested URL for '{event_title}': {e}")
    return None


def get_ticket_info(event_url: str, event_title: str) -> List[Dict[str, Any]]:
    """
    Retrieves and processes ticket information from a given event URL.
    Parameters:
        event_url (str): URL to the ticket information JSON.
        event_title (str): Title of the event, used for logging purposes.
    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing ticket sections and availability.
    """
    json_url = f"{event_url}item_types.json"
    print(f"\nUpdating ticket information for: {event_title}")
    try:
        json_data = fetch_url(json_url).json()
        if not json_data or 'item_types' not in json_data or not json_data['item_types']:
            print("Error in JSON response structure.")
            return []
    except Exception as e:
        print(f"Failed to fetch or parse JSON from {json_url}: {e}")
        return []

    sections_data = next((item for item in json_data["item_types"] if item["title"] == "Voksen"), json_data["item_types"][0])
    is_voksen = sections_data["title"] == "Voksen" if sections_data else False

    sections = [
        {"section_id": section["id"], "has_available_tickets": section["has_available_tickets"] if is_voksen else False}
        for section in sections_data["sections"]
    ]

    results = []
    if sections:
        with tqdm(total=len(sections), desc="Counting sections", unit="section") as progress_bar, ThreadPoolExecutor() as executor:
            ticket_info = [executor.submit(get_section_tickets, section, event_url, progress_bar) for section in sections]
            results = [info.result() for info in ticket_info]
    else:
        print("No sections found in the JSON data.")
    return results


def get_section_tickets(section: Dict[str, Any], event_url: str, progressbar: tqdm) -> Optional[Dict[str, Any]]:
    """
    Fetches detailed ticket information for a specific section of an event.
    Parameters:
        section (Dict[str, Any]): A dictionary containing details about the event section.
        event_url (str): Base URL to fetch ticket information for the section.
        progressbar (tqdm): Progress bar instance for visual progress tracking.
    Returns:
        Optional[Dict[str, Any]]: Dictionary containing detailed ticket data, or None if errors occur.
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


def save_new_json(event_title: str, data: Any) -> str:
    """
    Saves the provided data into a JSON file, naming it based on the current timestamp.
    Parameters:
        event_title (str): Title of the event, used for directory naming.
        data (Any): Data to be saved into the JSON file.
            It can be a single dictionary or a list of dictionaries.
    Returns:
        str: Directory path where the file was saved.
    """
    dir_path, dir_path_simple = get_directory_path(event_title)
    time_now = get_time_formatted("computer")
    filename = f"results_{time_now}.json"

    file_path = os.path.join(dir_path, filename)
    with open(file_path, "w") as json_file:
        json.dump(data, json_file)
        print(f"Json file saved to {dir_path_simple}")
    return dir_path


def get_directory_path(event_name: str) -> Tuple[str, str]:
    """
    Generates a valid directory path for storing files related to an event, creating the directory if it does not exist.
    Parameters:
        event_name (str): The name of the event, used to generate the directory name.
    Returns:
        Tuple[str, str]: A tuple containing the full directory path and a simplified path.
    """
    valid_dir_name = re.sub(r'[<>:"/\\|?*]', '', event_name).replace(' ', '').replace('\n', '')
    dir_path = os.path.join(SAVE_PATH, f"matches/{valid_dir_name}")
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    return dir_path, f"matches/{valid_dir_name}"


def get_time_formatted(computer_or_human: str) -> str:
    """
    Formats the current time according to the specified format type ('computer' or 'human').
    Parameters:
        computer_or_human (str): Indicates the format type: 'computer' for logging and filenames, 'human' for display.
    Returns:
        str: The formatted time string.
    """
    norway_timezone = pytz.timezone("Europe/Oslo")
    current_datetime = datetime.now(norway_timezone)

    if computer_or_human.lower() == "computer":
        return current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
    else:
        return current_datetime.strftime("%H:%M %d/%m/%Y")


def get_europe_from_event_title(event_title: str) -> bool:
    """
    Determines if the event title contains keywords related to European football competitions.
    Parameters:
        event_title (str): The title of the event.
    Returns:
        bool: True if the event is related to European competitions, otherwise False.
    """
    event_title_lower = event_title.lower()
    return "conference" in event_title_lower or "europa" in event_title_lower or "champions" in event_title_lower


def get_venue_from_event_date(event_date: str) -> str:
    """
    Extracts the venue information from an event date string.
    Parameters:
        event_date (str): A string containing the date and venue.
    Returns:
        str: The extracted venue.
    """
    venue_start_index = event_date.find("@") + 1
    return event_date[venue_start_index:].strip()


def get_latest_file(dir_path: str) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
    """
    Retrieves the latest and the prior latest JSON file from a specified directory.
    Parameters:
        dir_path (str): The directory path from which to retrieve the files.
    Returns:
        Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]: A tuple containing the latest and prior latest JSON file data, or None if not available.
    """
    files = os.listdir(dir_path)
    sorted_files = sorted(files, key=lambda x: os.path.getmtime(os.path.join(dir_path, x)), reverse=True)
    latest_file_path = os.path.join(dir_path, sorted_files[0])
    with open(latest_file_path, "r") as json_file:
        latest_file = json.load(json_file)

    if len(sorted_files) > 1:
        prior_file_path = os.path.join(dir_path, sorted_files[1])
        with open(prior_file_path, "r") as json_file:
            prior_file = json.load(json_file)
        return latest_file, prior_file
    return latest_file, None


def create_string(dir_path: str) -> str:
    """
    Generates a summary string representing the comparison between the latest and prior event data.
    Parameters:
        dir_path (str): The directory path where the event files are stored.
    Returns:
        str: A formatted string summarizing the event data changes.
    """
    latest, prior = get_latest_file(dir_path)
    summary = ""
    time = "NaN"

    if not latest:
        return "No data available."

    for category, data in latest.items():
        if "GENERAL" in category:
            time = data.get("time", "NaN")
            summary += f"{data['title']}\n{data['date']}\n\n"
            continue

        available_seats = data.get("available_seats", 0)
        total_capacity = data.get("section_amount", 0)
        sold_seats = total_capacity - available_seats
        percentage_sold = (sold_seats / total_capacity * 100) if total_capacity != 0 else 0

        if category.lower() == "totalt":  # Adds newline before totals
            summary += "\n"

        if prior:
            prior_data = prior.get(category, {})
            prior_available_seats = prior_data.get("available_seats", 0)
            prior_total_capacity = prior_data.get("section_amount", 0)
            prior_sold_seats = prior_total_capacity - prior_available_seats
            diff_sold_seats = sold_seats - prior_sold_seats

            diff_indicator = f"{diff_sold_seats:+}" if diff_sold_seats != 0 else ""
            summary += f"{category.ljust(10)} {f'{sold_seats}/{total_capacity}'.ljust(12)}{diff_indicator.ljust(7)} {percentage_sold:.1f}%\n"
        else:
            summary += f"{category.ljust(10)} {f'{sold_seats}/{total_capacity}'.ljust(12)} {percentage_sold:.1f}%\n"

    summary += f"\n\nUpdated: {time}\n"
    return summary
