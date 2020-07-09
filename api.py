import json
import logging

import pickle
import falcon

from bot.adapter import MarkovifyAdapter
from bot.adapter import from_newline_text, from_object

PREFIX = "/bot"
QUERY_ENDPOINT = f"{PREFIX}/query"
HEALTH_ENDPOINT = f"{PREFIX}/health"


class BotResource:
    def __init__(self, bot: MarkovifyAdapter = None):
        self.logger = logging.getLogger(__name__)
        self.bot = bot

    def on_post(self, req, resp, **kwargs):
        try:
            body = req.media
            if "text" not in body:
                raise ValueError(f'"text" field missing from POST body')
            sentence = self.bot.sample(body["text"])
            resp.body = json.dumps({"reply": sentence})
        except Exception as e:
            self.logger.error(str(e))
            raise falcon.HTTPBadRequest("Invalid data", str(e))

    def on_get_health(self, req, resp):
        resp.body = json.dumps({"status": "OK", "bot": self.bot.status()})


def create(bot=None):
    api = falcon.API()
    resource = BotResource(bot)

    api.add_route(QUERY_ENDPOINT, resource)
    api.add_route(HEALTH_ENDPOINT, resource, suffix="health")
    return api


def from_corpus(path: str):
    with open(path) as f:
        text = f.read()

    bot = from_newline_text(text=text)
    return create(bot=bot)


def from_pickle(path: str):
    with open(path, 'rb') as infile:
        model = pickle.load(infile)
    bot = from_object(model)
    return create(bot=bot)