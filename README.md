# BrannTicketCounter-v2

---
Brann Ticket Counter v2 is the latest iteration of the ticket counting application initially 
introduced [here](https://github.com/eyvmal/BrannTicketCounter/). This application is designed to monitor 
and report on ticket sales for upcoming football events, specifically for clubs using TicketCo services. 
It is important to note that this tool does not facilitate the purchase of tickets but rather 
provides updates on ticket sales to fans and interested parties.

The application automatically retrieves data on ticket availability from specified TicketCo platforms 
and generates visual updates.

### Improvements Over Version 1
* **Modularity:** The new architecture is more modular, making it significantly easier to add 
support for new clubs. While currently only configured for Brann, the system is designed to 
be extended to other teams in Norway's Eliteserien and Toppserien that utilize TicketCo for 
their ticketing services.
* **Enhanced Image Creation:** Improvements in the image generation feature include auto-scaling 
text, which adjusts to fit the content dynamically, and a more visually appealing static background.

### Future Plans
* **Database Integration:** To reduce storage space requirements, future versions plan to 
incorporate database usage. This will facilitate better data management and allow 
for historical data analysis and trend monitoring, providing richer insights into ticket sales 
patterns over time. 
* **Third-Party Application Interfaces:** With the foundational data organized within a database, 
there will be opportunities to develop third-party applications, such as mobile apps or web pages, 
that can display real-time updates, historical graphs, and other analytics. This will make the data 
more accessible to fans and analysts, allowing them to view ticket sales dynamics through 
interactive and user-friendly interfaces.
* **Predictive Analytics:** Leveraging historical data, the system could eventually offer 
predictions on ticket sales outcomes for upcoming matches. This feature would utilize data-driven 
insights to forecast sales trends, helping fans and organizers better anticipate ticket 
availability and demand.

### Disclaimer
* **Approximate Counts:** The numbers provided by this script may not always reflect the exact 
number of tickets available.
* **Exclusions:** The script does not count tickets in sections without assigned seating 
(e.g., standing sections).

---
# Setup and Installation
## Running Locally
### 1. Comment Out the Tweet Creation:
* Navigate to the run function within the specific club's Python file located at 
clubs/{clubname}/{clubname}.py.
Locate and comment out the following line to prevent the application from attempting to send 
tweets:```create_tweet(tweet_header, image_path_list)```

### 2. Modify the Main Function:
* Edit the main function in main.py to call the correct run function for the club you are 
interested in. Replace {clubname}_run() with the function corresponding to your specific club:
```
if __name__ == "__main__":
    {clubname}_run("all", False, False)

# For example
if __name__ == "__main__":
    brann_run("all", False, False)
```

## Setting Up Twitter Integration
To enable posting tweets through the Twitter API, you must provide your Twitter API credentials. 
Set up a .env file in the root directory of the project and include the following keys:
```
TWITTER_API_KEY="your_twitter_api_key"
TWITTER_API_KEY_SECRET="your_twitter_api_key_secret"
TWITTER_BEARER_TOKEN="your_twitter_bearer_token"
TWITTER_ACCESS_TOKEN="your_twitter_access_token"
TWITTER_ACCESS_TOKEN_SECRET="your_twitter_access_token_secret"
```

## Installation of Dependencies
Before running the application, install the required Python packages by running the following 
command in your terminal:

```pip install -r requirements.txt```

This command installs all the necessary packages, as specified in the requirements.txt file, 
which is crucial for the proper functioning of the project.

---