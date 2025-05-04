# -*- coding: utf-8 -*-
"""
This file contains the regex patterns for the language module and pocessing data
"""

from typing import List
from backend.lib.language.text_normalizer import normalize_text, encode_spanish
from backend.lib.language.types.regex import (ESPNameRegexPattern, SPANISH_NAME_PATTERN,
                                      NIFRegexPattern, NIFFormat, DEFAULT_NIF_FORMAT, 
                                      NIF_PATTERN, NIF_EMPRESA_PATTERN, NIFEmpresaRegexPattern)

def name_detector(
    text: str,
    spanish_name_pattern: ESPNameRegexPattern = SPANISH_NAME_PATTERN
    ) -> List[ESPNameRegexPattern]:
    """
    Detect names in a text
    """
    text: str = normalize_text(text)
    text: str = encode_spanish(text)
    matches: List[ESPNameRegexPattern] = spanish_name_pattern.findall(text)
    names: List[ESPNameRegexPattern] = [m.strip() for m in matches if m.strip()] # Remove empty strings
    return names

def nif_detector(
    text: str,
    nif_format: NIFFormat = DEFAULT_NIF_FORMAT,
    nif_pattern: NIFRegexPattern = NIF_PATTERN
    ) -> List[NIFRegexPattern]:
    """
    Detect NIF in a text.
    A NIF consists of 8 digits and a letter.
    e.g. 12345678Z or 12345678-Z or 12345678-z (note: 12345678 z is invalid)
    The letter is calculated as:
      mod = number % 23

    @return: List of valid NIF found in the text
    @format: Tuple of two booleans: (HYPHEN, UPPERCASE)
      - If HYPHEN is True => a hyphen(-) will be inserted between digits and letter.
      - If HYPHEN is False => no separator is inserted.
      - If UPPERCASE is True => the letter is returned in uppercase.
      - If UPPERCASE is False => the letter is returned in lowercase.
    """
    text: str = normalize_text(text)
    text: str = encode_spanish(text)
    mod_to_letter = {
        0: "T",  1: "R",  2: "W",  3: "A",  4: "G",  5: "M",
        6: "Y",  7: "F",  8: "P",  9: "D", 10: "X", 11: "B",
       12: "N", 13: "J", 14: "Z", 15: "S", 16: "Q", 17: "V",
       18: "H", 19: "L", 20: "C", 21: "K", 22: "E",
    }

    return nif_formatter(text, nif_pattern, mod_to_letter, nif_format)

def nif_formatter(
    text: str,
    nif_pattern: NIFRegexPattern,
    mod_to_letter: dict,
    nif_format: NIFFormat
    ) -> List[NIFRegexPattern]:
    """
    Itera sobre los matches encontrados en el texto utilizando el patrón NIF y 
    retorna una lista de NIF formateados correctamente según las opciones de 'nif_format'.

    Parameters:
      text: El texto a escanear.
      nif_pattern: Expresión regular compilada para detectar el NIF.
      mod_to_letter: Diccionario que mapea el módulo (number % 23) a la letra correspondiente.
      nif_format: Tupla (HYPHEN, UPPERCASE) donde:
          - HYPHEN: Si es True se inserta un guión entre los dígitos y la letra.
          - UPPERCASE: Si es True se retorna la letra en mayúsculas, sino en minúsculas.

    Returns:
      Lista de NIF formateados que cumplen con la validación.
    """
    matches = []
    for m in nif_pattern.finditer(text):
        number_str = m.group(1)
        letter_raw = m.group(3)
        try:
            number = int(number_str)
        except ValueError:
            continue
        mod = number % 23
        # Determina la versión de la letra (mayúscula o minúscula)
        if nif_format[1]:
            expected_letter = mod_to_letter[mod]
            letter_found = letter_raw.upper()
        else:
            expected_letter = mod_to_letter[mod].lower()
            letter_found = letter_raw.lower()
        if letter_found == expected_letter:
            # Formatea el nif con o sin guión según la opción HYPHEN
            if nif_format[0]:
                nif: NIFRegexPattern = f"{number_str}-{letter_found}"
            else:
                nif: NIFRegexPattern = f"{number_str}{letter_found}"
            matches.append(nif)
    return matches

def nif_empresa_detector(
    text: str
) -> List[NIFEmpresaRegexPattern]:
    """
    Función de conveniencia que normaliza el texto y retorna los NIF de empresa encontrados y
    formateados correctamente.
    Input: A12345671, A-1234567-1, A1234567-1, A-12345671
    Output: A12345671
    """
    text = normalize_text(encode_spanish(text))
    text = encode_spanish(text)
    # Encontramos todas las coincidencias utilizando finditer para obtener los match objects.
    matches = NIF_EMPRESA_PATTERN.finditer(text)
    # Cambiamos a mayúsculas y eliminamos los guiones de cada coincidencia.
    # Luego eliminamos duplicados usando set y los convertimos de nuevo a lista.
    # Finalmente, ordenamos la lista de NIF.
    cleaned_results = []
    for m in matches:
        cleaned_results.append(m.group(0).upper().replace("-", ""))
    return sorted(cleaned_results)
