import pytest
from server import configure_server
from statuses import ProcessingStatus

async def fetch_good_html(*args, **kwargs):
    return '<article class="article"><h1>hello</h1> <p>бодрость</p> <p>выходные</p></article>'

@pytest.fixture()
def cli(aiohttp_client, loop):
    app = configure_server()
    return loop.run_until_complete(aiohttp_client(app))


async def test_no_urls(cli):
    response = await cli.get('/')
    assert response.status == 200
    t = await response.json()
    assert t == []


async def test_more_than_10_urls(cli):
    urls = [f'http://example/{i}' for i in range(11)]
    urls = ','.join(urls)
    query = f'/?urls={urls}'
    response = await cli.get(query)
    assert response.status == 400
    r_json = await response.json()
    assert r_json['error']


async def test_success(cli, mocker):
    mocked_f = mocker.patch('main.fetch')
    mocked_f.side_effect = fetch_good_html
    response = await cli.get('/?urls=http://example/')
    assert response.status == 200
    r_json = await response.json()
    r_json = r_json[0]
    assert r_json['status'] == ProcessingStatus.OK.value
    assert r_json['url'] == 'http://example/'
    assert str(r_json['score']) == '33.33'
    assert r_json['word_count'] == 3
