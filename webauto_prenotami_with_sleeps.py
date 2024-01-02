import requests
import subprocess
# import keyboard
import random

from bs4 import BeautifulSoup
from datetime import datetime
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from time import sleep
from dotenv import load_dotenv


site_url = "https://prenotami.esteri.it/"

msg_text = "Stante l'elevata richiesta i posti disponibili per il servizio scelto sono esauriti. Si invita a controllare con frequenza la disponibilità in quanto l’agenda viene aggiornata regolarmente"

# -------------------------------------------------------------------


def login(driver):

    # Load environment variables from .env file
    load_dotenv()

    sleep(5)

    username_field = driver.find_element(By.ID, 'login-email')
    password_field = driver.find_element(By.ID, 'login-password')

    username_field.send_keys(os.environ.get('USERNAME'))
    password_field.send_keys(os.environ.get('PASSWORD'))

    sleep(5)

    confirm_button = driver.find_element(
        By.CLASS_NAME, 'button.primary.g-recaptcha')
    confirm_button.click()


# -------------------------------------------------------------------
def service_to_book_is_available(driver):

    sleep(random.randint(10, 40))
    driver.get(site_url+'Services/Booking/224')  # 224

    # Here we should catch the popup:

    # if present: click and wait a random time like 20 to 50 min
    # else:   continue the navigation
    sleep(random.randint(10, 40))

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    pop_up_object = soup.find('div',    class_='jconfirm-content')

    if pop_up_object:

        if (msg_text != pop_up_object.text.strip()):
            print(pop_up_object.text.strip())

        ok_button = driver.find_element(By.CLASS_NAME, "btn-blue")

        ok_button.click()

        return False

    else:
        print('no pop up / Booking available')

        driver.save_screenshot("screenshot.png")

        macos_alert()

        return True


# -------------------------------------------------------------------
def confirm_user_data_to_access_calendar(driver):

    privacy_policy_checkbox = driver.find_element(By.ID, 'PrivacyCheck')

    # mark the checkbox
    if not privacy_policy_checkbox.is_selected():
        privacy_policy_checkbox.click()

    confirm_button = driver.find_element(By.ID, 'btnAvanti')
    confirm_button.click()

    # give time for the elements to load
    sleep(1)

    # Switch to the confirmation dialog
    confirmation_dialog = driver.switch_to.alert

    # Accept the confirmation dialog (click "OK")
    confirmation_dialog.accept()


# -------------------------------------------------------------------
def find_available_date_and_book(driver):

    # check the next 24 months
    # soup = BeautifulSoup(driver.page_source, 'html.parser')

    max_attempts = 2
    attempts = 0

    while attempts < max_attempts:

        try:
            available_date_value = driver.find_element(
                By.CLASS_NAME, 'day.availableDay')
            print(f'''Next available date is {available_date_value.text}.''')

            available_date_value.click()

            sleep(3)

            hour_block = driver.find_element(By.CLASS_NAME, 'dot')
            hour_block.click()

            submit = driver.find_element(By.ID, 'btnPrenotaNoOtp')
            print(submit.text)
            # submit.click()

            print('reservation successfull, breaking the loop')
            break

        except NoSuchElementException:

            sleep(3)

            # Handle the case where the element was not found
            next_month_button = driver.find_element(
                By.CLASS_NAME, 'dtpicker-next')
            next_month_button.click()

            print(f"There were no available dates, checking next month.")
            attempts += 1

        # Add a sleep to avoid continuous looping too quickly
        sleep(2)

        if attempts >= max_attempts:
            print("Exceeded maximum attempts. Exiting the loop.")


def macos_alert():

    # AppleScript command to display a notification
    notification_script = 'display notification "New dates available!" with title "ALERT"'

    try:
        # Run the AppleScript commands
        # subprocess.run(["afplay", "/System/Library/Sounds/Ping.aiff"])
        subprocess.run(['osascript', '-e', notification_script])
    except Exception as e:
        print(f"An error occurred: {e}")


def macos_alert_error():

    # AppleScript command to display a notification
    notification_script = 'display notification "Exit by error!" with title "Bye"'

    try:
        # Run the AppleScript commands
        # subprocess.run(["afplay", "/System/Library/Sounds/Ping.aiff"])
        subprocess.run(['osascript', '-e', notification_script])
    except Exception as e:
        print(f"An error occurred: {e}")


# -------------------------------------------------------------------
if __name__ == "__main__":

    while True:

        driver = webdriver.Chrome()  # options=chrome_options)
        driver.get(site_url)

        login(driver)

        try:
            while True:

                if service_to_book_is_available(driver):

                    confirm_user_data_to_access_calendar(driver)

                    find_available_date_and_book(driver)

                    print('Booked?')

                    driver.quit()

                else:
                    print(f'''Booking unavailable at: {datetime.now()} .''')
                    sleep(40)

                # # Check if the Escape key is pressed
                # if keyboard.is_pressed('esc'):
                #     print("Escape key pressed. Exiting loop.")
                #     break

        except:
            macos_alert_error()
            print(f'''Restarting due to error at: {datetime.now()}''')
            driver.quit()
            sleep(40)
