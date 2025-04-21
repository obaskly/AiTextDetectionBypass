from nltk.tokenize import sent_tokenize
import re

def sanitize_text_for_chromedriver(text):
    """
    Remove characters outside the Basic Multilingual Plane (BMP) that ChromeDriver doesn't support.
    This includes emojis and certain rare characters.
    """
    # This regex pattern matches any character outside the BMP range (U+0000 to U+FFFF)
    return re.sub(r'[^\u0000-\uFFFF]', '', text)

def split_text_preserve_sentences(text, max_words):
    # Sanitize text first
    text = sanitize_text_for_chromedriver(text)
    
    sentences = sent_tokenize(text)
    chunks = []
    current_chunk = []
    current_word_count = 0

    for sentence in sentences:
        words_in_sentence = len(sentence.split())
        if current_word_count + words_in_sentence > max_words:
            chunks.append(' '.join(current_chunk))
            current_chunk = []
            current_word_count = 0
        current_chunk.append(sentence)
        current_word_count += words_in_sentence

    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks
