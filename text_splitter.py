from nltk import download
from nltk.tokenize import sent_tokenize

# Download required resources for nltk
download("punkt")

def split_text_preserve_sentences(text, max_words):
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
