import json
import os
from utils.email_utils import authenticate_gmail, get_gmail_service, extract_verify_link, get_message_body
from utils.automation_utils import initialize_driver, automate_sign_in, process_confirmation_link, wait_for_confirmation_email
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent

ua = UserAgent()
fake_user_agent = ua.random

def load_existing_apis(output_file):
    #Load existing APIs from the JSON file, if it exists.
    if os.path.exists(output_file):
        with open(output_file, 'r') as f:
            return json.load(f)
    return {}

def get_new_emails(existing_apis, email_variations):
    #Get emails that have not been processed yet
    if not existing_apis:
        return email_variations  # Process all emails if no existing APIs

    last_processed_email = list(existing_apis.keys())[-1]
    if last_processed_email not in email_variations:
        return email_variations  # Process all if last processed email not in the variations

    # Find the position of the last processed email and return emails after it
    start_index = email_variations.index(last_processed_email) + 1
    return email_variations[start_index:]

def main(update_current_email=None, update_result=None):
    variations_file_path = os.path.join('json_files', 'generated_variations.json')
    output_file_path = os.path.join('json_files', 'apis.json')

    # Check if the JSON file with email variations exists
    if not os.path.exists(variations_file_path):
        error_message = f"{variations_file_path} does not exist. Please provide the file with email variations."
        print(error_message)
        return error_message  # Return the error message to the caller

    # Load email variations
    with open(variations_file_path, 'r') as f:
        email_variations = json.load(f)

    # Load existing APIs and determine new emails to process
    existing_apis = load_existing_apis(output_file_path)
    new_emails = get_new_emails(existing_apis, email_variations)

    if not new_emails:
        print("No new emails to process. Exiting.")
        return "No new emails to process."

    # Open the output file in append mode
    with open(output_file_path, 'w') as f:
        f.write(json.dumps(existing_apis, indent=4))

    # Process new emails
    apis = existing_apis.copy()
    for email in new_emails:
        if update_current_email:
            update_current_email(email)  # Emit current email being processed

        api_key = None  # Initialize API key as None
        try:
            print(f"Processing email: {email}")
            driver = initialize_driver(fake_user_agent)

            retry_attempts = 3  # Maximum retry attempts
            for attempt in range(retry_attempts):
                try:
                    # Sign in
                    automate_sign_in(driver, email, email)

                    # Wait for confirmation email and process link
                    creds = authenticate_gmail()
                    service = get_gmail_service(creds)
                    confirmation_email = wait_for_confirmation_email(service)

                    if confirmation_email:
                        message_body = get_message_body(confirmation_email)
                        verify_link = extract_verify_link(message_body)
                        if verify_link:
                            success = process_confirmation_link(driver, verify_link, service, email)
                            if success:
                                break  # Exit retry loop if successful
                            else:
                                print(f"Verification failed for {email}. Retrying.")
                        else:
                            print(f"Verify link not found in email for {email}. Retrying.")
                    else:
                        print(f"No confirmation email found for {email}. Retrying.")

                except Exception as e:
                    print(f"Error during processing email {email}: {e}")
                finally:
                    if attempt == retry_attempts - 1:
                        print(f"Maximum retry attempts reached for {email}. Skipping.")
                        break

            # Navigate to the API page and extract API key
            driver.get('https://undetectable.ai/develop')

            wait = WebDriverWait(driver, 10)
            api_element = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="apiKey"]')))
            api_key = api_element.get_attribute('value')
            print(f'API key for {email}: {api_key}')
            apis[email] = api_key

        except Exception as e:
            print(f"Error during getting API for {email}: {e}")
        finally:
            driver.quit()

        # Notify final result
        if update_result:
            if api_key:
                update_result(f"{email}: {api_key}")  # Notify about the grabbed API key
            else:
                update_result(f"{email}: Failed to grab API")

        # Append the current progress to the file
        with open(output_file_path, 'w') as f:
            json.dump(apis, f, indent=4)

    return "APIs grabbed successfully."

def grab_apis(progress_callback=None):
    try:
        print("Starting API grabber...")
        grabbed_apis = {}
        
        def update_progress(email, api_key=None):
            if api_key:
                grabbed_apis[email] = api_key  # Store API key
            if progress_callback:
                progress_callback(email, api_key)  # Notify GUI
        
        result = main(update_progress)  # Pass the callback to main
        if result == "No new emails to process.":
            print(result)
            return {"success": False, "message": "No new emails to process."}  # No new emails
        elif result == "APIs grabbed successfully.":
            print(result)
            return {"success": True, "message": grabbed_apis}  # APIs grabbed
        else:
            print(f"Unexpected result: {result}")
            return {"success": False, "message": "Unexpected result from grab_apis."}
    except Exception as e:
        error_message = str(e)
        print(f"Error occurred in API grabbing: {error_message}")
        return {"success": False, "message": error_message}
