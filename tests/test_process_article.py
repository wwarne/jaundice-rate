import asyncio

import aiohttp
import pytest

from statuses import ProcessingStatus
from utils import process_article

"""
NOTE
Python 3.8 supports AsyncMock but I want this to run on Python 3.7
So plan is simple - I will mock a function and place some async function
to a resulted mock's `side_effect`

Example:
mocked_f = mocker.patch('my_project.utils.fetch')
mocked_f.size_effect = my_custom_async_func

When the code I test calls `fetch` it would call its `side_effect` (default Mock behavior)
So in tested code -> await fetch(url, other_param) # this fetch is a mock
becomes
->  await mocked_f.side_effect(url, other_param)
-> my_custom_async_func do the thing I want (raises exception, emulate long-running func, etc...)
"""


async def fetch_has_broken_connection(*args, **kwargs):
    raise aiohttp.ClientError()


async def fetch_has_timeout(*args, **kwargs):
    raise asyncio.TimeoutError()


async def emulate_long_running_task(*args, **kwargs):
    await asyncio.sleep(10)


async def fetch_return_bad_html(*args, **kwargs):
    return '<html></html>'


async def fetch_return_inosmi_html(*args, **kwargs):
    return '<article class="article"><h1>hello</h1> <p>бодрость</p> <p>выходные</p></article>'


@pytest.mark.asyncio
class TestProcessArticle:
    async def test_request_timeout(self, mocked_fetch):
        """request timeout - server didn't respond for a specified time."""
        mocked_fetch.side_effect = emulate_long_running_task
        results = []
        await process_article(
            session=None,
            morph=None,
            charged_words=[],
            url='http://localhost',
            results=results,
            request_timeout=0.1,
        )
        assert mocked_fetch.called is True
        assert len(results) == 1
        assert results[0]['status'] == ProcessingStatus.TIMEOUT.value

    async def test_process_timeout(self, mocked_fetch, mocker):
        """process timeout - we can't process article text for a specified time."""
        mocked_fetch.side_effect = fetch_return_inosmi_html
        mocked_split = mocker.patch('utils.split_by_words')
        mocked_split.side_effect = emulate_long_running_task

        results = []
        await process_article(
            session=None,
            morph=None,
            charged_words=[],
            url='http://localhost',
            results=results,
            process_timeout=0.1,
        )
        assert mocked_split.called is True
        assert results[0]['status'] == ProcessingStatus.TIMEOUT.value

    async def test_connection_problem(self, mocked_fetch):
        """If we have problems with the network aiohttp raises ClientError-type exceptions."""
        mocked_fetch.side_effect = fetch_has_broken_connection
        results = []
        await process_article(
            session=None,
            morph=None,
            charged_words=[],
            url='http://localhost',
            results=results,
        )
        assert mocked_fetch.called is True
        assert results[0]['status'] == ProcessingStatus.FETCH_ERROR.value

    async def test_not_inosmi_html(self, mocked_fetch):
        mocked_fetch.side_effect = fetch_return_bad_html
        results = []
        await process_article(
            session=None,
            morph=None,
            charged_words=[],
            url='http://localhost',
            results=results,
        )
        assert mocked_fetch.called is True
        assert results[0]['status'] == ProcessingStatus.PARSING_ERROR.value

    async def test_everything_ok(self, mocked_fetch, morpher):
        mocked_fetch.side_effect = fetch_return_inosmi_html
        results = []
        await process_article(
            session=None,
            morph=morpher,
            charged_words=['бодрость'],
            url='http://localhost',
            results=results,
        )
        assert mocked_fetch.called is True
        assert results[0]['status'] == ProcessingStatus.OK.value
        assert results[0]['word_count'] == 3
        assert str(results[0]['score']) == '33.33'
