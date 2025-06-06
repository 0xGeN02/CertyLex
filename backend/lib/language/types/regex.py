"""
This module contains the types used in the language module.
"""
import re
from typing import NewType, Tuple

ESPNameRegexPattern = NewType("ESPNameRegexPattern", re.Match)
MAYUS = r"[A-ZÁÉÍÓÚÑ]"
MINUS = r"[a-záéíóúñ]"
DETER = r"(?:del|de|la|los)"
NAME = rf"{MAYUS}(?:{MINUS}+|ª)"
NOMBRE_COMPUESTO = rf"{NAME}(?:-{NAME})?"
SPANISH_NAME_PATTERN : ESPNameRegexPattern = re.compile(
    rf"\b(?:(?:{NAME}|{DETER})(?:-{NAME})?\s+)+(?:{NOMBRE_COMPUESTO})\b"
)

NIFFormat = Tuple[bool, bool]
UPPERCASE: bool = True # Normalize letter to uppercase as default
HYPHEN: bool = False # No space between digits and letter as default
DEFAULT_NIF_FORMAT: NIFFormat = (HYPHEN, UPPERCASE)

NIFRegexPattern = NewType("NIFRegexPattern", re.Pattern)
NIF_DIGITS = r"\d{8}"
NIF_LETTER = r"[A-HJ-NP-TV-Za-hj-np-tv-z]"  # Excluding I, Ñ, O, U
NIF_SEPARATOR = r"-?"  # Optional hyphen between digits and letter
NIF_PATTERN : NIFRegexPattern = re.compile(rf"\b({NIF_DIGITS})({NIF_SEPARATOR})({NIF_LETTER})\b")

# NIFEmpresa: 1 letter + 7 digits + 1 letter/digit
# - 1 letter + 7 digits + 1 letter/digit
# 1st value is a Letter identifies the type of entity (A-H,J,N-W)
# 9th value is a control code (digit or letter) generated by a mathematical formula
NIFEmpresaRegexPattern = NewType("NIFEmpresaRegexPattern", re.Pattern)
NIF_SEPARATOR = r"[ -]*"  # Permite cero o más espacios y/o guiones
NIF_EMPRESA_ENDS_DIGIT = rf"\b[ABEHabeh]{NIF_SEPARATOR}\d{{7}}{NIF_SEPARATOR}[0-9]\b"
NIF_EMPRESA_ENDS_LETTER = rf"\b[PQRSTWNpqrstwn]{NIF_SEPARATOR}\d{{7}}{NIF_SEPARATOR}[A-Ja-j]\b"
NIF_EMPRESA_ENDS_BOTH  = rf"\b[CDFGJLMUVcdfgjlmuv]{NIF_SEPARATOR}\d{{7}}{NIF_SEPARATOR}[0-9A-Ja-j]\b"

NIF_EMPRESA_PATTERN: NIFEmpresaRegexPattern = re.compile(
    rf"({NIF_EMPRESA_ENDS_DIGIT})|({NIF_EMPRESA_ENDS_LETTER})|({NIF_EMPRESA_ENDS_BOTH})"
)
# (eg A12345678, A-1234567-8, P-1234567-J, C-1234567-8, C-1234567-J, etc.)
