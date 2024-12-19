
import random
import pyperclip
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from fake_useragent import UserAgent
from colorama import Fore

from email_utils import authenticate_gmail, generate_gmail_variation, get_gmail_service, extract_verify_link, get_message_body
from automation_utils import initialize_driver, automate_sign_in, process_confirmation_link, wait_for_confirmation_email

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
                automate_sign_in(driver, email_variant, base_email)

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

                # Retry current chunk until successfully paraphrased
                while True:
                    try:
                        chunk = article_chunks[0]  # Keep the current chunk until success
                        driver.get('https://undetectable.ai/')

                        # Remove the banner if it exists
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

                        purpose_select = Select(purpose)
                        readability_select = Select(readability)

                        purpose_select.select_by_index(purpose_choice - 1)
                        readability_select.select_by_index(readability_choice - 1)

                        textarea = driver.find_element(By.XPATH, '//*[@id="scrollElement"]/div/div/div[1]/div/div[2]/div/textarea')
                        textarea.clear()
                        textarea.send_keys(chunk)

                        humanize = driver.find_element(By.ID, 'humanize-tooltip')
                        driver.execute_script("arguments[0].click();", humanize)

                        # Check for the "not enough words" popup
                        try:
                            popup_present = WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located((By.XPATH, "//button[@aria-label='View Paid Plans']"))
                            )
                            if popup_present:
                                print(f"{Fore.YELLOW}Not enough words left. Switching to a new email session.")
                                raise Exception("Switch to new email session")
                        except TimeoutException:
                            # Popup did not appear, proceed normally
                            pass

                        # Successfully paraphrased the chunk
                        paraphrased = WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="copy-output"]')))
                        paraphrased.click()

                        copied_content = pyperclip.paste()
                        with open('paraphrased.txt', 'a') as new:
                            new.write(f'{copied_content}\n')

                        # Remove the successfully paraphrased chunk
                        article_chunks.pop(0)
                        print(f"{Fore.GREEN}Successfully paraphrased chunk. Moving to the next one.")
                        break  # Exit the loop to process the next chunk

                    except Exception as e:
                        print(f"{Fore.RED}Error paraphrasing chunk: {e}. Retrying with a new email.")
                        break  # Exit the loop to start a new email session

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
