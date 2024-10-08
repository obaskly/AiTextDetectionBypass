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
cd AiTextDetectionBypass
```

2. Install the required Python packages.

  ```bash
  pip install -r requirements.txt
  ```

Prepare your article in a text file (e.g., article.txt).

3. Run the script.

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

