# 📝 Ai Text Detection Bypass Script

ParaGenie is a script that automates the process of paraphrasing articles using the undetectable.ai platform. It enables users to transform long-form content into unique paraphrased versions by splitting the input text into manageable chunks and processing each chunk individually. The script is designed with flexibility, automation, and user anonymity in mind, making it an efficient tool for paraphrasing lengthy documents.

## ✨ What's New?

You can Try the Other tool as well https://github.com/obaskly/AiDetectionBypass

## 🛑 Disclaimer

This script automates text paraphrasing but is **NOT responsible for the quality or accuracy of the output**. Please review and verify results independently.

## 🔥 Features

- Automated Paraphrasing: Automatically paraphrase long articles by breaking them into chunks.
- Multi-File Support: Hndles text extraction and processing for TXT, DOCX, and PDF file formats. (NEW!)
- Customizable Chunk Splitting: Choose between the default word-based splitting method or a more advanced NLTK-powered sentence-preserving approach. (NEW!)
- Gmail-Based Registration: Automates Gmail registration and verification for seamless paraphrasing. (NEW!)
- Purpose-Specific Writing: Supports a variety of writing purposes such as essays, articles, marketing material, and more.
- Readability Options: Tailor the readability level of the output, from high school to professional marketing standards.
- Tone selection: Support three different kinds of tones.
- Anonymity Features: Leverages Chrome's incognito mode and a random user agent to protect your identity.
- Error Handling and Recovery: Automatically retries chunks if any errors occur during the paraphrasing process.
- Output Management: Saves paraphrased content into a file for easy access and organization.

## Usage

1. Clone this repository to your local machine.

```bash
git clone https://github.com/obaskly/AiTextDetectionBypass.git
cd AiTextDetectionBypass
```

2. Install the required Python packages.

  ```bash
  pip install -r requirements.txt
  ```

3. GMAIL SETUP

- go to https://console.cloud.google.com
- create new project
- click on 'api and services'
- type "Gmail API" and select it from the results.
- Click the Enable button.
  
  ### Set Up OAuth Consent Screen
  
- In the left-hand menu, go to APIs & Services > OAuth consent screen.
- Choose External 
- Add the necessary scopes: https://www.googleapis.com/auth/gmail.readonly
- Go to the Test users section.
- Add the Gmail address you want to use for paraphrasing.
- Click Save and Continue.
  
  ### Create OAuth 2.0 Credentials
  
- Go to APIs & Services > Credentials.
- Click Create Credentials > OAuth 2.0 Client IDs.
- Choose Desktop App as the application type.
- Download the credentials.json file once it’s created and put it in the same directory as the script.

4. Run the script.

  ```bash
  python gui.py
  ```

Prepare your article in a text file (e.g., article.txt).
Select the writing purpose, readability level, and provide the path to your article.

If you don't want to use the GUI mode, open `paraphraser.py`, uncomment the last part, and run it.

The script will save the paraphrased content to paraphrased.txt.
Sit back and relax while the script paraphrases your article!

## Prerequisites

- Python 3.x
- Google Chrome installed (chromedriver is used by Selenium)
  
## Script in action

https://github.com/obaskly/AiTextDetectionBypass/assets/11092871/7fc4ccf0-d97f-43dd-a987-9b7e6812c174

