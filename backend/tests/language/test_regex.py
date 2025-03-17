"""
Test the regex module
"""

from typing import List
import pytest
from lib.language.regex import name_detector

@pytest.mark.parametrize("text, expected", [
    ("Juan Pérez", ["Juan Pérez"]),
    ("María del Carmen Rodríguez López", ["María del Carmen Rodríguez López"]),
    ("José de los Ángeles Martínez", ["José de los Ángeles Martínez"]),
    ("Mª del Mar Fernández de la Torre", ["Mª del Mar Fernández de la Torre"]),
    ("Esto no es un nombre", []),
    ("Pedro García y Ana López son amigos", ["Pedro García", "Ana López"]),
])
def test_is_valid_name(text, expected):
    """
    Test if the name is valid
    """
    result: List[str] = name_detector(text)
    assert result == expected, f"Expected {expected} but got {result}"
