# Documentación del NIF (Número de Identificación Fiscal)

Este documento describe los dos tipos principales de NIF en España:

- **NIF de personas físicas (DNI-NIF)**
- **NIF de personas jurídicas (anteriormente CIF)**

## NIF de Personas Físicas (DNI-NIF)

El NIF para personas físicas se basa en el Documento Nacional de Identidad (DNI) y consta de:

- **8 dígitos**
- **1 letra** calculada mediante un algoritmo:
  - Se divide el número (los 8 dígitos) entre 23 y el resto se utiliza para obtener la letra correspondiente según una tabla predeterminada.
  
Ejemplo de formato:

- `12345678Z`
- También se acepta la versión con guión o espacio, aunque se normaliza a `12345678Z`.

## NIF de Empresas (anteriormente CIF)

El NIF para personas jurídicas, antes conocido como CIF, tiene una estructura diferente:

- **Una letra inicial** que identifica el tipo de entidad (por ejemplo, "A" para sociedades anónimas, "B" para sociedades de responsabilidad limitada, etc.).
- **7 dígitos** numéricos.
- **Un dígito o letra final** que es el carácter de control, calculado mediante un algoritmo matemático.  
  - El algoritmo utiliza los 7 dígitos para generar un control que puede ser un número o una letra.
  
Ejemplo de formato:

- `A1234567B`
- Donde:
  - La **letra inicial** indica el tipo de entidad.
  - Los **7 dígitos** son la parte numérica de la identificación.
  - El **carácter final** es el dígito/letra de control calculado mediante el algoritmo.

## Uso en Procesamiento de Texto y Extracción de Datos

Para la extracción y validación de estos NIF en documentos, se pueden implementar expresiones regulares específicas que:

- Detecten el patrón de 8 dígitos y una letra para personas físicas.
- Detecten el patrón de una letra + 7 dígitos + dígito/letra de control para empresas.

Estas expresiones pueden ser integradas en un módulo de procesamiento de texto para normalizar y validar los datos extraídos de documentos.

## Consideraciones Adicionales

- **Normalización:**  
  Se recomienda utilizar funciones de normalización de texto (por ejemplo, Unicode NFC) para asegurar la coherencia en los datos extraídos.

- **Validación:**  
  Tanto para el NIF de personas físicas como para el de empresas, es crucial validar:
  - Las longitudes de los números.
  - La correcta correspondencia entre el número y la letra de control, utilizando el algoritmo específico de cada caso.

- **Extensibilidad:**  
  En futuras implementaciones, se puede extender la lógica para:
  - Integrar nuevas reglas de validación.
  - Aplicar técnicas de extracción complementarias, como reconocimiento de entidades (NER), para mejorar la precisión en textos con formatos variados.

## Conclusión

El manejo adecuado del NIF es esencial para cualquier sistema que trabaje con identificación fiscal en España. La estandarización y validación de estos números mejora la integridad de los datos y facilita integraciones posteriores con servicios externos o sistemas de gestión.
