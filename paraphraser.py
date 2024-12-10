import os
import time
import re
import random
import json
import pyperclip
import base64
import requests
from colorama import Fore
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from fake_useragent import UserAgent

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
                print(f"Extracted HTML part: {decoded_data[:500]}") 
                return decoded_data
            # Fallback to plain text if no HTML part found
            elif part['mimeType'] == 'text/plain':
                msg_data = part['body'].get('data', '')
                decoded_data = base64.urlsafe_b64decode(msg_data).decode('utf-8')
                print(f"Extracted plain text part: {decoded_data[:500]}")  
                return decoded_data
    else:
        # Handle case where the message does not have parts (e.g., it's a single text/plain or text/html email)
        msg_data = message['payload']['body'].get('data', '')
        decoded_data = base64.urlsafe_b64decode(msg_data).decode('utf-8')
        print(f"Extracted single body message: {decoded_data[:500]}")  
        return decoded_data
    return ''

def automate_sign_in(driver, temp_email):
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

        print(f"\nSign-in attempt made with email: {temp_email}")

    except Exception as e:
        print(f"Error during sign-in process: {e}")

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

def monitor_url_change(driver, target_success_url, error_url, timeout=10):
    start_time = time.time()
    while time.time() - start_time < timeout:
        current_url = driver.current_url

        if error_url in current_url:
            print(f"{Fore.RED}Magic link expired detected in URL: {current_url}")
            return False  # Error detected

        if target_success_url in current_url:
            print(f"{Fore.GREEN}Magic link verified successfully. Redirected to: {current_url}")
            return True  # Success detected

        time.sleep(1)  # Poll every 1s

    print(f"{Fore.YELLOW}Timeout reached while monitoring URL.")
    return None  # Timeout

def process_confirmation_link(driver, verify_link, service, email):
    try:
        # Open the magic link
        driver.get(verify_link)

        # Monitor for success or error
        result = monitor_url_change(driver, 
                                    target_success_url="https://undetectable.ai/pricing", 
                                    error_url="?error=Verification", 
                                    timeout=10)

        if result is True:
            print(f"{Fore.GREEN}Verification successful.")
            return True
        elif result is False:
            print(f"{Fore.RED}Magic link expired. Switching to OTP mode.")
            # Re-enter the email for OTP
            email_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@name='email']"))
            )
            email_input.clear()
            email_input.send_keys(email)

            continue_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Continue']"))
            )
            driver.execute_script("arguments[0].click();", continue_button)

            print(f"{Fore.YELLOW}Waiting for OTP input fields...")

            # Wait for the OTP fields to appear
            otp_fields = WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located((By.XPATH, "//input[starts-with(@id, 'otp-input-')]"))
            )

            # Fetch the OTP from email
            confirmation_email = wait_for_confirmation_email(service)
            if not confirmation_email:
                print(f"{Fore.RED}Failed to retrieve OTP email.")
                return False

            message_body = get_message_body(confirmation_email)
            otp_code_match = re.search(r"Your OTP code is: (\d{6})", message_body)
            if not otp_code_match:
                print(f"{Fore.RED}OTP not found in the email.")
                return False

            otp_code = otp_code_match.group(1)
            print(f"{Fore.GREEN}Retrieved OTP: {otp_code}")

            # Input the OTP into the fields
            for i, digit in enumerate(otp_code):
                otp_fields[i].send_keys(digit)

            # Submit the OTP
            continue_button2 = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Continue']"))
            )
            driver.execute_script("arguments[0].click();", continue_button2)

            # Verify if the OTP submission is successful
            result = monitor_url_change(driver, 
                                        target_success_url="https://undetectable.ai/pricing", 
                                        error_url="?error=Verification", 
                                        timeout=10)

            if result:
                print(f"{Fore.GREEN}OTP verification successful.")
                return True
            else:
                print(f"{Fore.RED}OTP verification failed.")
                return False
    except Exception as e:
        print(f"{Fore.RED}Error during OTP handling: {e}")
        return False

def initialize_driver(fake_user_agent):
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--log-level=3")
    options.add_argument('--no-proxy-server')
    options.add_argument(f"user-agent={fake_user_agent}")
    options.add_argument("--incognito")
    options.add_argument("--start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    return webdriver.Chrome(options=options)

def main(purpose_choice, readability_choice, article_file_path, base_email):
    driver = None
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

        # Initialize fake user agent generator
        ua = UserAgent()

        # Process each chunk
        while article_chunks:
            fake_user_agent = ua.random
            driver = initialize_driver(fake_user_agent)
            
            try:
                # Generate a Gmail variation and sign in
                email_variant = generate_gmail_variation(base_email)
                automate_sign_in(driver, email_variant)

                # Wait for confirmation email and process link
                creds = authenticate_gmail()
                service = get_gmail_service(creds)
                confirmation_email = wait_for_confirmation_email(service)
                
                if confirmation_email:
                    message_body = get_message_body(confirmation_email)
                    verify_link = extract_verify_link(message_body)
                    if verify_link:
                        success = process_confirmation_link(driver, verify_link, service, email_variant)
                        if not success:
                            print(f"{Fore.RED}Verification failed. Retrying with a new account.")
                            continue  # Retry with a new email
                    else:
                        print(f"{Fore.RED}Verify link not found in email.")
                        continue  # Retry with a new email
                else:
                    print(f"{Fore.RED}No confirmation email found.")
                    continue  # Retry with a new email

                # Submit the chunk for paraphrasing
                chunk = article_chunks.pop(0)
                driver.get('https://undetectable.ai/')

                try:
                    banner = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CLASS_NAME, 'iubenda-banner-content'))
                    )
                    if banner:
                        print(f"{Fore.YELLOW}Banner detected. Removing it.")
                        driver.execute_script("document.querySelector('.iubenda-banner-content').style.display = 'none';")
                except TimeoutException:
                    # Banner not present, continue normally
                    pass

                wait = WebDriverWait(driver, 10)
                purpose = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="scrollElement"]/div/div/div[1]/div/div[1]/div/div[1]/div[2]/select')))
                readability = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="scrollElement"]/div/div/div[1]/div/div[1]/div/div[1]/div[1]/select')))
                
                select1 = Select(purpose)
                select2 = Select(readability)

                if 1 <= purpose_choice <= len(select1.options) - 1:
                    select1.select_by_index(purpose_choice)

                if 1 <= readability_choice <= len(select2.options) - 1:
                    select2.select_by_index(readability_choice)

                textarea = driver.find_element(By.XPATH, '//*[@id="scrollElement"]/div/div/div[1]/div/div[2]/div/textarea')
                textarea.clear()
                textarea.send_keys(chunk)

                humanize = driver.find_element(By.ID, 'humanize-tooltip')
                driver.execute_script("arguments[0].click();", humanize)

                # Check if the popup for buying words appears
                try:
                    popup_present = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, "//button[@aria-label='View Paid Plans']"))
                    )
                    if popup_present:
                        print(f"{Fore.YELLOW}Not enough words left. Switching to a new email session.")
                        continue  # Retry with a new email
                except TimeoutException:
                    # Popup did not appear, proceed normally
                    pass

                paraphrased = WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="copy-output"]')))
                paraphrased.click()

                copied_content = pyperclip.paste()
                with open('paraphrased.txt', 'a') as new:
                    new.write(f'{copied_content}\n')

            except Exception as e:
                print(f"{Fore.RED}Error during chunk processing: {e}")
            finally:
                if driver:
                    driver.quit()

        print(f"{Fore.GREEN}\nArticle has been paraphrased successfully.")

    except Exception as e:
        print(f"{Fore.RED}Error during processing: {e}")

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
