import pathlib

import pymorphy2
import pytest

TEST_BASE_DIR = pathlib.Path(__file__).parent


@pytest.fixture(scope="session")
def morpher():
    """
    MorphAnalyzer instance takes 10-15 Mb of RAM.

    So it's good to not create it in every test.
    """
    return pymorphy2.MorphAnalyzer()


@pytest.fixture()
def inosmi_good_html():
    good_article = TEST_BASE_DIR.joinpath('html_examples/inosmi_good_example.html')
    return good_article.read_text()


@pytest.fixture()
def inosmi_bad_html():
    good_article = TEST_BASE_DIR.joinpath('html_examples/inosmi_bad_example.html')
    return good_article.read_text()


@pytest.fixture()
def mocked_fetch(mocker):
    return mocker.patch('utils.fetch')


def pytest_make_parametrize_id(config, val):
    """
    By default for every parametrized option pytest calls _ascii_escaped(val)
    and russian test_id's text is like \u0412\u043e-... in the console output. This fixes it.
    """
    return repr(val)
