---
description: Validación y limpieza de datos extraídos por scrapers
---

# Skill: Validación de Datos

## Cuándo usar

- Después de extraer datos con IA
- Antes de guardar resultados finales
- Al detectar datos inconsistentes

---

## Reglas de Validación

### 1. Emails

**Regex estándar:**

```python
import re

EMAIL_PATTERN = re.compile(
    r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
)

def es_email_valido(email: str) -> bool:
    if not email:
        return False

    # Limpiar espacios
    email = email.strip().lower()

    # Validar formato
    if not EMAIL_PATTERN.match(email):
        return False

    # Rechazar dominios sospechosos
    dominios_invalidos = ['example.com', 'test.com', 'localhost']
    dominio = email.split('@')[1]

    return dominio not in dominios_invalidos
```

**Priorización de dominios:**

```python
def priorizar_emails(emails: List[str], dominio_municipio: str) -> str:
    """Selecciona el mejor email de una lista"""

    # 1. Preferir email del dominio del municipio
    for email in emails:
        if dominio_municipio in email:
            return email

    # 2. Evitar genéricos (gmail, hotmail) si hay otros
    emails_institucionales = [e for e in emails
                             if not any(d in e for d in ['gmail', 'hotmail', 'yahoo'])]

    if emails_institucionales:
        return emails_institucionales[0]

    # 3. Retornar primero disponible
    return emails[0] if emails else None
```

---

### 2. Nombres

**Reglas:**

- Longitud mínima: 3 caracteres
- Longitud máxima: 100 caracteres
- No debe ser solo números
- Capitalización correcta

```python
def validar_nombre(nombre: str) -> tuple[bool, str]:
    """Valida y normaliza un nombre"""

    if not nombre:
        return False, "Nombre vacío"

    nombre = nombre.strip()

    # Longitud
    if len(nombre) < 3:
        return False, "Nombre muy corto"

    if len(nombre) > 100:
        return False, "Nombre muy largo"

    # No solo números
    if nombre.isdigit():
        return False, "Nombre es solo números"

    # Normalizar capitalización
    nombre_normalizado = capitalizar_nombre(nombre)

    return True, nombre_normalizado


def capitalizar_nombre(nombre: str) -> str:
    """Capitaliza correctamente nombres españoles"""

    # Excepciones que no se capitalizan
    excepciones = {
        'de', 'del', 'la', 'las', 'el', 'los',
        'y', 'e', 'o', 'u'
    }

    palabras = nombre.split()
    resultado = []

    for i, palabra in enumerate(palabras):
        # Primera palabra siempre capitalizada
        # Excepciones solo en medio del nombre
        if i == 0 or palabra.lower() not in excepciones:
            resultado.append(palabra.capitalize())
        else:
            resultado.append(palabra.lower())

    return ' '.join(resultado)


# Ejemplos:
# "JUAN PÉREZ" → "Juan Pérez"
# "maría de los angeles" → "María de los Angeles"
# "D. JOSÉ DEL VALLE" → "D. José del Valle"
```

---

### 3. Cargos

**Lista de cargos conocidos:**

```python
CARGOS_VALIDOS = {
    'alcalde': 'Alcalde',
    'alcaldesa': 'Alcaldesa',
    'concejal': 'Concejal',
    'concejala': 'Concejala',
    'teniente alcalde': 'Teniente de Alcalde',
    'teniente alcaldesa': 'Teniente de Alcaldesa',
    'primera tenencia': 'Primera Tenencia de Alcaldía',
    'segunda tenencia': 'Segunda Tenencia de Alcaldía',
    'tercera tenencia': 'Tercera Tenencia de Alcaldía',
    'concejal delegado': 'Concejal Delegado',
    'concejala delegada': 'Concejala Delegada'
}

def normalizar_cargo(cargo: str) -> str:
    """Normaliza un cargo a formato estándar"""

    if not cargo:
        return None

    cargo_lower = cargo.lower().strip()

    # Buscar en diccionario
    for key, valor in CARGOS_VALIDOS.items():
        if key in cargo_lower:
            return valor

    # Si no está en diccionario, capitalizar
    return cargo.title()
```

---

### 4. Partidos Políticos

**Lista de siglas conocidas:**

```python
PARTIDOS_VALIDOS = {
    'pp': 'PP',
    'psoe': 'PSOE',
    'cc': 'CC',
    'nc': 'NC',
    'podemos': 'Podemos',
    'iu': 'IU',
    'vox': 'VOX',
    'cs': 'Cs',
    'ciudadanos': 'Ciudadanos',
    'nueva canarias': 'NC',
    'coalición canaria': 'CC',
    'partido popular': 'PP',
    'partido socialista': 'PSOE'
}

def normalizar_partido(partido: str) -> str:
    """Normaliza siglas de partidos"""

    if not partido:
        return None

    partido_lower = partido.lower().strip()

    # Buscar en diccionario
    for key, valor in PARTIDOS_VALIDOS.items():
        if partido_lower == key or key in partido_lower:
            return valor

    # Si no está, devolver original en mayúsculas
    return partido.upper()
```

