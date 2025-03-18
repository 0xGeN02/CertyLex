"""
This package contains the language models and the language processing tools.
"""

from .regex import name_detector, dni_detector, DNIFormat
from .text_normalizer import normalize_text, encode_spanish
