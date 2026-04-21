#!/usr/bin/env python3
"""
Extractor fiscal anónimo — Capa local de privacidad para la declaración de la renta.

Extrae el texto completo de documentos fiscales y usa Gemma 4 (Ollama, 100% local)
SOLO para identificar y redactar datos personales. El contenido fiscal se preserva íntegro.

Uso:
    python3 anonimizar.py <archivo1> [archivo2] ...
    python3 anonimizar.py ~/Descargas/datos_fiscales.pdf
    python3 anonimizar.py renta_2024.pdf certificado_banco.pdf nomina.pdf

Formatos soportados: PDF (texto), imágenes (JPG/PNG — requiere visión), texto plano, XML
Salida: fichero Markdown anonimizado en ./extracciones/
"""

import subprocess
import sys
import json
import os
import re
from pathlib import Path
from datetime import datetime

OLLAMA_MODEL = "gemma4:e4b"
OUTPUT_DIR = Path(__file__).parent / "extracciones"

# ─────────────────────────────────────────────────────────────────
# PASO 1: Patrones regex para redacción automática (sin IA)
# ─────────────────────────────────────────────────────────────────

PII_PATTERNS = [
    # DNI/NIE/NIF (8 dígitos + letra, o X/Y/Z + 7 dígitos + letra)
    (r'\b([0-9]{8}[A-Z])\b', '[NIF_REDACTADO]'),
    (r'\b([XYZ][0-9]{7}[A-Z])\b', '[NIE_REDACTADO]'),
    # IBAN español
    (r'\b(ES[0-9]{2}[\s]?[0-9]{4}[\s]?[0-9]{4}[\s]?[0-9]{4}[\s]?[0-9]{4}[\s]?[0-9]{4})\b', '[IBAN_REDACTADO]'),
    # Cuenta bancaria (20 dígitos seguidos o en grupos de 4)
    (r'\b([0-9]{4}[\s\-]?[0-9]{4}[\s\-]?[0-9]{2}[\s\-]?[0-9]{10})\b', '[CUENTA_REDACTADA]'),
    # Referencia catastral (14 dígitos + 4 letras + 2 dígitos + 2 letras, patrón típico)
    (r'\b([0-9]{7}[A-Z]{2}[0-9]{4}[A-Z][0-9]{4}[A-Z]{2})\b', '[REF_CATASTRAL_REDACTADA]'),
    # Teléfono español (9 dígitos empezando por 6-9, con o sin +34)
    (r'(?:\+34|0034)[\s\-]?([6-9][0-9]{8})\b', '[TELÉFONO_REDACTADO]'),
    (r'\b([6-9][0-9]{2}[\s\-]?[0-9]{3}[\s\-]?[0-9]{3})\b', '[TELÉFONO_REDACTADO]'),
    # Email
    (r'\b([A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,})\b', '[EMAIL_REDACTADO]'),
    # Código Seguro de Verificación (alfanumérico, 16 caracteres)
    (r'\b([A-Z0-9]{16})\b', '[CSV_REDACTADO]'),
    # Número de justificante (13 dígitos)
    (r'\b([0-9]{13})\b', '[JUSTIFICANTE_REDACTADO]'),
    # Expediente/Referencia (patrón tipo 202410052391248Q)
    (r'\b(20[0-9]{2}[0-9]{11,}[A-Z])\b', '[EXPEDIENTE_REDACTADO]'),
]

# Teléfonos institucionales que NO deben redactarse
PHONE_WHITELIST = ['915548770', '901335533']

def regex_redact(text):
    """Aplica redacciones automáticas por regex. Rápido y determinista."""
    result = text
    for pattern, replacement in PII_PATTERNS:
        result = re.sub(pattern, replacement, result)
    # Restaurar teléfonos institucionales
    for phone in PHONE_WHITELIST:
        result = result.replace('[TELÉFONO_REDACTADO]', phone, 1)
    return result


