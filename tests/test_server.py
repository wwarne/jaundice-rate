import pytest
from server import configure_server
from statuses import ProcessingStatus
from tests.test_process_article import fetch_return_inosmi_html, fetch_return_bad_html



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


async def test_same_urls_processed_as_one(cli, mocked_fetch):
    mocked_fetch.side_effect = fetch_return_bad_html
    response = await cli.get('/?urls=http://example,http://example,http://example')
    assert response.status == 200
    r_json = await response.json()
    assert len(r_json) == 1
    main_result = r_json[0]
    assert main_result['url'] == 'http://example'


async def test_success(cli, mocked_fetch):
    mocked_fetch.side_effect = fetch_return_inosmi_html
    response = await cli.get('/?urls=http://example/')
    assert response.status == 200
    r_json = await response.json()
    main_result = r_json[0]
    assert main_result['status'] == ProcessingStatus.OK.value
    assert main_result['url'] == 'http://example/'
    assert str(main_result['score']) == '33.33'
    assert main_result['word_count'] == 3


async def test_few_urls(cli, mocked_fetch):
    mocked_fetch.side_effect = fetch_return_inosmi_html
    response = await cli.get('/?urls=http://example/,http://another-url')
    assert response.status == 200
    r_json = await response.json()
    assert sorted([item['url'] for item in r_json]) == sorted(['http://example/', 'http://another-url'])
