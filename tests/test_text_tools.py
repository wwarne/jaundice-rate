import pytest

from text_tools import calculate_jaundice_rate, split_by_words


@pytest.mark.parametrize('source,result', [
    ('Во-первых, он хочет, чтобы', ['во-первых', 'хотеть', 'чтобы']),
    ('«Удивительно, но это стало началом!»', ['удивительно', 'это', 'стать', 'начало']),
])
@pytest.mark.asyncio
async def test_split_by_words(morpher, source, result):
    assert await split_by_words(morpher, source) == result


def test_calculate_jaundice_rate():
    assert -0.01 < calculate_jaundice_rate([], []) < 0.01
    assert 33.0 < calculate_jaundice_rate(['все', 'аутсайдер', 'побег'], ['аутсайдер', 'банкротство']) < 34.0
