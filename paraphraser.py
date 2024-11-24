import os
import time
import re
import random
import json
import pyperclip
import base64
from colorama import Fore
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Gmail API scope
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate_gmail():
    creds = None
    # The token.json file stores the user's access and refresh tokens.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If there are no valid credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())  # This was causing the error
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run.
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return creds

def generate_gmail_variation(base_email):
    local_part, domain = base_email.split('@')

    # Ensure that the local part has more than one character to allow for dot insertion
    if len(local_part) <= 2:
        return base_email  # Not enough characters to add dots

    # Convert the local part into a list of characters
    local_part_variants = list(local_part)

    # Determine how many dots can be inserted (max: length of local_part - 1)
    max_dots = len(local_part) - 2  # Avoid starting and ending positions
    num_dots = random.randint(1, max_dots) if max_dots > 0 else 0

    # Select random positions to insert dots, ensuring no consecutive dots
    dot_positions = sorted(random.sample(range(1, len(local_part) - 1), num_dots))

    # Insert dots at the selected positions
    for i, pos in enumerate(dot_positions):
        if local_part_variants[pos - 1] != '.':
            local_part_variants.insert(pos + i, '.')

    # Join the modified local part and return the new email address
    return ''.join(local_part_variants).strip('.') + '@' + domain

def extract_verify_link(text):
    pattern = r'https://undetectable\.ai/api/auth/callback/sendgrid\?[^"]+'
    matches = re.findall(pattern, text)
    return matches[0] if matches else None

def get_gmail_service(creds):
    return build('gmail', 'v1', credentials=creds)

def search_for_confirmation_email(service, query='subject:Sign in to Undetectable AI'):
    results = service.users().messages().list(userId='me', q=query).execute()
    messages = results.get('messages', [])
    
    if not messages:
        print("No confirmation email found.")
        return None
    
    message = service.users().messages().get(userId='me', id=messages[0]['id'], format='full').execute()
    return message

def get_message_body(message):
    if 'parts' in message['payload']:
        # Iterate through all parts of the email
        for part in message['payload']['parts']:
            # Check if the part is HTML
            if part['mimeType'] == 'text/html':
                msg_data = part['body'].get('data', '')
                decoded_data = base64.urlsafe_b64decode(msg_data).decode('utf-8')
                print(f"Extracted HTML part: {decoded_data[:500]}")  # Print part of the content for debugging
                return decoded_data
            # Fallback to plain text if no HTML part found
            elif part['mimeType'] == 'text/plain':
                msg_data = part['body'].get('data', '')
                decoded_data = base64.urlsafe_b64decode(msg_data).decode('utf-8')
                print(f"Extracted plain text part: {decoded_data[:500]}...")  # Print part of the content for debugging
                return decoded_data
    else:
        # Handle case where the message does not have parts (e.g., it's a single text/plain or text/html email)
        msg_data = message['payload']['body'].get('data', '')
        decoded_data = base64.urlsafe_b64decode(msg_data).decode('utf-8')
        print(f"Extracted single body message: {decoded_data[:500]}...")  # Print part of the content for debugging
        return decoded_data
    return ''

def automate_sign_in(temp_email):
    options = webdriver.ChromeOptions()
    options.add_argument("--log-level=3")
    options.add_argument("--incognito")
    options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    driver = webdriver.Chrome(options=options)

    try:
        # Go to the Undetectable AI login page
        driver.get('https://undetectable.ai/login')

        # Enter the Gmail address into the email input field
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@name='email']"))
        )
        email_input.send_keys(temp_email)

        # Click on the "continue" button
        sign_in_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Continue']"))
        )
        driver.execute_script("arguments[0].click();", sign_in_button)

        print(f"Sign-in attempt made with email: {temp_email}")
    
    except Exception as e:
        print(f"Error during sign-in process: {e}")
    
    finally:
        driver.quit()

def wait_for_confirmation_email(service, max_wait_time=300, poll_interval=10):
    start_time = time.time()
    while time.time() - start_time < max_wait_time:
        confirmation_email = search_for_confirmation_email(service)
        if confirmation_email:
            print(f"{Fore.GREEN}Confirmation email found!")
            return confirmation_email
        print(f"{Fore.YELLOW}Waiting for the confirmation email... polling again in {poll_interval} seconds.")
        time.sleep(poll_interval)  # Wait for the next poll
    print(f"{Fore.RED}Timeout: Confirmation email not received within {max_wait_time} seconds.")
    return None

