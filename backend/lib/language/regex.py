# -*- coding: utf-8 -*-
"""
This file contains the regex patterns for the language module and pocessing data
"""

import re
from typing import List, Tuple, NewType
from lib.language.text_normalizer import normalize_text

ESPNamePattern = NewType("ESPNamePattern", re.Match)
MAYUS = r"[A-ZÁÉÍÓÚÑ]"
MINUS = r"[a-záéíóúñ]"
DETER = r"(?:del|de|la|los)"
NAME = rf"{MAYUS}(?:{MINUS}+|ª)"
NOMBRE_COMPUESTO = rf"{NAME}(?:-{NAME})?"
SPANISH_NAME_PATTERN : ESPNamePattern = re.compile(
    rf"(?:(?:{NAME}|{DETER})(?:-{NAME})?\s+)+(?:{NOMBRE_COMPUESTO})"
)

def name_detector(
    text: str,
    spanish_name_pattern: ESPNamePattern = SPANISH_NAME_PATTERN
    ) -> List[ESPNamePattern]:
    """
    Detect names in a text
    """
    text: str = normalize_text(text)
    matches: List[ESPNamePattern] = spanish_name_pattern.findall(text)
    names: List[ESPNamePattern] = [m.strip() for m in matches if m.strip()] # Remove empty strings
    return names

DNIFormat = Tuple[bool, bool]
UPPERCASE: bool = True # Normalize letter to uppercase as default
HYPHEN: bool = False # No space between digits and letter as default
DEFAULT_DNI_FORMAT: DNIFormat = (HYPHEN, UPPERCASE)

DNIRegexPattern = NewType("DNIRegexPattern", re.Pattern)
DNI_DIGITS = r"\d{8}"
DNI_LETTER = r"[A-HJ-NP-TV-Za-hj-np-tv-z]"  # Excluding I, Ñ, O, U
DNI_SEPARATOR = r"(?:-?\s*)"  # Optional hyphen and/or spaces between digits and letter
DNI_PATTERN : DNIRegexPattern = re.compile(rf"({DNI_DIGITS})({DNI_SEPARATOR})({DNI_LETTER})")

def dni_detector(
    text: str,
    dni_format: DNIFormat = DEFAULT_DNI_FORMAT,
    dni_pattern: DNIRegexPattern = DNI_PATTERN
    ) -> List[DNIRegexPattern]:
    """
    Detect DNI in a text.
    A DNI consists of 8 digits and a letter.
    e.g. 12345678Z or 12345678-Z or 12345678-z (note: 12345678 z is invalid)
    The letter is calculated as:
      mod = number % 23

    @return: List of valid DNI found in the text
    @format: Tuple of two booleans: (HYPHEN, UPPERCASE)
      - If HYPHEN is True => a hyphen(-) will be inserted between digits and letter.
      - If HYPHEN is False => no separator is inserted.
      - If UPPERCASE is True => the letter is returned in uppercase.
      - If UPPERCASE is False => the letter is returned in lowercase.
    """
    text: str = normalize_text(text)
    mod_to_letter = {
        0: "T",  1: "R",  2: "W",  3: "A",  4: "G",  5: "M",
        6: "Y",  7: "F",  8: "P",  9: "D", 10: "X", 11: "B",
       12: "N", 13: "J", 14: "Z", 15: "S", 16: "Q", 17: "V",
       18: "H", 19: "L", 20: "C", 21: "K", 22: "E",
    }

    return dni_formatter(text, dni_pattern, mod_to_letter, dni_format)

def dni_formatter(
    text: str,
    dni_pattern: DNIRegexPattern,
    mod_to_letter: dict,
    dni_format: DNIFormat
    ) -> List[DNIRegexPattern]:
    """
    Itera sobre los matches encontrados en el texto utilizando el patrón DNI y 
    retorna una lista de DNI formateados correctamente según las opciones de 'dni_format'.

    Parameters:
      text: El texto a escanear.
      dni_pattern: Expresión regular compilada para detectar el DNI.
      mod_to_letter: Diccionario que mapea el módulo (number % 23) a la letra correspondiente.
      dni_format: Tupla (HYPHEN, UPPERCASE) donde:
          - HYPHEN: Si es True se inserta un guión entre los dígitos y la letra.
          - UPPERCASE: Si es True se retorna la letra en mayúsculas, sino en minúsculas.

    Returns:
      Lista de DNI formateados que cumplen con la validación.
    """
    matches = []
    for m in dni_pattern.finditer(text):
        number_str = m.group(1)
        letter_raw = m.group(3)
        try:
            number = int(number_str)
        except ValueError:
            continue
        mod = number % 23
        # Determina la versión de la letra (mayúscula o minúscula)
        if dni_format[1]:
            expected_letter = mod_to_letter[mod]
            letter_found = letter_raw.upper()
        else:
            expected_letter = mod_to_letter[mod].lower()
            letter_found = letter_raw.lower()
        if letter_found == expected_letter:
            # Formatea el DNI con o sin guión según la opción HYPHEN
            if dni_format[0]:
                dni: DNIRegexPattern = f"{number_str}-{letter_found}"
            else:
                dni: DNIRegexPattern = f"{number_str}{letter_found}"
            matches.append(dni)
    return matches
