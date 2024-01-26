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


msg_text = "Stante l'elevata richiesta i posti disponibili per il servizio scelto sono esauriti. Si invita a controllare con frequenza la disponibilità in quanto l’agenda viene aggiornata regolarmente"

time_format = "%Y-%m-%d - %H:%M:%S"


class booking_bot:

    # ---------------------------------------------------------------------------------------------
    def __init__(self, site_url):

        load_dotenv()

        self.site_url = site_url
        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 60)

    # ---------------------------------------------------------------------------------------------

    def login(self):

        self.driver.get(self.site_url)

        username_field = self._wait_and_get_where_id_is_('login-email')
        username_field.send_keys(os.environ.get('PRENOTAMI_USERNAME'))

        password_field = self._wait_and_get_where_id_is_('login-password')
        password_field.send_keys(os.environ.get('PRENOTAMI_PASSWORD'))

        confirm_button = self._wait_and_get_where_classname_is_(
            'button.primary.g-recaptcha')
        confirm_button.click()

    def _wait_and_get_where_id_is_(self, descriptor):
        return self.wait.until(
            EC.presence_of_element_located((By.ID, descriptor)))

    def _wait_and_get_where_classname_is_(self, descriptor):
        return self.wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, descriptor)))

    # ---------------------------------------------------------------------------------------------

    def check_for_available_bookings_every_(self, x_seconds):

        while True:

            if self._service_to_book_is_available():

                sleep(400)
                self._confirm_user_data_to_access_calendar()
                self._find_available_date_and_book()

                print('Booked?')
                self.driver.quit()

            else:
                print(
                    f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} -- No dates available, retrying in 40 secs.')
                sleep(x_seconds)

    # --------------------------------------------------------------------------------------------

    def _service_to_book_is_available(self):

        try:
            self.driver.get(self.site_url+'Services/Booking/224')
            sleep(10)

            soup = BeautifulSoup(self.driver.page_source, 'html.parser')

            booking_unavailable_pop_up_msg = soup.find(
                'div',    class_='jconfirm-content')

            if booking_unavailable_pop_up_msg:

                if (msg_text != booking_unavailable_pop_up_msg.text.strip()):
                    print(booking_unavailable_pop_up_msg.text.strip())

                booking_unavailable_confirm_button = self._wait_and_get_where_classname_is_(
                    "btn-blue")
                booking_unavailable_confirm_button.click()

                return False

            else:
                print('We found no pop up. Taking a screenshot.')

                self.driver.save_screenshot("screenshot.png")

                self._raise_alert()

                return True

        except Exception as e:
            print(f"An error occurred at service_to_book_is_available: {e}")

    # --------------------------------------------------------------------------------------------

    def _confirm_user_data_to_access_calendar(self):

        privacy_policy_checkbox = self._wait_and_get_where_id_is_(
            'PrivacyCheck')

        # mark the checkbox
        if not privacy_policy_checkbox.is_selected():
            privacy_policy_checkbox.click()

        confirm_button = self._wait_and_get_where_id_is_('btnAvanti')
        confirm_button.click()

        # give time for the elements to load

        # print('hello there')
        # sleep(10)

        # Switch to the confirmation dialog
        confirmation_dialog = self.driver.switch_to.alert

        # Accept the confirmation dialog (click "OK")
        confirmation_dialog.accept()

    # --------------------------------------------------------------------------------------------

    def _find_available_date_and_book(self):

        # check the next 24 months
        # soup = BeautifulSoup(driver.page_source, 'html.parser')

        max_attempts = 12
        attempts = 0

        while attempts < max_attempts:

            try:
                available_date_value = self._wait_and_get_where_classname_is_(
                    'day.availableDay')
                available_date_value.click()

                print(
                    f'''Next available date is {available_date_value.text}.''')

                hour_block = self._wait_and_get_where_classname_is_('dot')
                hour_block.click()

                submit = self._wait_and_get_where_id_is_('btnPrenotaNoOtp')
                submit.click()

                print(submit.text)

                print('reservation successfull, breaking the loop')
                break

            except NoSuchElementException:

                # Handle the case where the element was not found
                next_month_button = self._wait_and_get_where_classname_is_(
                    'dtpicker-next')

                next_month_button.click()

                print(f"There were no available dates, checking next month.")
                attempts += 1

            # Add a sleep to avoid continuous looping too quickly
            sleep(2)

            if attempts >= max_attempts:
                print("Exceeded maximum attempts. Exiting the loop.")

    # ---------------------------------------------------------------------------------------------

    def report_error_and_restart_after_(self, x_seconds):

        self._raise_alert_error()
        print(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - ERROR --> Restarting ')
        self.driver.quit()
        sleep(x_seconds)

    # ---------------------------------------------------------------------------------------------

    def _raise_alert_error(self):

        notification_script = 'display notification "Exit by error!" with title "Bye"'

        try:
            # Run the AppleScript commands to display a notification
            subprocess.run(["afplay", "/System/Library/Sounds/Ping.aiff"])
            # subprocess.run(['osascript', '-e', notification_script])

        except Exception as e:
            print(f"An error occurred: {e}")

    # ---------------------------------------------------------------------------------------------
    def _raise_alert(self):

        notification_script = 'display notification "New dates available!" with title "ALERT"'

        try:
            # Run the AppleScript commands to display a notification
            subprocess.run(["afplay", "/System/Library/Sounds/Ping.aiff"])
            # subprocess.run(['osascript', '-e', notification_script])
        except Exception as e:
            print(f"An error occurred: {e}")


# campo
# <input type="text" placeholder="OTP" id="otp-input" name="otp-input" class="name form-control" style="margin-bottom:20px;" required="">
# boton de enviar nuevo codice
# <input type="text" placeholder="OTP" id="otp-input" name="otp-input" class="name form-control" style="margin-bottom:20px;" required="">

# //*[@id="PrivacyCheck"]  /html/body/main/form/div/div[5]/div/div/input[1]    check de privacidad