def main(purpose_choice, readability_choice, article_file_path, base_email):
    try:
        with open(article_file_path, 'r', encoding="utf8") as article_file:
            article_text = article_file.read()

        # Split the article into chunks of 250 words
        words = article_text.split()
        chunk_size = 250
        article_chunks = [' '.join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]

        if not article_chunks:
            print(f"{Fore.RED}Your file is empty.")
            return

        # Initialize the WebDriver
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--log-level=3")
        options.add_argument('--no-proxy-server')
        options.add_argument("--incognito")
        options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])

        # Authenticate Gmail and get the service object
        creds = authenticate_gmail()
        service = get_gmail_service(creds)

        while article_chunks:
            # Generate Gmail variant email
            email_variant = generate_gmail_variation(base_email)

            # Automate the sign-in process using the new function
            automate_sign_in(email_variant)

            driver = webdriver.Chrome(options=options)

            # Wait for the confirmation email to arrive using the polling method
            confirmation_email = wait_for_confirmation_email(service)
            if confirmation_email:
                message_body = get_message_body(confirmation_email)
                verify_link = extract_verify_link(message_body)
                if verify_link:
                    driver.get(verify_link)
                    time.sleep(1)
                else:
                    print(f"{Fore.RED}Verify link not found in email.")
            else:
                print(f"{Fore.RED}No confirmation email found.")

            driver.get('https://undetectable.ai/')

            # Now fill out the form to paraphrase the text
            try:
                wait = WebDriverWait(driver, 10)
                purpose = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="scrollElement"]/div/div/div[1]/div/div[1]/div/div[1]/div[2]/select')))
                readability = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="scrollElement"]/div/div/div[1]/div/div[1]/div/div[1]/div[1]/select')))
                
                select1 = Select(purpose)
                select2 = Select(readability)

                options1 = select1.options
                options2 = select2.options

                if 1 <= purpose_choice <= len(options1) - 1:
                    select1.select_by_index(purpose_choice)

                if 1 <= readability_choice <= len(options2) - 1:
                    select2.select_by_index(readability_choice)

                # Get the next chunk to submit
                chunk = article_chunks.pop(0)

                textarea = driver.find_element(By.XPATH, '//*[@id="scrollElement"]/div/div/div[1]/div/div[2]/div/textarea')
                textarea.clear()
                textarea.send_keys(chunk)

                time.sleep(1)

                humanize = driver.find_element(By.ID, 'humanize-tooltip')
                driver.execute_script("arguments[0].click();", humanize)
                
                try : 
                    driver.execute_script("document.querySelector('.iubenda-banner-content').style.display = 'none';")
                except: 
                    pass

                paraphrased = WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="copy-output"]')))
                paraphrased.click()

                time.sleep(1)

                copied_content = pyperclip.paste()

                with open('paraphrased.txt', 'a') as new:
                    new.write(f'{copied_content}\n')

            except Exception as e:
                print(f"{Fore.RED}Error during paraphrasing: {e}")
            finally:
                driver.quit()
                
        print(f"{Fore.GREEN}\nArticle has been paraphrased successfully.")

    except Exception as e:
        print(f"{Fore.RED}Error during article submission: {e}")
        raise

'''
if __name__ == "__main__":
    try:
        print(f'{Fore.GREEN}1. General Writing\n2. Essay\n3. Article\n4. Marketing Material\n5. Story\n6. Cover letter\n7. Report\n8. Business Material\n9. Legal Material\n')
        purpose_choice = int(input(f'{Fore.CYAN}Select the purpose of your writing: {Fore.GREEN}'))
        print(f'{Fore.GREEN}\n1. High School\n2. University\n3. Doctorate\n4. Journalist\n5. Marketing')
        readability_choice = int(input(f'\n{Fore.CYAN}Select the readability of your writing: {Fore.GREEN}'))
        article_file_path = input(f"\n{Fore.CYAN}Enter the path to the text file containing your article: {Fore.GREEN}")
        base_email = input(f"\n{Fore.CYAN}Enter your base Gmail address: {Fore.GREEN}")

        main(purpose_choice, readability_choice, article_file_path, base_email)
    except Exception as e:
        print(f"{Fore.RED}Aborting due to error: {e}")
        raise
'''
