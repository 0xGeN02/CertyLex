"""
This file contains the regex patterns for the language module and pocessing data
"""

import re
from typing import List, Any

# Regex for name detection in text
def name_detector(text: str) -> List[str]:
    """
    Detect names in a text
    """
    mayus = r"[A-ZÁÉÍÓÚÑ]"
    minus = r"[a-záéíóúñ]"
    deter = r"(?:del|de|la|los)"

    # Name / Surname regex pattern
    name_pattern = re.compile(
        rf"(?:(?:{mayus}(?:{minus}+|ª)|{deter})(?:-{mayus}(?:{minus}+|ª))?\s+)+"
        rf"(?:{mayus}(?:{minus}+|ª)(?:-{mayus}(?:{minus}+|ª))?)"
    )
    matches: List[Any] = name_pattern.findall(text)
    names: List[str] = [m.strip() for m in matches if m.strip()]
    return names

def dni_detector(text: str) -> List[str]:
    """
    Detect DNI in a text.
    Un DNI consists of 8 digits and a letter.
    eg. 12345678Z or 12345678-Z or 12345678-z not 12345678 z
    The letter is calculated as follows:
    mod = number % 23
    """
    mod_to_letter = {
        0: "T",  1: "R",  2: "W",  3: "A",  4: "G",  5: "M",
        6: "Y",  7: "F",  8: "P",  9: "D", 10: "X", 11: "B",
       12: "N", 13: "J", 14: "Z", 15: "S", 16: "Q", 17: "V",
       18: "H", 19: "L", 20: "C", 21: "K", 22: "E",
    }
    dni_digits = r"\d{8}"
    dni_letter = r"[A-HJ-NP-TV-Za-hj-np-tv-z]" # Excluding I, Ñ, O, U (23 + 4 = 27letras)
    dni_pattern = re.compile(rf"({dni_digits})(?:-?)({dni_letter})")

    matches = []
    for m in dni_pattern.finditer(text):
        number_str = m.group(1)
        letter_found = m.group(2).upper()
        try:
            number = int(number_str)
        except ValueError:
            continue
        # Calcula la letra esperada
        mod = number % 23
        expected_letter = mod_to_letter[mod]
        if letter_found == expected_letter:
            # Si es válida, se retorna el DNI completo (sin espacios adicionales)
            matches.append(f"{number_str}{letter_found}")
    return matches