---

## Limpieza de Texto OCR

### Errores Comunes de OCR

```python
def limpiar_ocr(texto: str) -> str:
    """Corrige errores comunes de OCR"""

    # Reemplazos comunes
    correcciones = {
        '|': 'I',      # Barra vertical → I
        '0': 'O',      # Cero → O (en nombres)
        'l': 'I',      # L minúscula → I (en siglas)
        '1': 'I',      # Uno → I (en siglas)
        '©': 'e',      # Símbolo copyright → e
        '®': 'o',      # Símbolo registered → o
    }

    resultado = texto
    for incorrecto, correcto in correcciones.items():
        # Solo reemplazar en contextos específicos
        resultado = resultado.replace(incorrecto, correcto)

    # Remover saltos de línea extraños
    resultado = re.sub(r'\n+', ' ', resultado)

    # Remover espacios múltiples
    resultado = re.sub(r'\s+', ' ', resultado)

    return resultado.strip()


def fusionar_lineas_partidas(texto: str) -> str:
    """Fusiona líneas que fueron partidas incorrectamente"""

    lineas = texto.split('\n')
    resultado = []
    buffer = ''

    for linea in lineas:
        # Si termina en guion, es continuación
        if linea.endswith('-'):
            buffer += linea[:-1]  # Remover guion
        # Si es muy corta y no empieza con mayúscula, es continuación
        elif buffer and len(linea) < 30 and not linea[0].isupper():
            buffer += ' ' + linea
        else:
            if buffer:
                resultado.append(buffer)
            buffer = linea

    if buffer:
        resultado.append(buffer)

    return '\n'.join(resultado)
```

---

## Validación Completa de Registro

```python
from typing import Tuple, List

def validar_registro(registro: Dict) -> Tuple[bool, List[str]]:
    """Valida un registro completo y retorna errores"""

    errores = []

    # 1. Validar nombre
    if 'nombre' in registro:
        valido, mensaje = validar_nombre(registro['nombre'])
        if not valido:
            errores.append(f"Nombre inválido: {mensaje}")
        else:
            registro['nombre'] = mensaje  # Nombre normalizado
    else:
        errores.append("Falta campo 'nombre'")

    # 2. Validar email (opcional)
    if 'email' in registro and registro['email']:
        if not es_email_valido(registro['email']):
            errores.append(f"Email inválido: {registro['email']}")

    # 3. Normalizar cargo
    if 'cargo' in registro and registro['cargo']:
        registro['cargo'] = normalizar_cargo(registro['cargo'])

    # 4. Normalizar partido
    if 'partido' in registro and registro['partido']:
        registro['partido'] = normalizar_partido(registro['partido'])

    # 5. Validar tipo
    if 'tipo' not in registro:
        # Inferir tipo
        if registro.get('partido'):
            registro['tipo'] = 'Persona'
        else:
            registro['tipo'] = 'Organización/Departamento'

    return len(errores) == 0, errores
```

---

## Pipeline de Validación

```python
def validar_dataset_completo(registros: List[Dict]) -> Dict:
    """Valida un dataset completo y genera reporte"""

    validos = []
    invalidos = []

    for i, registro in enumerate(registros):
        es_valido, errores = validar_registro(registro)

        if es_valido:
            validos.append(registro)
        else:
            invalidos.append({
                'index': i,
                'registro': registro,
                'errores': errores
            })

    # Reporte
    reporte = {
        'total': len(registros),
        'validos': len(validos),
        'invalidos': len(invalidos),
        'tasa_exito': len(validos) / len(registros) * 100 if registros else 0,
        'registros_validos': validos,
        'registros_invalidos': invalidos
    }

    return reporte
```

---

## Ejemplos de Uso

### Validar resultado de scraping

```python
# Después de extraer con IA
raw_data = ai_extractor.extract(html)

# Validar
reporte = validar_dataset_completo(raw_data)

logger.info(f"Validación: {reporte['validos']}/{reporte['total']} válidos ({reporte['tasa_exito']:.1f}%)")

# Loggear errores
for invalido in reporte['registros_invalidos']:
    logger.warning(f"Registro {invalido['index']} inválido: {invalido['errores']}")

# Guardar solo válidos
guardar_resultados(reporte['registros_validos'])
```

### Limpiar datos de OCR

```python
# Texto extraído de OCR
texto_ocr = extract_text_from_image(image_url)

# Limpiar
texto_limpio = limpiar_ocr(texto_ocr)
texto_fusionado = fusionar_lineas_partidas(texto_limpio)

# Extraer con IA
registros = ai_extractor.extract(texto_fusionado)

# Validar
reporte = validar_dataset_completo(registros)
```

---

## Referencias

- `core/validator.py` - Implementación de validadores
- `core/ai_extractor.py` - Extracción con IA
- `scrapers/ocr_scraper.py` - OCR con limpieza
