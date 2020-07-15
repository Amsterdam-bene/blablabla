import datetime
import json
import logging
import logging.config
from typing import Dict

import falcon
import toml

from bot.adapter import MarkovifyAdapter
from bot.adapter import from_newline_text, from_object, from_json

PREFIX = "/bot"
QUERY_ENDPOINT = f"{PREFIX}/query"
HEALTH_ENDPOINT = f"{PREFIX}/health"

loaders = {"json": from_json, "pickle": from_object, "text": from_newline_text}

logging.config.fileConfig("logging.conf")


class BotResource:
    def __init__(self, bots: Dict[str, MarkovifyAdapter] = None):
        self.logger = logging.getLogger("bot")
        self.bots = bots

    def on_post(self, req, resp, **kwargs):
        try:
            body = req.media
            required_fields = ("text", "channel")
            for field in required_fields:
                if field not in body:
                    raise ValueError(f'"{field} field missing from POST body')

            channel = body["channel"]
            if channel not in self.bots:
                raise falcon.HTTPForbidden(f"No resource for channel {channel}")

            bot = self.bots[channel]["bot"]
            sentence = bot.sample(body["text"])

            resp.body = json.dumps({"reply": sentence})
        except falcon.HTTPForbidden as e:
            self.logger.error(str(e))
            raise e
        except Exception as e:
            self.logger.error(str(e))
            raise falcon.HTTPBadRequest("Invalid data", str(e))
        else:
            if self.bots[channel]["log_query"]:
                self.logger.info(
                    {
                        "timestamp": datetime.datetime.now(),
                        "channel": channel,
                        "input": body["text"],
                        "message": sentence,
                    }
                )

    def on_get_health(self, req, resp):
        resp.body = json.dumps(
            {
                "status": "OK",
                "bots": {
                    channel: self.bots[channel]["bot"].status() for channel in self.bots
                },
            }
        )


def create(bots=None):
    api = falcon.API()
    resource = BotResource(bots)

    api.add_route(QUERY_ENDPOINT, resource)
    api.add_route(HEALTH_ENDPOINT, resource, suffix="health")
    return api


def from_config(path: str):
    logger = logging.getLogger()
    conf = toml.load(path)

    if not conf["bots"]:
        raise ValueError("No bots configured. Aborting.")

    bots = {}
    for bot in conf["bots"]:
        try:
            channel = bot["channel"]
            format = bot["format"]
            path = bot["path"]
            language = bot.get("language", None)
            stopwords = bot.get("stopwords", None)
            log_query = bot.get("log_query", False)

            if channel in bot:
                raise ValueError(
                    f"A bot has already been instantiated for {channel}. Skipping {path}."
                )
            if format not in loaders:
                raise ValueError(f"Format {format} is not supported")

            mode = "r"
            if format == "pickle":
                mode += "b"

            with open(path, mode) as fh:
                model_input = fh.read()

            loader = loaders[format]
            bot = loader(model_input, language=language, stopwords=stopwords)
            bots[channel] = {"bot": bot, "log_query": log_query}
        except Exception as e:
            logger.error("Failed to load bot. ", str(e))

    return create(bots)
