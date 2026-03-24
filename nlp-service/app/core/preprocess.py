import spacy
from app.core.config import settings

_nlp = None


def _get_nlp():
    global _nlp
    if _nlp is None:
        _nlp = spacy.load(settings.SPACY_MODEL, disable=["parser", "ner"])
    return _nlp


def preprocess(texts: list[str]) -> list[str]:
    nlp = _get_nlp()
    cleaned = []
    for doc in nlp.pipe(texts, batch_size=32):
        tokens = [
            t.lemma_.lower()
            for t in doc
            if not t.is_stop and not t.is_punct and not t.is_space and len(t.text) > 2
        ]
        cleaned.append(" ".join(tokens))
    return cleaned
