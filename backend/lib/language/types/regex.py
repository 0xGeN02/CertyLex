"""
This module contains the types used in the language module.
"""
import re
from typing import NewType, Tuple

ESPNamePattern = NewType("ESPNamePattern", re.Match)
MAYUS = r"[A-ZÁÉÍÓÚÑ]"
MINUS = r"[a-záéíóúñ]"
DETER = r"(?:del|de|la|los)"
NAME = rf"{MAYUS}(?:{MINUS}+|ª)"
NOMBRE_COMPUESTO = rf"{NAME}(?:-{NAME})?"
SPANISH_NAME_PATTERN : ESPNamePattern = re.compile(
    rf"(?:(?:{NAME}|{DETER})(?:-{NAME})?\s+)+(?:{NOMBRE_COMPUESTO})"
)

DNIFormat = Tuple[bool, bool]
UPPERCASE: bool = True # Normalize letter to uppercase as default
HYPHEN: bool = False # No space between digits and letter as default
DEFAULT_DNI_FORMAT: DNIFormat = (HYPHEN, UPPERCASE)

DNIRegexPattern = NewType("DNIRegexPattern", re.Pattern)
DNI_DIGITS = r"\d{8}"
DNI_LETTER = r"[A-HJ-NP-TV-Za-hj-np-tv-z]"  # Excluding I, Ñ, O, U
DNI_SEPARATOR = r"(?:-?\s*)"  # Optional hyphen and/or spaces between digits and letter
DNI_PATTERN : DNIRegexPattern = re.compile(rf"({DNI_DIGITS})({DNI_SEPARATOR})({DNI_LETTER})")
