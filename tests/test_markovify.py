import pytest
from bot.adapter import MarkovifyAdapter
from bot.adapter import from_newline_text


def test_invalid_init(corpus):
    with pytest.raises(KeyError):
        from_newline_text("")

    with pytest.raises(KeyError):
        from_newline_text(corpus, language=None)

    with pytest.raises(KeyError):
        from_newline_text(corpus, language="unknown language")


def test_markovify_adapter(corpus):
    bot = from_newline_text(corpus)

    assert bot.sample("") == MarkovifyAdapter.DEFAULT_RESPONSE
