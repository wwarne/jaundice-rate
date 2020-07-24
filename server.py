from aiohttp import web

async def index(request: web.Request) -> web.Response:
    return web.json_response([])

def configure_server() -> web.Application:
    app = web.Application()
    app.add_routes([
        web.get('/', index, name='index'),
    ])
    return app
