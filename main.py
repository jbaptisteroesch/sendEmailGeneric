import os
import smtplib

from send_mail_to_users import send_mail_to_users

email_sender = ''
app_password = ''


def get_csv_filepath():
    """Prompt the user for a CSV file path and validate the input.

    Returns:
        str: The validated CSV file path.
    """
    while True:
        filepath = input("Please enter the path to the CSV file: ").strip()
        if os.path.isfile(filepath) and filepath.endswith('.csv'):
            return filepath
        else:
            print("Invalid file path or file type. Please enter a valid CSV file path.")


def authenticate_user():
    while True:
        global email_sender
        global app_password
        email_sender = input("Please enter your Google email: ")
        app_password = input("Please enter your app password: ")

        try:
            # Attempt to log in to the SMTP service using the provided credentials
            with smtplib.SMTP_SSL('smtp.gmail.com') as server:
                server.login(email_sender, app_password)

            # If the login is successful, the credentials are valid
            print("Authentication successful. Proceeding...")
            break
        except smtplib.SMTPAuthenticationError:
            # If authentication fails, an SMTPAuthenticationError is raised
            print("Authentication failed. Please verify your email and app password and try again.")


def main():
    print("\033[91mALERT: You are about to use a tool that interacts with the live production environment.")
    print("Misuse can have serious repercussions. Proceed with utmost caution and responsibility.")
    print("We strongly encourage you to read the README file before using the program if you haven't done so already."
          "\033[0m\n")

    authenticate_user()

    while True:
        try:
            print("Choose an option:")
            print("1: Send emails to users")
            print("2: Quit (q)")

            option = input("Enter your choice: ").strip()

            if option in {"1", "2", "q"}:
                if option == "1":
                    csv_filepath = get_csv_filepath()
                    confirmation = input(f"You are about to send emails to users. Confirm to proceed. (y/n): ").strip()
                    if confirmation == 'y':
                        send_mail_to_users(csv_filepath, email_sender, app_password)
                    else:
                        print("Option not confirmed, please try again.")
                elif option in {"2", "q"}:
                    print("Goodbye!")
                    break
            else:
                print("Invalid option. Please enter a valid option (1, or 2/q).")
        except ValueError:
            print("Invalid input. Please enter a number (1 or 2) or 'q'.")


if __name__ == '__main__':
    main()
