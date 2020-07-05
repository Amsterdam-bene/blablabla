import pytest
from bot.adapter import MarkovifyAdapter


def test_invalid_init(corpus):
    with pytest.raises(KeyError):
        bot = MarkovifyAdapter(text="")


def test_invalid_init(corpus):
    with pytest.raises(KeyError):
        bot = MarkovifyAdapter(text=corpus, language=None)


def test_markovify_adapter(corpus):
    bot = MarkovifyAdapter(text=corpus)

    assert bot.sample("") == MarkovifyAdapter.DEFAULT_RESPONSE
