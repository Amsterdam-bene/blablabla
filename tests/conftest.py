import pytest


@pytest.fixture(scope="session")
def corpus():
    return [
        "Antani, come fosse antani, la supercazzola con scappellamento.",
        "Come?",
        "A destra, per due",
    ]
