"""
This package contains the language models and the language processing tools.
"""

from .regex import name_detector, nif_detector, NIFFormat, nif_empresa_detector
from .text_normalizer import normalize_text, encode_spanish
