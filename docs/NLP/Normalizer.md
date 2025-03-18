# Text Normalizer

El módulo de normalización de texto se encuentra en:
`backend/lib/language/text_normalizer.py`

## Objetivo

El propósito de la función `normalize_text` es asegurar que todos los caracteres de un texto se expresen de forma consistente utilizando la forma Unicode **NFC**. En español, esto es especialmente útil para tratar correctamente caracteres acentuados o compuestos. Por ejemplo, la "é" puede representarse como un solo carácter o como la combinación de "e" y el acento agudo; la normalización permite que ambas representaciones se conviertan en la misma cadena.

## Cómo Funciona

La implementación utiliza el módulo `unicodedata` de Python:

```python
import unicodedata

def normalize_text(text: str) -> str:
    """
    Normaliza el texto usando la forma Unicode NFC.
    """
    return unicodedata.normalize("NFC", text)
```

Al llamar a `normalize_text` sobre cualquier entrada, la función transforma el texto a su forma compuesta canónica, lo que facilita que las expresiones regulares detecten patrones sin problemas por variaciones en la codificación de acentos.

## Impacto en los Tests

Gracias a la normalización:

- Los nombres con acentos se reconocen correctamente.  
  Por ejemplo:
  - `"Juan Pérez"` se procesa de manera que la "é" se interpreta uniformemente, permitiendo que `name_detector` devuelva `["Juan Pérez"]`.
  - `"María del Carmen Rodríguez López"` y nombres similares se detectan sin problemas, ya que cualquier diferencia en la representación Unicode se elimina.
  
- La detección de DNI también se beneficia, ya que el patrón de expresión regular no se ve afectado por posibles diferencias en la codificación de caracteres (aunque en este caso es menos habitual, la normalización garantiza consistencia en todo el procesamiento).
  
Los resultados de los tests se ven así debido al encoding de terminal windows pero se alamcenan en catellano legible:

```sh
backend/tests/language/test_regex.py::test_is_valid_name[Juan P\xe9rez-expected0] PASSED                         
backend/tests/language/test_regex.py::test_is_valid_name[Mar\xeda del Carmen Rodr\xedguez L\xf3pez-expected1] PASSED
backend/tests/language/test_regex.py::test_is_valid_name[Jos\xe9 de los \xc1ngeles Mart\xednez-expected2] PASSED
...
backend/tests/language/test_regex.py::test_dni_detector[...] PASSED
```

## Terminal en UTF-8 encoding (chcp 65001)

```sh (chcp 65001)
backend/tests/language/test_regex.py::test_is_valid_name[Juan Pérez-expected0] PASSED                         
backend/tests/language/test_regex.py::test_is_valid_name[María del Carmen Rodríguez López-expected1] PASSED
backend/tests/language/test_regex.py::test_is_valid_name[José de los Ángeles Martínez-expected2] PASSED
...
backend/tests/language/test_regex.py::test_dni_detector[...] PASSED

Sin la normalización, se podrían experimentar fallos o resultados inconsistentes debido a la forma en que se representan internamente los acentos y otros diacríticos.

## Conclusión

La función `normalize_text` es un paso esencial en el procesamiento de textos en español, ya que garantiza que tanto la detección de nombres (`name_detector`) como la detección de DNI (`dni_detector`) operen de manera confiable y consistente, permitiendo que todos los tests (como los previamente mostrados) pasen sin problemas.
