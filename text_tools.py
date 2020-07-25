import asyncio
import string
from pathlib import Path
from typing import List

import pymorphy2


def _clean_word(word):
    word = word.replace('«', '').replace('»', '').replace('…', '')
    # FIXME какие еще знаки пунктуации часто встречаются ?
    word = word.strip(string.punctuation)
    return word


async def split_by_words(morph: pymorphy2.MorphAnalyzer, text: str) -> List[str]:
    """Учитывает знаки пунктуации, регистр и словоформы, выкидывает предлоги."""
    words = []
    for word in text.split():
        cleaned_word = _clean_word(word)
        normalized_word = morph.parse(cleaned_word)[0].normal_form
        if len(normalized_word) > 2 or normalized_word == 'не':
            words.append(normalized_word)
        await asyncio.sleep(0)  # release control to not to block event loop entirely
    return words


def calculate_jaundice_rate(article_words, charged_words):
    """Расчитывает желтушность текста, принимает список "заряженных" слов и ищет их внутри article_words."""

    if not article_words:
        return 0.0

    found_charged_words = [word for word in article_words if word in set(charged_words)]

    score = len(found_charged_words) / len(article_words) * 100

    return round(score, 2)


def load_from_file(filepath: Path) -> List[str]:
    """Load file into a list. Every line - new element."""
    with filepath.open(mode='r', encoding='utf-8') as f:
        return [word.strip() for word in f]


def get_charged_words(dict_path: str) -> List[str]:
    """Loads dictionaries of `charged` words into a memory."""
    dict_path = Path(dict_path)
    positive_file = dict_path.joinpath('positive_words.txt')
    negative_file = dict_path.joinpath('negative_words.txt')
    total_words = []
    total_words.extend(load_from_file(positive_file))
    total_words.extend(load_from_file(negative_file))
    return total_words
