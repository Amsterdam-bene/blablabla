import pytest
from falcon import testing

import api
from bot.adapter import from_newline_text


@pytest.fixture(scope="session")
def corpus():
    return [
        "Antani, come fosse antani, la supercazzola con scappellamento.",
        "Come?",
        "A destra, per due",
    ]


@pytest.fixture(scope="session")
def bot(corpus):
    return from_newline_text(text=corpus)


@pytest.fixture(scope="session")
def client(bot):
    bots = {
        "##horsing-around": {"bot": bot, "log_query": False, "model_path": ":memory"}
    }
    return testing.TestClient(api.create(bots))


@pytest.fixture
def body():
    return {
        "_meta": {"api_version": 1},
        "text": "hello bot, say something",
        "nick": "Rocco",
        "sender": "Rocco!~rtanica@unaffiliated/rocco",
        "my_own_nick": "DeBot",
        "channel": "##horsing-around",
    }
