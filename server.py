import json
from typing import Optional, List

from aiohttp import web

from statuses import ProcessingStatus


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
    if urls:
        response = {
            'status': ProcessingStatus.OK.value,
            'url': 'http://example/',
            'score': 33.33,
            'word_count': 3,
        }
        results.append(response)
    return web.json_response(results)

def configure_server() -> web.Application:
    app = web.Application()
    app.add_routes([
        web.get('/', index, name='index'),
    ])
    return app
