"""
Normalizador de texto en español.
"""
import unicodedata

def normalize_text(text: str) -> str:
    """
    Normaliza el texto usando la forma Unicode NFC.
    """
    try:
        return unicodedata.normalize("NFC", text)
    except TypeError:
        return text

def encode_spanish(text: str) -> str:
    """
    Decodifica el texto en español.
    """
    try:
        return text.encode("latin1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return text
