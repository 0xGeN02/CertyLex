# Especificaciones del NIF para Empresas

>[!INFO]  
>Es importante destacar que, desde la entrada en vigor del Real Decreto 1065/2007, el Código de Identificación Fiscal (CIF) fue sustituido por el NIF para las personas jurídicas. Aunque anteriormente los dos primeros dígitos se asignaban en función de la provincia, actualmente se asignan de manera secuencial sin relación directa con la localización geográfica.

El NIF para empresas consta de tres partes:

1. **Clave Inicial:** Una letra que indica el tipo de entidad.
2. **Siete Dígitos Centrales:** Un número secuencial.
3. **Carácter de Control:** Puede ser un dígito o una letra, calculado mediante un algoritmo.

---

## 1. Clave Inicial

La letra inicial indica la forma jurídica de la entidad. Las claves válidas son:

- **A**: Sociedades anónimas.
- **B**: Sociedades de responsabilidad limitada.
- **C**: Sociedades colectivas.
- **D**: Sociedades comanditarias.
- **E**: Comunidades de bienes, herencias yacentes y demás entidades carentes de personalidad jurídica no incluidas expresamente en otras claves.
- **F**: Sociedades cooperativas.
- **G**: Asociaciones.
- **H**: Comunidades de propietarios en régimen de propiedad horizontal.
- **J**: Sociedades civiles.
- **P**: Corporaciones Locales.
- **Q**: Organismos públicos.
- **R**: Congregaciones e instituciones religiosas.
- **S**: Órganos de la Administración del Estado y de las Comunidades Autónomas.
- **U**: Uniones Temporales de Empresas.
- **V**: Otros tipos no definidos en el resto de las claves.
- **W**: Establecimientos permanentes de entidades no residentes en territorio español (NIF W).

>[!INFO]
> **Nota:** Dependiendo de esta clave inicial se establece el tipo de carácter de control:
>
> - Si la clave es **'A', 'B', 'E' o 'H'**, el carácter de control **debe ser numérico**.
> - Si la clave es **'P', 'Q', 'R', 'S', 'W' o 'N'**, el control **debe ser una letra**.
> - Para otras letras, el carácter de control puede ser tanto numérico como alfabético.

*Ejemplo:* La letra **B** se utiliza para una sociedad de responsabilidad limitada y debe terminar como digito y no con caracter.

---

## 2. Los Siete Dígitos Centrales

A continuación se incluye un bloque de **7 dígitos** que conforman el número secuencial identificador.

---

## 3. Cálculo del Carácter de Control

El **último carácter** del NIF es el control, calculado a partir de los siete dígitos centrales según el siguiente procedimiento (según *Wikipedia, la Enciclopedia Libre*):

### Paso 1. Suma de Dígitos en Posiciones Pares

- Se suman los dígitos que ocupan las posiciones **pares** (segunda, cuarta y sexta) de los siete dígitos.

### Paso 2. Cálculo para Dígitos en Posiciones Impares

- Cada dígito en posición **impar** (primera, tercera, quinta y séptima) se multiplica por 2.
- Si el resultado es de dos cifras, se suman entre sí (por ejemplo, 16 → 1 + 6 = 7).
- Se suman todos los resultados obtenidos en este paso.

### Paso 3. Suma Total

- Se suman los resultados obtenidos en los pasos 1 y 2.

### Paso 4. Cálculo del Dígito de Control

- Se toma la **unidad** (último dígito) de la suma total obtenida.
- Se resta este dígito de **10**. El resultado es el valor del dígito de control.
- Si la unidad es 0, el dígito de control será **0**.

### Paso 5. Determinación del Carácter de Control

- **Dependiendo de la Clave Inicial:**
  - Si la letra inicial es **'P', 'Q', 'R', 'S', 'W' o 'N'**, el carácter de control será una letra.
  - Si la letra inicial es **'A', 'B', 'E' o 'H'**, el carácter de control será un número.
  - Para otras letras iniciales, el carácter de control puede ser tanto un número como una letra.

### Conversión a Letra (Si Corresponde)

Si el carácter de control ha de ser una letra, se utiliza la siguiente correspondencia:

| Dígito | Letra |
| ------ | ----- |
| 0      | J     |
| 1      | A     |
| 2      | B     |
| 3      | C     |
| 4      | D     |
| 5      | E     |
| 6      | F     |
| 7      | G     |
| 8      | H     |
| 9      | I     |

---

## Ejemplo Práctico

Supongamos un NIF para empresa con la siguiente información:

- **Clave Inicial:** A (indica una sociedad anónima).
- **Siete Dígitos Centrales:** 5881850

Realizamos el cálculo del carácter de control:

1. **Suma de Dígitos en Posiciones Pares:**  
   - Posiciones 2, 4 y 6: 8 + 1 + 5 = 14

2. **Cálculo para Dígitos en Posiciones Impares:**
   - Primera posición: 5 × 2 = 10 → 1 + 0 = 1  
   - Tercera posición: 8 × 2 = 16 → 1 + 6 = 7  
   - Quinta posición: 8 × 2 = 16 → 1 + 6 = 7  
   - Séptima posición: 0 × 2 = 0 → 0  
   - Suma de estos resultados: 1 + 7 + 7 + 0 = 15

3. **Suma Total:**  
   - 14 (pares) + 15 (impares) = 29

4. **Cálculo del Dígito de Control:**  
   - Última cifra de 29: 9  
   - 10 - 9 = 1

5. **Determinación del Carácter de Control:**  
   - Para la letra inicial **'A'**, el carácter de control debe ser un **número**.
  
Por lo tanto, el NIF completo sería: **A58818501**.

---

## Consideraciones Finales

- Asegúrate de que el NIF siga el formato preestablecido para evitar errores en la validación.
- Los algoritmos de cálculo para el dígito de control deben implementarse correctamente para garantizar la veracidad del NIF.
- Este método garantiza la validez y coherencia de los NIF asignados a las empresas.
- La conversión a letra (cuando corresponda) se realiza mediante la tabla de correspondencia mostrada anteriormente.

Este proceso es fundamental para el procesamiento y validación de datos fiscales en aplicaciones empresariales y sistemas de gestión.
