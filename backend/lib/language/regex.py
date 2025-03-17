"""
This file contains the regex patterns for the language module and pocessing data
"""

import re
from typing import List

# Regex for name detection in text

def detect_names(text: str) -> List[str]:
    """
    Detect names in a given text
    - Nombre: ([A-Z][a-z]+) | ([A-Z][a-z]+)\-\1 | ([A-Z][a-z]+)\_\1\_\1 (eg. Juan, Juan-Pablo, Maria del Carmen, Maria de los Angeles, Mª del Carmen)
    - Apellido: ([A-Z][a-z]+) | ([A-Z][a-z]+)\-\1 | ([A-Z][a-z]+)\-\1 (eg. Perez, Perez-Gomez, De Juan)
 
    Expected name formats (spanish):
    - Nombre Apellido
    - Nombre Apellido Apellido
    - Nombre Nombre Apellido Apellido
    """
    
    # Name / Surname regex pattern
    name_pattern = re.compile(r"([A-Z][a-z]+) | ([A-Z][a-z]+)\-([A-Z][a-z]+)")