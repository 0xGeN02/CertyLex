# -*- coding: utf-8 -*-
"""
Test the regex module
"""

from typing import List
import pytest
from lib.language.regex import name_detector, nif_detector, nif_empresa_detector
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
    # Valid NIF without hyphen
    ("12345678Z", ["12345678Z"]),
    # Valid NIF with hyphen
    ("12345678-Z", ["12345678Z"]),
    # Valid NIF with hyphen and lowercase letter, should be normalized to uppercase
    ("12345678-z", ["12345678Z"]),
    ("12345678-Z", ["12345678Z"]),
    # NIF embedded in text
    ("El NIF es 12345678Z.", ["12345678Z"]),
    # Multiple valid NIF in text: using 00000000, 0 % 23 = 0 → T
    ("NIFs: 12345678Z y 00000000T", ["12345678Z", "00000000T"]),
    # Invalid NIF: Wrong letter (12345678 mod 23 is 14 which should be Z)
    ("12345678A", []),
    # Text without NIF
    ("Sin NIF aquí", []),
])
def test_nif_detector(text, expected):
    """
    Test the nif detector
    """
    text: str = encode_spanish(text)
    text: str = normalize_text(text)
    result = nif_detector(text)
    assert result == expected, f"For text: {text} expected {expected} but got {result}"

@pytest.mark.parametrize("text, nif_format, expected", [
    # (HYPHEN, UPPERCASE)
    ("12345678Z", (False, True), ["12345678Z"]),
    ("12345678Z", (True, True),  ["12345678-Z"]),
    # (HYPHEN, not UPPERCASE)
    ("12345678Z", (False, False), ["12345678z"]),
    ("12345678Z", (True, False),  ["12345678-z"]),
    # NIF embedded in text with multiple matches
    ("NIFs: 12345678Z y 00000000T", (True, True),  ["12345678-Z", "00000000-T"]),
    ("NIFs: 12345678Z y 00000000T", (False, False), ["12345678z", "00000000t"]),
])
def test_nif_formatting(text, nif_format, expected):
    """
    Test que valida que el formato del NIF devuelto por nif_detector
    varía según los valores de NIFFormat.
    """
    text: str = encode_spanish(text)
    text: str = normalize_text(text)
    result = nif_detector(text, nif_format=nif_format)
    assert result == expected, f"For text: {text} with format {nif_format} expected {expected} but got {result}"

@pytest.mark.parametrize("text, expected", [
    # NIF de empresa aislado en el texto
    ("A12345671", ["A12345671"]),
    # NIF de empresa incluido en un párrafo
    ("La empresa con NIF A1234567-1 es reconocida.", ["A12345671"]),
    # Múltiples NIF de empresa en el texto
    ("NIFs: A-12345671 y A-1234567-1", ["A12345671", "A12345671"]),
    # NIF de empresa con letra minúscula
    ("a12345671", ["A12345671"]),
    # Texto sin NIF de empresa
    ("No se encontró ningún NIF de empresa aquí.", []),
])
def test_nif_empresa_detector(text: str, expected: List[str]):
    """
    Comprueba que la función nif_empresa_detector detecta correctamente
    los NIF de empresa en distintos textos.
    """
    # Normalizamos el texto (las funciones internas ya lo hacen)
    text = normalize_text(encode_spanish(text))
    result = nif_empresa_detector(text)
    assert result == expected, f"Para el texto: {text} se esperaba {expected} pero se obtuvo {result}"
