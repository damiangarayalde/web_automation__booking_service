import requests
import subprocess
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

time_format = "%Y-%m-%d - %H:%M:%S"


# -------------------------------------------------------------------


def login(driver):

    # Load environment variables from .env file
    load_dotenv()

    # Set an explicit wait with a maximum timeout of 60 seconds
    wait = WebDriverWait(driver, 60)

    username_field = wait.until(
        EC.presence_of_element_located((By.ID, 'login-email')))
    username_field.send_keys(os.environ.get('PRENOTAMI_USERNAME'))

    password_field = wait.until(
        EC.presence_of_element_located((By.ID, 'login-password')))
    password_field.send_keys(os.environ.get('PRENOTAMI_PASSWORD'))

    confirm_button = wait.until(EC.presence_of_element_located(
        (By.CLASS_NAME, 'button.primary.g-recaptcha')))
    confirm_button.click()


# -------------------------------------------------------------------
def service_to_book_is_available(driver):

    try:
        # Set an explicit wait
        wait = WebDriverWait(driver, 90)

        driver.get(site_url+'Services/Booking/224')
        sleep(random.randint(20, 40))

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        booking_unavailable_pop_up_msg = soup.find(
            'div',    class_='jconfirm-content')

        if booking_unavailable_pop_up_msg:

            if (msg_text != booking_unavailable_pop_up_msg.text.strip()):
                print(booking_unavailable_pop_up_msg.text.strip())

            booking_unavailable_confirm_button = wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "btn-blue")))
            booking_unavailable_confirm_button.click()

            return False

        else:
            print('We found no pop up. Taking a screenshot.')

            driver.save_screenshot("screenshot.png")

            macos_alert()

            return True

    except Exception as e:
        print(f"An error occurred at service_to_book_is_available: {e}")

# -------------------------------------------------------------------


def confirm_user_data_to_access_calendar(driver):

    # Set an explicit wait
    wait = WebDriverWait(driver, 40)

    privacy_policy_checkbox = wait.until(
        EC.presence_of_element_located((By.ID, 'PrivacyCheck')))

    # mark the checkbox
    if not privacy_policy_checkbox.is_selected():
        privacy_policy_checkbox.click()

    confirm_button = wait.until(
        EC.presence_of_element_located((By.ID, 'btnAvanti')))

    confirm_button.click()

    # give time for the elements to load

    # print('hello there')
    # sleep(10)

    # Switch to the confirmation dialog
    confirmation_dialog = driver.switch_to.alert

    # Accept the confirmation dialog (click "OK")
    confirmation_dialog.accept()


# -------------------------------------------------------------------
def find_available_date_and_book(driver):

    # check the next 24 months
    # soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Set an explicit wait
    wait = WebDriverWait(driver, 90)

    max_attempts = 12
    attempts = 0

    while attempts < max_attempts:

        try:
            available_date_value = wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, 'day.availableDay')))

            print(f'''Next available date is {available_date_value.text}.''')

            available_date_value.click()

            hour_block = wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, 'dot')))

            hour_block.click()

            submit = wait.until(
                EC.presence_of_element_located((By.ID, 'btnPrenotaNoOtp')))

            print(submit.text)
            submit.click()

            print('reservation successfull, breaking the loop')
            break

        except NoSuchElementException:

            # Handle the case where the element was not found
            next_month_button = wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, 'dtpicker-next')))

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
        subprocess.run(["afplay", "/System/Library/Sounds/Ping.aiff"])
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

                    sleep(400)

                    confirm_user_data_to_access_calendar(driver)

                    find_available_date_and_book(driver)

                    print('Booked?')

                    driver.quit()

                else:
                    print(
                        f'''{datetime.now().strftime(time_format)} -- No dates available, retring in 40 secs.''')
                    sleep(40)

        except:
            macos_alert_error()
            print(
                f'''{datetime.now().strftime(time_format)} - ERROR --> Restarting ''')
            driver.quit()
            sleep(40)

# campo
# <input type="text" placeholder="OTP" id="otp-input" name="otp-input" class="name form-control" style="margin-bottom:20px;" required="">
# boton de enviar nuevo codice
# <input type="text" placeholder="OTP" id="otp-input" name="otp-input" class="name form-control" style="margin-bottom:20px;" required="">

# //*[@id="PrivacyCheck"]  /html/body/main/form/div/div[5]/div/div/input[1]    check de privacidad
