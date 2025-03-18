# -*- coding: utf-8 -*-
"""
Test the regex module
"""

from typing import List
import pytest
from lib.language.regex import name_detector, dni_detector
from lib.language.text_normalizer import normalize_text, encode_spanish

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
    text: str = encode_spanish(text)
    text: str = normalize_text(text)
    result: List[str] = name_detector(text)
    assert result == expected, f"Expected {expected} but got {result}"

@pytest.mark.parametrize("text, expected", [
    # Valid DNI without hyphen
    ("12345678Z", ["12345678Z"]),
    ("12345678 Z", ["12345678Z"]),
    # Valid DNI with hyphen and lowercase letter, should be normalized to uppercase
    ("12345678-z", ["12345678Z"]),
    ("12345678-Z", ["12345678Z"]),
    # DNI embedded in text
    ("El DNI es 12345678Z.", ["12345678Z"]),
    # Multiple valid DNI in text: using 00000000, 0 % 23 = 0 → T
    ("DNIs: 12345678Z y 00000000T", ["12345678Z", "00000000T"]),
    # Invalid DNI: Wrong letter (12345678 mod 23 is 14 which should be Z)
    ("12345678A", []),
    # Text without DNI
    ("Sin DNI aquí", []),
])
def test_dni_detector(text, expected):
    """
    Test the DNI detector
    """
    text: str = encode_spanish(text)
    text: str = normalize_text(text)
    result = dni_detector(text)
    assert result == expected, f"For text: {text} expected {expected} but got {result}"

@pytest.mark.parametrize("text, dni_format, expected", [
    # (HYPHEN, UPPERCASE)
    ("12345678Z", (False, True), ["12345678Z"]),
    ("12345678Z", (True, True),  ["12345678-Z"]),
    # (HYPHEN, not UPPERCASE)
    ("12345678Z", (False, False), ["12345678z"]),
    ("12345678Z", (True, False),  ["12345678-z"]),
    # DNI embedded in text with multiple matches
    ("DNIs: 12345678Z y 00000000T", (True, True),  ["12345678-Z", "00000000-T"]),
    ("DNIs: 12345678Z y 00000000T", (False, False), ["12345678z", "00000000t"]),
])
def test_dni_formatting(text, dni_format, expected):
    """
    Test que valida que el formato del DNI devuelto por dni_detector
    varía según los valores de DNIFormat.
    """
    text: str = encode_spanish(text)
    text: str = normalize_text(text)
    result = dni_detector(text, dni_format=dni_format)
    assert result == expected, f"For text: {text} with format {dni_format} expected {expected} but got {result}"