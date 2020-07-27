import json
from typing import Optional, List

import aiohttp
import anyio
import pymorphy2
from aiohttp import web

from main import process_article
from text_tools import get_charged_words
from settings import BASE_DIR


def split_urls(urls: Optional[str]) -> List[str]:
    """Splits comma-separated args into a list. Removes duplicates."""
    if not urls:
        return []
    return list({item for item in urls.split(',')})


async def index(request: web.Request) -> web.Response:
    urls = request.query.get('urls')
    urls = split_urls(urls)
    if len(urls) > 10:
        raise web.HTTPBadRequest(
            text=json.dumps({'error': 'too many urls in request, should be 10 or less'}),
            content_type='application/json'
        )
    results = []
    async with anyio.create_task_group() as tg:
        for url in urls:
            await tg.spawn(
                process_article,
                request.app['aiohttp_session'],
                request.app['morpher'],
                request.app['charged_words'],
                url,
                results,
            )
    return web.json_response(results)

async def create_aiohttp_session(app: web.Application) -> None:
    """
    Reusable aiohttp client session.

    Because docs suggested to reuse it as much as possible.
    Don’t create a session per request.
    Most likely you need a session per application which performs all requests altogether.
    """
    async with aiohttp.ClientSession() as session:
        app['aiohttp_session'] = session
        yield

async def create_morpher(app: web.Application) -> None:
    """MorphAnalyzer instance is 10-15 Mb of RAM. Need to share it."""
    app['morpher'] = pymorphy2.MorphAnalyzer()

async def load_charged_words(app: web.Application) -> None:
    app['charged_words'] = get_charged_words(BASE_DIR.joinpath('charged_dict'))

def configure_server() -> web.Application:
    app = web.Application()
    app.on_startup.append(create_morpher)
    app.on_startup.append(load_charged_words)
    app.cleanup_ctx.append(create_aiohttp_session)
    app.add_routes([
        web.get('/', index, name='index'),
    ])
    return app


if __name__ == '__main__':
    app = configure_server()
    web.run_app(app)
