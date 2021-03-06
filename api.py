import datetime
import json
import logging
import logging.config
import os
import re
from typing import Dict, Union

import falcon
import toml

from bot.adapter import MarkovifyAdapter
from bot.adapter import from_newline_text, from_object, from_json

LOGGING_CONF = os.environ.get("BLABLABLA_LOGGING_CONF", "logging.conf")

PREFIX = "/bot"
QUERY_ENDPOINT = f"{PREFIX}/query"
HEALTH_ENDPOINT = f"{PREFIX}/health"

loaders = {"json": from_json, "pickle": from_object, "text": from_newline_text}

logging.config.fileConfig(LOGGING_CONF)


class BotResource:
    def __init__(self, bots: Dict[str, Dict[str, Union[str, MarkovifyAdapter]]] = None):
        self.logger = logging.getLogger("bot")
        self.bots = bots

    @classmethod
    def sanitize_response_privmsg(cls, sentence):
        # Do not reply with a privmsg
        message_pat = re.compile("^(?P<privmsg>.*?:)?\s(?P<message>.*)$", re.IGNORECASE)
        match = re.match(message_pat, sentence)

        if match:
            sentence = match["message"]
        return sentence

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
            sentence = bot.sample(
                body["text"], sanitizers=(self.sanitize_response_privmsg,)
            )

            resp.body = json.dumps({"reply": sentence})
        except falcon.HTTPForbidden as e:
            self.logger.error(str(e), exc_info=True)
            raise e
        except Exception as e:
            self.logger.error(str(e), exc_info=True)
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
                    channel: {
                        "model": self.bots[channel]["bot"].status(),
                        "model_path": self.bots[channel]["model_path"],
                    }
                    for channel in self.bots
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
            channels = bot["channel"]
            model_format = bot["format"]
            path = bot["path"]
            language = bot.get("language", None)
            stopwords = bot.get("stopwords", None)
            log_query = bot.get("log_query", False)

            if model_format not in loaders:
                raise ValueError(f"Format {model_format} is not supported")

            mode = "r"
            if model_format == "pickle":
                mode += "b"

            with open(path, mode, encoding="utf-8") as fh:
                model_input = json.load(fh)

            loader = loaders[model_format]
            bot = loader(model_input, language=language, stopwords=stopwords)

            for channel in channels:
                if channel in bots:
                    raise ValueError(
                        f"A bot has already been instantiated for {channel}. Skipping {path}."
                    )
                bots[channel] = {"bot": bot, "log_query": log_query, "model_path": path}

        except Exception as e:
            logger.error("Failed to load bot. ", str(e))

    return create(bots)
