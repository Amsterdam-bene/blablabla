import logging
import random
import re
from typing import Union

from markovify.text import Text, NewlineText
from stop_words import get_stop_words, StopWordError

__version__ = "0.1.0"
logger = logging.getLogger()


def from_newline_text(text: str, language: str = "italian"):
    return MarkovifyAdapter(NewlineText(text), language)


def from_object(model: Union[Text, NewlineText], language: str = "italian"):
    return MarkovifyAdapter(model, language)


class MarkovifyAdapter:
    MAX_TRIES = 10
    MAX_WORDS_IN_SENTENCE = 180
    DEFAULT_RESPONSE = (
        "Tarapia sulla supercazzola con scappellamento a destra o sinistra?"
    )

    def __init__(self, model: Union[Text, NewlineText], language: str = "italian"):
        self.model = model
        try:
            self.stopwords = get_stop_words(language)
        except (KeyError, StopWordError) as ke:
            logger.error(f"language={language} not supported. {ke}")
            raise KeyError(ke)
        else:
            self.language = language

    def generate_sentences(self, init_states, tries):
        for init_state in init_states:
            try:
                sentence = self.model.make_sentence_with_start(init_state, tries=tries)
            except KeyError as ke:
                logger.error(f"Unknown initial state: {ke}")
            else:
                if sentence:
                    yield sentence

    def sample(self, text):
        """
        Generate a reply for an input sentence

        :param sentence:
        :return:
        """
        response = None
        words = re.findall(r"(\w+)", text)

        words = [word for word in words if word.lower() not in self.stopwords]
        random.shuffle(words)

        sentences = list(self.generate_sentences(words, self.MAX_TRIES))
        if any(sentences):
            response = random.choice(sentences)
        if not response:
            response = self.model.make_short_sentence(
                self.MAX_WORDS_IN_SENTENCE, tries=self.MAX_TRIES
            )
        if not response:
            response = self.DEFAULT_RESPONSE
        return response