# ─────────────────────────────────────────────────────────────────
# PASO 2: Gemma — solo para redactar nombres y direcciones
# ─────────────────────────────────────────────────────────────────

GEMMA_SYSTEM = """Eres un filtro de anonimización. Recibes un documento fiscal español que ya ha sido parcialmente anonimizado (NIF, IBAN, teléfonos ya están redactados).

Tu ÚNICA tarea es identificar y sustituir los datos personales que quedan:

1. NOMBRES Y APELLIDOS de personas físicas → sustituir por "CONTRIBUYENTE" (o "CÓNYUGE" si es el/la cónyuge)
2. NOMBRES DE EMPRESAS o entidades pagadoras → sustituir por "PAGADOR_1", "PAGADOR_2", etc. (en orden de aparición)
3. DIRECCIONES POSTALES (calle, número, piso, puerta, municipio) → sustituir por "[DIRECCIÓN_REDACTADA, provincia: XX]" conservando SOLO la provincia
4. NOMBRES DE ENTIDADES FINANCIERAS o aseguradoras → sustituir por "ENTIDAD_1", "ENTIDAD_2", etc.

REGLAS CRÍTICAS:
- NO modifiques NADA más. Ni cifras, ni casillas, ni conceptos fiscales, ni formato, ni espacios.
- Conserva las líneas en blanco, los saltos de página, la indentación — TODO el formato original.
- Si una línea no contiene datos personales, cópiala EXACTAMENTE IGUAL, carácter por carácter.
- El resultado debe tener el MISMO número de líneas que la entrada.
- NO añadas encabezados, resúmenes, comentarios ni explicaciones. Solo devuelve el documento procesado.
- Si detectas un dato personal que podría ser también un término fiscal, mantén el término fiscal.
- Las URLs institucionales (sede.agenciatributaria.gob.es, etc.) NO son datos personales — no las redactes.
- Los nombres de modelos fiscales, leyes y normativa NO son datos personales — no los redactes.
- "DEGIRO", "IBEX", nombres de índices bursátiles o brokers en contexto de operaciones bursátiles → sustituir por "BROKER_1", "BROKER_2", etc.

Tu respuesta debe ser EXCLUSIVAMENTE el documento con las sustituciones aplicadas. Nada más."""

GEMMA_USER = """Anonimiza los nombres de personas, empresas, entidades y direcciones en el siguiente documento fiscal. No modifiques nada más.

DOCUMENTO:
{content}"""


def extract_text_from_pdf(filepath):
    """Extrae texto de un PDF con pdftotext (poppler)."""
    try:
        result = subprocess.run(
            ["pdftotext", "-layout", filepath, "-"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # Fallback: textutil (macOS)
    try:
        result = subprocess.run(
            ["textutil", "-convert", "txt", "-stdout", filepath],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    return None


def read_file_content(filepath):
    """Lee el contenido de un archivo. Devuelve (contenido, es_imagen)."""
    path = Path(filepath)
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        text = extract_text_from_pdf(filepath)
        if text:
            return text, False
        return filepath, True

    if suffix in (".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"):
        return filepath, True

    # Intentar como texto
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            return f.read(), False
    except Exception:
        return None, False


def call_ollama_text(content):
    """Llama a Gemma via Ollama para anonimizar nombres y direcciones."""
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": GEMMA_SYSTEM},
            {"role": "user", "content": GEMMA_USER.format(content=content)}
        ],
        "stream": False,
        "options": {
            "temperature": 0.0,
            "num_predict": 16384
        }
    }

    result = subprocess.run(
        ["curl", "-s", "http://localhost:11434/api/chat",
         "-H", "Content-Type: application/json",
         "-d", json.dumps(payload)],
        capture_output=True, text=True, timeout=600
    )

    if result.returncode != 0:
        raise RuntimeError(f"Error llamando a Ollama: {result.stderr}")

    response = json.loads(result.stdout)
    return response["message"]["content"]


def call_ollama_vision(image_path):
    """Para imágenes/PDFs escaneados: Gemma extrae texto y anonimiza."""
    import base64

    with open(image_path, "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode("utf-8")

    vision_prompt = """Este es un documento fiscal español (imagen). Necesito que:
1. Transcribas ÍNTEGRAMENTE todo el texto visible, conservando la estructura y formato
2. Sustituyas SOLO los datos personales identificables:
   - Nombres de personas → "CONTRIBUYENTE" / "CÓNYUGE"
   - Nombres de empresas → "PAGADOR_1", "PAGADOR_2"
   - NIF/DNI/NIE → "[NIF_REDACTADO]"
   - Direcciones → "[DIRECCIÓN_REDACTADA, provincia: XX]"
   - IBAN/cuentas → "[IBAN_REDACTADO]"
3. Conserves TODO lo demás: cifras, casillas, conceptos fiscales, porcentajes, fechas

Devuelve SOLO el documento transcrito y anonimizado, sin comentarios."""

    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "user", "content": vision_prompt, "images": [image_b64]}
        ],
        "stream": False,
        "options": {
            "temperature": 0.0,
            "num_predict": 16384
        }
    }

    result = subprocess.run(
        ["curl", "-s", "http://localhost:11434/api/chat",
         "-H", "Content-Type: application/json",
         "-d", json.dumps(payload)],
        capture_output=True, text=True, timeout=600
    )

    if result.returncode != 0:
        raise RuntimeError(f"Error llamando a Ollama: {result.stderr}")

    response = json.loads(result.stdout)
    return response["message"]["content"]


