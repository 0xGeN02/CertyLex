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
    # Name / Surname regex pattern
    pattern = re.compile(
        r"(?:(?:[A-ZÁÉÍÓÚÑ](?:[a-záéíóúñ]+|ª)|(?:del|de|la|los))(?:-[A-ZÁÉÍÓÚÑ](?:[a-záéíóúñ]+|ª))?\s+)+"
        r"(?:[A-ZÁÉÍÓÚÑ](?:[a-záéíóúñ]+|ª)(?:-[A-ZÁÉÍÓÚÑ](?:[a-záéíóúñ]+|ª))?)"
    )
    matches: List[Any] = pattern.findall(text)
    names: List[str] = [m.strip() for m in matches if m.strip()]
    return names
