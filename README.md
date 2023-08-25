# 📝 Ai Text Detection Bypass Script

This script automates the process of paraphrasing articles using undetectable.ai website. It splits the input article into 250-word chunks and paraphrases each chunk. The paraphrased content is then saved to a file.

## Features

- Paraphrase long articles automatically.
- Split articles into manageable chunks.
- Save paraphrased content to a file.
- Uses a temporary email for registration.
- Supports different writing purposes and readability levels.
- Utilizes Chrome's incognito mode for anonymity.

## Usage

1. Clone this repository to your local machine.

```bash
git clone https://github.com/obaskly/AiTextDetectionBypass.git
```

2. Install the required Python packages.

  ```bash
  pip install -r requirements.txt
  ```

Prepare your article in a text file (e.g., article.txt).

3. Run the script.

  ```bash
  python paraphraser.py
  ```

Follow the on-screen prompts to select the writing purpose, readability level, and provide the path to your article.

The script will create an accounts.txt file with temporary email accounts and save the paraphrased content to paraphrased.txt.
Sit back and relax while the script paraphrases your article!

## Prerequisites

- Python 3.x
- Google Chrome installed (chromedriver is used by Selenium)