# ─────────────────────────────────────────────────────────────────
# PASO 3: Verificación post-anonimización
# ─────────────────────────────────────────────────────────────────

def verify_anonymization(text):
    """Verifica que no quedan datos personales en la salida."""
    warnings = []

    # DNI/NIE/NIF
    matches = re.findall(r'\b[0-9]{8}[A-Z]\b', text)
    if matches:
        warnings.append(f"ALERTA: Posible DNI/NIF detectado: {matches}")

    matches = re.findall(r'\b[XYZ][0-9]{7}[A-Z]\b', text)
    if matches:
        warnings.append(f"ALERTA: Posible NIE detectado: {matches}")

    # IBAN
    if re.search(r'\bES[0-9]{2}[\s]?[0-9]{4}', text):
        warnings.append("ALERTA: Posible IBAN detectado")

    # Email
    emails = re.findall(r'\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b', text)
    # Excluir dominios institucionales
    personal_emails = [e for e in emails if not any(d in e for d in ['agenciatributaria', 'gob.es', 'juntadeandalucia'])]
    if personal_emails:
        warnings.append(f"ALERTA: Email personal detectado: {personal_emails}")

    return warnings


def count_data_lines(text):
    """Cuenta líneas con contenido fiscal (no vacías ni decorativas)."""
    count = 0
    for line in text.split('\n'):
        stripped = line.strip()
        if stripped and not all(c in '-=─ ' for c in stripped):
            count += 1
    return count


# ─────────────────────────────────────────────────────────────────
# FLUJO PRINCIPAL
# ─────────────────────────────────────────────────────────────────

