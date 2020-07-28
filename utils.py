import asyncio
import time
from contextlib import contextmanager
from typing import Generator, List, Dict, Union, Optional

import aiohttp
import async_timeout
import pymorphy2

from aiocache.base import BaseCache
from adapters import ArticleNotFound, SANITIZERS
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
                          cache: Optional[BaseCache] = None,
                          ) -> None:
    if cache:
        cached_result = await get_from_cache(cache, url)
        if cached_result:
            results.append(cached_result)
            return

    result = {
        'status': None,
        'url': url,
        'score': None,
        'word_count': None,
    }
    try:
        async with async_timeout.timeout(request_timeout):
            html = await fetch(session, url)
        article_text = SANITIZERS['inosmi_ru'](html, plaintext=True)
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
        if cache:
            await set_to_cache(cache, url, result)
    results.append(result)


async def get_from_cache(cache: BaseCache, key: str) -> Optional[Dict]:
    """Loads result from cache and ignore errors."""
    try:
        return await cache.get(key)
    except Exception:
        return None

async def set_to_cache(cache: BaseCache, key: str, value: Dict) -> None:
    """Save result to cache and ignore errors."""
    try:
        await cache.set(key, value, ttl=60 * 60)  # cache successful items for an hour
    except Exception:
        pass
