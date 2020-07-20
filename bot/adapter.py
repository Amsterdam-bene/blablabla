import logging
import random
import re
from typing import Union, List, Optional

from markovify.text import Text, NewlineText
from stop_words import get_stop_words, StopWordError

__version__ = "0.1.0"
logger = logging.getLogger()


def from_newline_text(
    text: str,
    retain_original=True,
    language: Optional[str] = None,
    stopwords: Optional[List[str]] = None,
):
    return MarkovifyAdapter(
        NewlineText(text, retain_original=retain_original), language, stopwords
    )


def from_json(
    json_thing: dict,
    language: Optional[str] = None,
    stopwords: Optional[List[str]] = None,
):
    return MarkovifyAdapter(NewlineText.from_dict(json_thing), language, stopwords)


def from_object(
    model: Union[Text, NewlineText],
    language: Optional[str] = None,
    stopwords: Optional[List[str]] = None,
):
    return MarkovifyAdapter(model, language, stopwords)


class MarkovifyAdapter:
    MAX_TRIES = 10
    MAX_WORDS_IN_SENTENCE = 180
    DEFAULT_LANGUAGE = (
        "en"  # Assume some degree of English text will be present in the markov chain.
    )
    DEFAULT_RESPONSE = (
        "Tarapia sulla supercazzola con scappellamento a destra o sinistra?"
    )

    def __init__(
        self,
        model: Union[Text, NewlineText],
        language: Optional[str] = None,
        stopwords: Optional[List[str]] = None,
        compiled=True,
    ):
        self.model = model
        if compiled and not self.model.chain.compiled:
            self.model.compile(inplace=True)

        self.language = language
        self.stopwords = []
        try:
            self.set_stopwords(stopwords)
        except (KeyError, StopWordError) as ke:
            logger.error(f"language={language} not supported. {ke}")
            raise KeyError(ke)

        self.state_space_size = len(self.model.chain.model)
        self.state_size = self.model.state_size

        try:
            self.parsed_sentences = len(self.model.parsed_sentences)
        except AttributeError:
            # Models trained with retain_original=False won't have the parsed_sentences
            # attribute
            self.parsed_sentences = None
        self.last_updated = "Not implemented"

    def set_stopwords(self, stopwords):
        self.stopwords = get_stop_words(self.DEFAULT_LANGUAGE)
        if self.language:
            self.stopwords.extend(get_stop_words(self.language))
        if stopwords:
            self.stopwords.extend([word.lower() for word in stopwords])

    def status(self):
        return {
            "state_space_size": self.state_space_size,
            "state_size": self.state_size,
            "parsed_sentences": self.parsed_sentences,
            "language": self.language,
            "bot_version": __version__,
            "last_updated": self.last_updated,
        }

    def generate_sentences(self, init_states, tries, sanitizers=(lambda x: x,)):

        for init_state in init_states:
            try:
                sentence = self.model.make_sentence_with_start(
                    init_state, tries=tries, strict=True
                )
            except KeyError as ke:
                logger.error(f"Unknown initial state: {ke}")
            else:
                if sentence and all(sanitize(sentence) for sanitize in sanitizers):
                    yield sentence

    def sample(self, sentence: str, sanitizers: Optional[object] = None) -> object:
        """
        Generate a reply for an input sentence

        :param sentence: input state for the markov chain
        :param sanitizers: an (optional) list of functions to sanitize the markov chain output
        :return: a reply
        """
        sanitizers = sanitizers
        if not sanitizers:
            sanitizers = (lambda x: x,)

        response = None
        words = re.findall(r"(\w+)", sentence)

        words = [word for word in words if word.lower() not in self.stopwords]
        random.shuffle(words)
        # TODO(gmodena): test sentence quality with init states of more than a single word
        sentences = list(
            self.generate_sentences(words, self.MAX_TRIES, sanitizers=sanitizers)
        )
        if sentences:
            response = random.choice(sentences)
        if not response:
            response = self.model.make_short_sentence(
                self.MAX_WORDS_IN_SENTENCE, tries=self.MAX_TRIES
            )
        if not response or not all(sanitize(response) for sanitize in sanitizers):
            response = self.DEFAULT_RESPONSE
        return response
