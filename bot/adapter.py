from markovify.text import Text, NewlineText
import re
import logging
import random
from stop_words import get_stop_words, StopWordError
from typing import Union

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

    def __init__(self, model: Union[Text, NewlineText], language: str = "italian", compiled=True):
        self.model = model
        if compiled and not self.model.chain.compiled:
            self.model.compile(inplace=True)
        try:
            self.stopwords = get_stop_words(language)
        except (KeyError, StopWordError) as ke:
            logger.error(f"language={language} not supported. {ke}")
            raise KeyError(ke)

        self.language = language
        self.state_space_size = len(self.model.chain.model)
        self.state_size = self.model.state_size
        self.parsed_sentences = self.model.parsed_sentences
        self.last_updated = "Not implemented"

    def status(self):
        return {
            'state_space_size': self.state_space_size,
            'state_size': self.state_size,
            'parsed_sentences': len(self.parsed_sentences),
            'language': self.language,
            'bot_version': __version__,
            'last_updated': self.last_updated
        }

    def generate_sentences(self, init_states, tries):
        for init_state in init_states:
            try:
                sentence = self.model.make_sentence_with_start(init_state, tries=tries, strict=False)
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
        # TODO(gmodena): test sentence quality with init states of more than a single word
        sentences = list(self.generate_sentences(words, self.MAX_TRIES))
        if sentences:
            response = random.choice(sentences)
        if not response:
            response = self.model.make_short_sentence(
                self.MAX_WORDS_IN_SENTENCE, tries=self.MAX_TRIES
            )
        if not response:
            response = self.DEFAULT_RESPONSE
        return response
