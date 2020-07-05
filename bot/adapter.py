import markovify
import re
import logging
import random
from stop_words import get_stop_words, StopWordError

logger = logging.getLogger()


class MarkovifyAdapter:
    MAX_TRIES = 10
    MAX_WORDS_IN_SENTENCE = 180
    DEFAULT_RESPONSE = (
        "Tarapia sulla supercazzola con scappellamento a destra o sinistra?"
    )

    def __init__(self, text: str, language: str = "italian"):
        self.model = markovify.NewlineText(text)
        try:
            self.stopwords = get_stop_words(language)
        except (KeyError, StopWordError) as ke:
            logger.error(f"language={language} not supported. {ke}")
            raise KeyError(ke)

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
