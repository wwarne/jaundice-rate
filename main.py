import asyncio
import logging
import time
from contextlib import contextmanager
from typing import Generator, List, Dict, Union

import aiohttp
import async_timeout
import pymorphy2

from adapters.inosmi_ru import sanitize, ArticleNotFound
from settings import logger
from statuses import ProcessingStatus
from text_tools import split_by_words, calculate_jaundice_rate


@contextmanager
def measure_time() -> Generator[None, None, None]:
    start = time.monotonic()
    yield
    elapsed = round(time.monotonic() - start, 2)
    logger.info(f'Анализ закончен за: {elapsed} сек')


async def fetch(session: aiohttp.ClientSession, url: str) -> str:
    async with session.get(url) as response:
        response.raise_for_status()
        return await response.text()


async def process_article(session: aiohttp.ClientSession,
                          morph: pymorphy2.MorphAnalyzer,
                          charged_words: List[str],
                          url: str,
                          results: List[Dict[str, Union[str, int, float, None]]],
                          request_timeout: Union[float, int] = 2,
                          process_timeout: Union[float, int] = 3,
                          ) -> None:
    result = {
        'status': None,
        'url': url,
        'score': None,
        'word_count': None,
    }
    try:
        async with async_timeout.timeout(request_timeout):
            html = await fetch(session, url)
        article_text = sanitize(html, plaintext=True)
        with measure_time():
            async with async_timeout.timeout(process_timeout):
                just_words = await split_by_words(morph, article_text)
    except aiohttp.ClientError:
        result['status'] = ProcessingStatus.FETCH_ERROR.value
    except asyncio.TimeoutError:
        result['status'] = ProcessingStatus.TIMEOUT.value
    except ArticleNotFound:
        result['status'] = ProcessingStatus.PARSING_ERROR.value
    else:
        result['status'] = ProcessingStatus.OK.value
        result['score'] = calculate_jaundice_rate(just_words, charged_words)
        result['word_count'] = len(just_words)
    results.append(result)
