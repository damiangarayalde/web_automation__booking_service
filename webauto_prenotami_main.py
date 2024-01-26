from booking_bot import booking_bot

site_url = "https://prenotami.esteri.it/"

x_seconds = 40


# --------------------------------------------------------------
if __name__ == "__main__":

    bb = booking_bot(site_url)

    while True:

        bb.login()

        try:
            bb.check_for_available_bookings_every_(x_seconds)

        except:
            print('hello there')
            bb.report_error_and_restart_after_(x_seconds)
