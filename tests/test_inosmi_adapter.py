import pytest

from adapters.inosmi_ru import sanitize, ArticleNotFound


def test_sanitize(inosmi_good_html):
    clean_text = sanitize(inosmi_good_html)
    assert clean_text.startswith('<article>')
    assert clean_text.endswith('</article>')
    assert 'В субботу, 29 июня, президент США Дональд Трамп' in clean_text
    assert 'За несколько часов до встречи с Си' in clean_text

    assert '<img src="' in clean_text
    assert '<a href="' in clean_text
    assert '<h1>' in clean_text


def test_sanitize_plain_text(inosmi_good_html):
    clean_plaintext = sanitize(inosmi_good_html, plaintext=True)
    assert 'В субботу, 29 июня, президент США Дональд Трамп' in clean_plaintext
    assert 'За несколько часов до встречи с Си' in clean_plaintext

    assert '<img src="' not in clean_plaintext
    assert '<a href="' not in clean_plaintext
    assert '<h1>' not in clean_plaintext
    assert '</article>' not in clean_plaintext
    assert '<h1>' not in clean_plaintext


def test_sanitize_wrong_url(inosmi_bad_html):
    with pytest.raises(ArticleNotFound):
        sanitize(inosmi_bad_html)
