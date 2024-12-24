import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException
from colorama import Fore
from utils.email_utils import calculate_email_variations, get_message_body, search_for_confirmation_email

def automate_sign_in(driver, temp_email, base_email):
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
        print(f"{Fore.GREEN}Total variations for {base_email}: {calculate_email_variations(base_email)}")

    except Exception as e:
        print(f"Error during sign-in process: {e}")

def wait_for_confirmation_email(service, max_wait_time=300, poll_interval=10):
    time.sleep(7)
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
                try:
                    driver.execute_script("arguments[0].focus();", otp_fields[i])
                    
                    # Clear any pre-existing input (just in case)
                    otp_fields[i].clear()

                    # Send the digit
                    otp_fields[i].send_keys(digit)
                    
                    # Add a small delay between inputs to prevent race conditions
                    time.sleep(0.2)
                except Exception as e:
                    print(f"{Fore.RED}Error inputting OTP at position {i}: {e}")

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
