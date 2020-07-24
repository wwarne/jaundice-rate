from typing import Sequence

from bs4.element import Tag

DEFAULT_BLACKLIST_TAGS = (
    'script',
    'time'
)

DEFAULT_UNWRAPLIST_TAGS = (
    'div',
    'p',
    'span',
    'address',
    'article',
    'header',
    'footer'
)


def remove_buzz_attrs(soup: Tag) -> Tag:
    """Remove all attributes except some special tags."""
    for tag in soup.find_all(True):
        if tag.name == 'a':
            tag.attrs = {
                'href': tag.attrs.get('href'),
            }
        elif tag.name == 'img':
            tag.attrs = {
                'src': tag.attrs.get('src'),
            }
        else:
            tag.attrs = {}

    return soup


def remove_buzz_tags(soup: Tag,
                     blacklist: Sequence[str] = DEFAULT_BLACKLIST_TAGS,
                     unwraplist: Sequence[str] = DEFAULT_UNWRAPLIST_TAGS
                     ) -> None:
    """Remove most of tags, leaves only tags significant for text analysis."""
    for tag in soup.find_all(True):
        if tag.name in blacklist:
            tag.decompose()
        elif tag.name in unwraplist:
            tag.unwrap()


def remove_all_tags(soup: Tag) -> None:
    """Unwrap all tags."""
    for tag in soup.find_all(True):
        tag.unwrap()
