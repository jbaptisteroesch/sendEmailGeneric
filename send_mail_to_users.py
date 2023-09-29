import csv
import json
import smtplib
import ssl
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def load_csv_data(filename):
    """
    Load the CSV data from the specified file.

    :param filename: The name of the file to load the data from.
    :return: The loaded CSV data as a list of dictionaries.
    """
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            data = [row for row in reader]
        return data
    except FileNotFoundError:
        print(f"File {filename} not found.")
        return None
    except csv.Error:
        print(f"Could not decode CSV from file {filename}.")
        return None


def check_email_progress(user_data):
    try:
        with open('send_progress.json', 'r', encoding='utf-8') as file:
            progress_data = json.load(file)
    except FileNotFoundError:
        progress_data = []

    users_to_email = {}
    for user in user_data:
        email = user['email']
        if not any(d['email'] == email and d.get('email_sent') is True for d in progress_data):
            users_to_email[email] = user
    return users_to_email


def save_sending_progress(data):
    try:
        with open('send_progress.json', 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Failed to update JSON file: {e}")


def create_email_message(receiver_email, sender_email, forename, surname):
    """Create an email message with both plaintext and HTML content.

    Args:
        receiver_email (str): The recipient's email address.
        sender_email (str): The email of the sender.
        forename (str): The recipient's forename.
        surname (str): The recipient's surname.

    Returns:
        MIMEMultipart: The email message object.
    """

    message = MIMEMultipart("alternative")
    message["Subject"] = "Première mission aux Chimiques de Thann - Votre progression ? Des difficultés ?"
    message["From"] = sender_email
    message["To"] = receiver_email

    text = """\
    Bonjour {0} {1},
    Nous espérons que le jeu "Première mission aux Chimiques de Thann : un sans faute ?" vous plait !
    Si vos choix vous ont emmené vers le succès de la mission, avez-vous été tenté d'essayer d'autres choix que vous ne feriez jamais dans la vraie vie?
    Avez-vous déjà trouvé la girafe ? le minotaure ? et Timon ?
    Si vous rencontrez des difficultés pour vous connecter via votre ordinateur, nous vous encourageons à essayer depuis votre smartphone. 
    N'hésitez pas à répondre à ce mail pour toute assistance supplémentaire.
    Bonne journée,
    L'Équipe SafeTrooper
    """
    html = """\
    <html>
      <body>
        <p>Bonjour {0} {1},</p>
        <p>Nous espérons que le jeu "Première mission aux Chimiques de Thann : un sans faute ?" vous plait !</p>
        <p>Si vos choix vous ont emmené vers le succès de la mission, avez-vous été tenté d'essayer d'autres choix que vous ne feriez jamais dans la vraie vie?<br />Avez-vous déjà trouvé la girafe ? le minotaure ? et Timon ?</p>
        <p>Si vous rencontrez des difficultés pour vous connecter via votre ordinateur, nous vous encourageons à essayer depuis votre smartphone.</p>
        <p>N'hésitez pas à répondre à ce mail pour toute assistance supplémentaire.</p>
        <p>Bonne journée,</p>
        <p>L'Équipe SafeTrooper</p>
      </body>
    </html>
    """

    formated_text = text.format(forename, surname)
    formated_html = html.format(forename, surname)

    part1 = MIMEText(formated_text, "plain")
    part2 = MIMEText(formated_html, "html")

    message.attach(part1)
    message.attach(part2)

    return message


def send_email(email_sender, app_password, receiver_email, message):
    """Send the email message to the recipient.

    Args:
        email_sender (str): The email address of the sender.
        app_password (str): The app password for the sender's email address.
        receiver_email (str): The recipient's email address.
        message (MIMEMultipart): The email message object.

    Returns:
        bool: True if the email was sent successfully, False otherwise.
    """
    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender_email = email_sender
    password_email = app_password

    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, password_email)
            server.sendmail(sender_email, receiver_email, message.as_string())
        return True
    except Exception as e:
        print(f"\nCould not send email to {receiver_email} due to {str(e)}")
        return False


def send_mail_to_users(csv_filename, email_sender, app_password):
    """Send emails to users from the data loaded from the JSON file.

    :param csv_filename: The name of the CSV file containing the user email address.
    :param email_sender: The email address of the sender.
    :param app_password: The app password for the sender's email address.

    """
    # Load the JSON data
    user_data = load_csv_data(csv_filename)

    # Check the email status for each user
    users_to_email = check_email_progress(user_data)

    # Create and send emails to users who haven't received emails yet
    email_counter = 0
    email_success = 0
    batch_size = 80
    delay_between_batches = 600  # 10 minutes in seconds
    total_emails = len(users_to_email)

    # Create and send emails to users who haven't received emails yet
    for email, user_details in users_to_email.items():
        receiver_email = email
        forename = user_details.get("forename")
        surname = user_details.get("surname")

        # Create the email message
        message = create_email_message(receiver_email, email, forename, surname)

        # Send the email
        email_sent = send_email(email_sender, app_password, receiver_email, message)

        # Update the emailSent status for the user
        user_details["email_sent"] = email_sent

        if email_sent:
            email_success += 1

        # Save the progress immediately
        save_sending_progress(user_data)

        # Print a message if the email failed to send
        if not email_sent:
            print(f"\nFailed to deliver message to user: {email}")

        # Update the email counter
        email_counter += 1

        # Display the email counter and the number of emails left
        print(f"\rEmails sent: {email_success}/{total_emails}, Emails left: {total_emails - email_counter}", end="")

        # If the batch size is reached, wait for 10 minutes before the next batch
        if email_counter % batch_size == 0:
            print(f"\nSent {email_success} emails, waiting for 10 minutes before sending the next batch...")

            # Display a countdown
            for remaining in range(delay_between_batches, 0, -1):
                mins, secs = divmod(remaining, 60)
                timer = '{:02d}:{:02d}'.format(mins, secs)
                print(f"\r{timer} before the next batch, hang tight...", end="")
                time.sleep(1)

    # Print a completion message once all emails have been sent
    print(f"\n\033[92mAll emails have been sent! Total emails sent: {email_success}/{total_emails}.\033[0m")
