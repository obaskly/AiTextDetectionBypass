# 📝 Ai Text Detection Bypass Script

This script automates the process of paraphrasing articles using undetectable.ai website. It splits the input article into 250-word chunks and paraphrases each chunk. The paraphrased content is then saved to a file.

## Features

- Paraphrase long articles automatically.
- Split articles into manageable chunks.
- Save paraphrased content to a file.
- Uses Gmail for registration. (NEW !)
- Supports different writing purposes and readability levels.
- Utilizes Chrome's incognito mode for anonymity.

## Usage

1. Clone this repository to your local machine.

```bash
git clone https://github.com/obaskly/AiTextDetectionBypass.git
cd AiTextDetectionBypass
```

2. Install the required Python packages.

  ```bash
  pip install -r requirements.txt
  pip install --upgrade google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
  ```

Prepare your article in a text file (e.g., article.txt).

3. GMAIL SETUP

  . go to https://console.cloud.google.com
  
  . create new project
  
  . click on 'api and services'
  
  . type "Gmail API" and select it from the results.
  
  . Click the Enable button.
  
  ### Set Up OAuth Consent Screen
  
  . In the left-hand menu, go to APIs & Services > OAuth consent screen.
  
  . Choose External 
  
  . Add the necessary scopes: https://www.googleapis.com/auth/gmail.readonly
  
  . Go to the Test users section.
  
  . Add the Gmail address you want to use for paraphrasing.
  
  Click Save and Continue.
  
  ### Create OAuth 2.0 Credentials
  
  . Go to APIs & Services > Credentials.
  
  . Click Create Credentials > OAuth 2.0 Client IDs.
  
  . Choose Desktop App as the application type.
  
  . Download the credentials.json file once it’s created and put it in the same directory as the script.

4. Run the script.

  ```bash
  python gui.py
  ```

Select the writing purpose, readability level, and provide the path to your article.

If you don't want to use the GUI mode, go to paraphraser.py and uncomment the last part and run it.

The script will create an accounts.txt file with temporary email accounts and save the paraphrased content to paraphrased.txt.
Sit back and relax while the script paraphrases your article!

## Prerequisites

- Python 3.x
- Google Chrome installed (chromedriver is used by Selenium)
  
## Script in action

https://github.com/obaskly/AiTextDetectionBypass/assets/11092871/7fc4ccf0-d97f-43dd-a987-9b7e6812c174

