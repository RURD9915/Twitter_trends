import sys
import uuid
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pymongo import MongoClient
from urllib.parse import quote_plus

# URL encode your MongoDB username and password
username = quote_plus("shreyashk289")
password = quote_plus("Shreyas@2003")


# Twitter credentials
TWITTER_URL = "https://twitter.com/login"
USERNAME = "Rurd96969"
PASSWORD = "Shreyas@2003"
EMAIL = "rurd9916@gmail.com"

# MongoDB configuration
MONGO_URI = f"mongodb+srv://{username}:{password}@twitter.rc0mj.mongodb.net/?retryWrites=true&w=majority&appName=Twitter"
DATABASE_NAME = "twitter_trends"
COLLECTION_NAME = "trending_topics"


def fetch_trends():
    # Fetch the public IP used
    print("Fetching public IP...")
    try:
        response = requests.get("https://api64.ipify.org?format=json")
        if response.status_code == 200:
            public_ip = response.json().get("ip")
            print(f"Public IP being used: {public_ip}")
        else:
            print("Failed to fetch public IP.")
            public_ip = "Unknown"
    except Exception as e:
        print(f"Error fetching public IP: {e}")
        public_ip = "Unknown"

    # Configure Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode (optional)
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    # Initialize WebDriver without proxy
    try:
        driver = webdriver.Chrome(options=chrome_options)
    except Exception as e:
        print(f"Error initializing WebDriver: {e}")
        sys.exit(10)

    try:
        print("Launching Chrome browser...")
        driver.get(TWITTER_URL)

        # Log in to Twitter
        max_attempts_user = 10  # Maximum attempts for the username input process
        attempt_user = 0
        username_fetched = False

        while attempt_user < max_attempts_user and not username_fetched:
            attempt_user += 1
            print(f"Attempt {attempt_user} to enter username...")

            reload_attempts_user = 0
            while reload_attempts_user < 10 and not username_fetched:
                reload_attempts_user += 1
                print(f"Reload attempt {reload_attempts_user} for username input...")

                try:
                    # Wait for the username input field to appear and enter the username
                    print("Waiting for username input field...")
                    username_input = WebDriverWait(driver, 20).until(
                        EC.visibility_of_element_located((By.XPATH, "//input[@name='text']"))
                    )
                    username_input.send_keys(USERNAME)
                    username_input.send_keys(Keys.RETURN)
                    print("Username entered successfully.")
                    username_fetched = True
                    break  # Exit the loop if the username is entered successfully

                except Exception as e:
                    print(f"Failed to enter username on reload attempt {reload_attempts_user}. Exception: {e}")
                    if reload_attempts_user < 5:
                        print("Reloading the page for username input...")
                        driver.refresh()  # Reload the page and try again

        if username_fetched:
            print("Username entered successfully!")
        else:
            print("Failed to enter username after multiple attempts.")
            driver.quit()
            print("Browser closed.")
            sys.exit(2)

        # Handle the next input dynamically
        # noinspection PyBroadException
        try:
            print("Checking for password field...")
            password_input = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.XPATH, "//input[@name='password']"))
            )
            password_input.send_keys(PASSWORD)
            password_input.send_keys(Keys.RETURN)
            print("Password entered successfully.")
        except:
            print("Password field not found, entering email...")
            email_input = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.XPATH, "//input[@type='text']"))
            )
            email_input.send_keys(EMAIL)
            email_input.send_keys(Keys.RETURN)

            print("Checking for password field again...")
            password_input = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.XPATH, "//input[@name='password']"))
            )
            password_input.send_keys(PASSWORD)
            password_input.send_keys(Keys.RETURN)
            print("Password entered successfully.")

            # Check if another email slot appears
        # noinspection PyBroadException
        try:
            print("Checking for another email input...")
            additional_email_input = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.XPATH, "//input[@type='email']"))
            )
            additional_email_input.send_keys(EMAIL)
            additional_email_input.send_keys(Keys.RETURN)
            print("Additional email entered successfully.")
        except:
            print("No additional email input found.")

        # Wait for the page to load and fetch trending topics
        max_attempts = 5  # Maximum attempts to fetch sufficient trends
        attempt = 0
        top_5_trends = []

        # First, navigate to the trends and select the 'Timeline: Explore' section
        try:
            # Try to locate the "Show More" section of Trends
            show_more_button = None
            attempts = 0
            while show_more_button is None and attempts < 3:  # Retry up to 3 times
                try:
                    show_more_button = WebDriverWait(driver, 30).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, "//a[@href='/explore/tabs/for-you']")  # Adjust href value if necessary
                        )
                    )
                    show_more_button.click()
                    print("Navigated to 'Trends for You' page.")
                except Exception as e:
                    print(f"Failed to locate the 'Show More' button. Attempting page reload. Exception: {e}")
                    attempts += 1
                    driver.refresh()  # Reload the page and retry finding the button

            if show_more_button is None:
                print("Failed to locate the 'Show More' button after multiple attempts. Exiting...")
                driver.quit()
                sys.exit(3)

            # Navigate to the "Explore" section of Trends
            explore_section = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//a[@href='/explore/tabs/trending']")  # Adjust href value if necessary
                )
            )
            explore_section.click()
            print("Navigated to 'Explore' page.")

            # Wait for the 'Timeline: Explore' section to load
            explore_timeline = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[@aria-label='Timeline: Explore']")  # Ensure the section is loaded
                )
            )
            print("'Timeline: Explore' section is loaded. Starting to fetch trends...")

        except Exception as e:
            print(f"Failed to navigate to the explore page or load the 'Timeline: Explore' section. Exception: {e}")
            driver.quit()
            sys.exit(4)

        # Now start the retry loop for fetching trends
        while attempt < max_attempts:
            attempt += 1
            print(f"Attempt {attempt} to fetch trending topics...")

            reload_attempts = 0
            trends_fetched = False

            while reload_attempts < 3 and not trends_fetched:
                reload_attempts += 1
                print(f"Reload attempt {reload_attempts} for this iteration...")

                try:
                    # Locate the trends inside the specific CSS class within 'Timeline: Explore'
                    trend_elements = WebDriverWait(explore_timeline, 10).until(
                        EC.presence_of_all_elements_located(
                            (By.CSS_SELECTOR, "span.r-bcqeeo.r-1ttztb7.r-qvutc0.r-poiln3")
                        )
                    )

                    # Temporary list to store the first 25 fetched trends
                    # Assuming 'temp_trends' contains the full list of trends
                    temp_trends = [trend.text.strip() for trend in trend_elements[:100] if trend.text.strip()]
                    print(temp_trends)

                    # Create a list to store the selected trends
                    selected_trends = []

                    # Initialize the counter to track how many elements have been added
                    count = 0

                    # Iterate through the list
                    for i in range(len(temp_trends)):
                        # Stop the loop once we have added 5 elements
                        if count == 5:
                            break

                        # Check if the current element is the dot "·"
                        if temp_trends[i] == '·' and i + 2 < len(temp_trends):
                            # Append the element that comes 2 steps after the dot
                            selected_trends.append(temp_trends[i + 2])
                            count += 1  # Increment the counter

                    # Output the selected trends
                    print("Selected trends:", selected_trends)

                    top_5_trends.extend(selected_trends)  # Add these trends to the main list
                    trends_fetched = True  # Exit the reload loop as we've added the trends
                    break  # Exit the inner while loop

                except Exception as e:
                    print(f"Failed to fetch trends on reload attempt {reload_attempts}. Exception: {e}")
                    if reload_attempts < 3:
                        print("Reloading the page...")
                        driver.refresh()  # Reload the page and try again

            if trends_fetched:
                print("Sufficient trends fetched!")
                break  # Exit the main attempt loop if trends are fetched
            else:
                print(f"Failed to fetch sufficient trends after {reload_attempts} reload attempts.")
                driver.quit()
                print("Browser closed.")
                sys.exit(5)

        # Final check after the loop
        if len(top_5_trends) < 5:
            print("Failed to fetch at least 5 trends after multiple attempts.")
        else:
            print("Trending topics fetched successfully!")
            print("Top 5 Trending Topics:")
            for i, topic in enumerate(top_5_trends[:5], 1):  # Limit output to 5 trends
                print(f"{i}. {topic}")

        # Save the data to MongoDB
        print("Connecting to MongoDB...")
        try:
            client = MongoClient(MONGO_URI)
            db = client[DATABASE_NAME]
        except Exception as e:
            print(f"MongoDB connection failed: {e}")
            sys.exit(6)

        collection = db[COLLECTION_NAME]

        unique_id = str(uuid.uuid4())
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        record = {
            "_id": unique_id,
            "trends": top_5_trends,
            "timestamp": timestamp,
            "proxy_used": public_ip
        }
        collection.insert_one(record)
        print(f"Data saved to MongoDB successfully with ID: {unique_id}")
        driver.quit()
        print("Browser closed.")
        sys.exit(0)

    except Exception as e:
        print(f"An error occurred: {e}")
        driver.quit()
        print("Browser closed.")
        sys.exit(8)


fetch_trends()
