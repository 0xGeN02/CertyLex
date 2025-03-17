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