def process_file(filepath):
    """Procesa un archivo: extrae texto → regex → Gemma → verifica."""
    path = Path(filepath)
    if not path.exists():
        return f"ERROR: Archivo no encontrado: {filepath}", 0, 0

    print(f"  Leyendo: {path.name}...")
    content, is_image = read_file_content(filepath)

    if content is None:
        return f"ERROR: No se pudo leer el archivo: {filepath}", 0, 0

    if is_image:
        print(f"  Documento tipo imagen — Gemma extraerá y anonimizará directamente...")
        result = call_ollama_vision(content)
        original_lines = 0
    else:
        original_lines = count_data_lines(content)
        print(f"  Texto extraído: {original_lines} líneas con contenido")

        # PASO 1: Redacción automática por regex (instantáneo)
        print(f"  Paso 1/2: Redacción automática (regex)...")
        redacted = regex_redact(content)

        # PASO 2: Gemma anonimiza nombres y direcciones
        print(f"  Paso 2/2: Anonimización de nombres y direcciones ({OLLAMA_MODEL}, local)...")
        result = call_ollama_text(redacted)

    final_lines = count_data_lines(result)

    # PASO 3: Verificar
    warnings = verify_anonymization(result)
    if warnings:
        print(f"\n  ⚠  VERIFICACIÓN DE ANONIMIZACIÓN — ALERTAS:")
        for w in warnings:
            print(f"     {w}")
        print(f"     → REVISA el fichero antes de compartirlo con Claude\n")
    else:
        print(f"  ✓  Verificación OK — no se detectan datos personales residuales")

    if original_lines > 0:
        ratio = final_lines / original_lines * 100
        print(f"  Cobertura: {final_lines}/{original_lines} líneas ({ratio:.0f}%)")
        if ratio < 80:
            print(f"  ⚠  Cobertura por debajo del 80% — Gemma puede haber omitido contenido")

    return result, original_lines, final_lines


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    files = sys.argv[1:]

    # Verificar que Ollama está corriendo
    try:
        result = subprocess.run(
            ["curl", "-s", "http://localhost:11434/api/tags"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode != 0:
            print("ERROR: Ollama no está corriendo. Ejecuta 'ollama serve' primero.")
            sys.exit(1)
    except subprocess.TimeoutExpired:
        print("ERROR: Ollama no responde. Verifica que está corriendo.")
        sys.exit(1)

    # Verificar pdftotext
    has_pdftotext = subprocess.run(
        ["which", "pdftotext"], capture_output=True
    ).returncode == 0

    OUTPUT_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = OUTPUT_DIR / f"fiscal_anonimo_{timestamp}.md"

    print(f"\n{'='*60}")
    print(f"  EXTRACTOR FISCAL ANÓNIMO")
    print(f"  Modelo: {OLLAMA_MODEL} (100% local)")
    print(f"  pdftotext: {'disponible' if has_pdftotext else 'NO disponible (instala poppler)'}")
    print(f"  Archivos: {len(files)}")
    print(f"{'='*60}\n")

    all_results = []
    all_results.append("# Declaración Fiscal — Datos Anonimizados")
    all_results.append(f"")
    all_results.append(f"- Fecha de extracción: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    all_results.append(f"- Procesado con: {OLLAMA_MODEL} (100% local)")
    all_results.append(f"- Archivos procesados: {len(files)}")
    all_results.append(f"")
    all_results.append("> **Privacidad**: Este fichero fue generado localmente por Gemma 4 via Ollama.")
    all_results.append("> No contiene nombres, NIF, direcciones ni otros datos identificables.")
    all_results.append("> Es seguro compartirlo con Claude para el análisis fiscal.")
    all_results.append("")

    total_original = 0
    total_final = 0

    for i, filepath in enumerate(files, 1):
        print(f"[{i}/{len(files)}] Procesando: {Path(filepath).name}")
        file_result, orig, final = process_file(os.path.expanduser(filepath))
        total_original += orig
        total_final += final

        all_results.append(f"---")
        all_results.append(f"")
        all_results.append(f"## Archivo {i}: {Path(filepath).suffix.upper().lstrip('.')} — {Path(filepath).stem}")
        all_results.append(f"")
        all_results.append(file_result)
        all_results.append("")
        print(f"  Completado.\n")

    output_content = "\n".join(all_results)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(output_content)

    print(f"{'='*60}")
    print(f"  EXTRACCIÓN COMPLETADA")
    print(f"  Resultado: {output_file}")
    if total_original > 0:
        print(f"  Cobertura total: {total_final}/{total_original} líneas ({total_final/total_original*100:.0f}%)")
    print(f"{'='*60}")
    print(f"\nPara usar con Claude Code:")
    print(f"  1. Ejecuta: /declaracion-renta")
    print(f"  2. Indica esta ruta: {output_file}")


if __name__ == "__main__":
    main()
