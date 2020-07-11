import pytest

from bot.adapter import MarkovifyAdapter
from bot.adapter import from_newline_text, from_json


def test_from_json_chain(bot):
    json_str = bot.model.to_json()

    new_bot = from_json(json_str=json_str)

    assert isinstance(new_bot, MarkovifyAdapter)
    assert new_bot.model
    assert new_bot.model.chain
    assert bot.model.to_dict() == new_bot.model.to_dict()


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
