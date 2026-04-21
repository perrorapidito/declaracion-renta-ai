# Declaracion Renta AI

**Usa Cloud Code para la declaracion de la renta (IRPF) en Espana. Privacidad total: tus datos personales nunca salen de tu ordenador.**

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org)
[![Ollama](https://img.shields.io/badge/Ollama-Local_AI-purple.svg)](https://ollama.com)
[![Claude Code](https://img.shields.io/badge/Claude_Code-Skill-orange.svg)](https://claude.ai/code)

---

## El problema

Hacer la declaracion de la renta es complejo. Hay deducciones que no conoces, casillas que no entiendes, y datos repartidos entre 5 bancos distintos. Contratar un asesor fiscal cuesta entre 60 y 200 euros, y las herramientas online te obligan a subir todos tus datos personales a sus servidores.

## La solucion

Declaracion Renta AI combina dos capas de IA para darte asesoramiento fiscal de nivel profesional **sin comprometer tu privacidad**:

```
TUS DOCUMENTOS                    TU ORDENADOR                     LA NUBE
(nominas, certificados,     -->   Gemma 4 (Ollama)           -->   Claude (API)
 datos fiscales AEAT)             Extrae y anonimiza               Analiza y optimiza
                                  100% LOCAL                       Solo ve cifras
                                  Tus datos NO salen               Sin datos personales
```

### Arquitectura de privacidad

| Capa | Donde se ejecuta | Que hace | Datos personales |
|------|-------------------|----------|------------------|
| **Capa 1** - Gemma 4 | Tu ordenador (Ollama) | Extrae texto de PDFs y anonimiza nombres, NIF, direcciones, IBAN | **SI los ve**, pero nunca salen de tu maquina |
| **Capa 2** - Claude | API de Anthropic | Analiza cifras, calcula impuestos, encuentra deducciones | **NUNCA los ve** - solo recibe datos anonimizados |

## Que hace

- **Mapa fiscal completo**: Consolida informacion de todos tus bancos y brokers en un solo cuadro
- **Liquidacion del IRPF**: Calcula tu declaracion paso a paso siguiendo el esquema oficial
- **Auditoria de optimizacion**: Revisa 18+ deducciones autonomicas (Andalucia) y todas las estatales
- **Guia paso a paso**: Te indica exactamente que casillas modificar en Renta Web
- **Comparativa interanual**: Analiza como ha evolucionado tu patrimonio respecto al ejercicio anterior

### Deducciones que revisa automaticamente

<details>
<summary><strong>Deducciones autonomicas de Andalucia (18)</strong></summary>

1. Inversion en vivienda habitual protegida
2. Alquiler de vivienda habitual (hasta 1.200 euros)
3. Mejora de la sostenibilidad de la vivienda habitual
4. Nacimiento, adopcion o acogimiento
5. Adopcion internacional de menores
6. Familia numerosa
7. Familia monoparental
8. Ascendientes mayores de 75 anos
9. Personas con discapacidad
10. Asistencia a personas con discapacidad
11. Ayuda domestica
12. Inversion en acciones/participaciones de sociedades
13. Gastos de defensa juridica laboral
14. Donativos con finalidad ecologica
15. Donativos a entidades para I+D+i
16. Practica deportiva (15%, hasta 100 euros)
17. Gastos veterinarios de animales de compania
18. Celiaquia

</details>

<details>
<summary><strong>Deducciones estatales</strong></summary>

- Inversion en vivienda habitual (regimen transitorio pre-2013)
- Donativos a entidades acogidas a la Ley 49/2002
- Inversion en empresas de nueva creacion
- Maternidad
- Familia numerosa / personas con discapacidad a cargo
- Obras de mejora de eficiencia energetica
- Vehiculo electrico e infraestructura de recarga
- Planes de pensiones y sistemas de prevision social

</details>

## Requisitos

- **Python 3.9+**
- **[Ollama](https://ollama.com)** con el modelo Gemma 4
- **[Claude Code](https://claude.ai/code)** (CLI, desktop o web)
- **poppler** (para `pdftotext`)

## Instalacion

### 1. Instala las dependencias

```bash
# macOS
brew install ollama poppler

# Linux (Ubuntu/Debian)
sudo apt install poppler-utils
curl -fsSL https://ollama.com/install.sh | sh
```

### 2. Descarga el modelo Gemma 4

```bash
ollama pull gemma4:e4b
```

### 3. Clona este repositorio

```bash
git clone https://github.com/perrorapidito/declaracion-renta-ai.git
cd declaracion-renta-ai
```

### 4. Instala el skill en Claude Code

```bash
# Copia el skill a tu directorio de skills de Claude Code
mkdir -p ~/.claude/skills/declaracion-renta
cp SKILL.md ~/.claude/skills/declaracion-renta/SKILL.md
cp anonimizar.py ~/.claude/skills/declaracion-renta/anonimizar.py
```

Luego anade el skill a tu configuracion de Claude Code (`~/.claude/settings.json`):

```json
{
  "skills": {
    "declaracion-renta": {
      "path": "~/.claude/skills/declaracion-renta/SKILL.md"
    }
  }
}
```

## Uso

### Paso 1: Anonimiza tus documentos

```bash
# Un solo documento
python3 anonimizar.py ~/Descargas/datos_fiscales.pdf

# Varios documentos a la vez
python3 anonimizar.py ~/Descargas/nomina.pdf ~/Descargas/certificado_banco.pdf ~/Descargas/borrador.pdf
```

El script genera un fichero Markdown anonimizado en `./extracciones/`. Este fichero es **seguro para compartir** con Claude.

### Paso 2: Activa el skill en Claude Code

```
/declaracion-renta
```

### Paso 3: Comparte el fichero anonimizado

Indica la ruta del fichero generado y Claude te guiara paso a paso por toda la declaracion.

## Ejemplos

En la carpeta [`examples/`](examples/) encontraras:

| Archivo | Que muestra |
|---------|-------------|
| [`ejemplo_documento_original.txt`](examples/ejemplo_documento_original.txt) | Como se ve un documento fiscal **antes** de anonimizar (datos ficticios) |
| [`ejemplo_documento_anonimizado.md`](examples/ejemplo_documento_anonimizado.md) | El **mismo documento despues** de pasar por el script — sin datos personales |
| [`ejemplo_sesion_claude.md`](examples/ejemplo_sesion_claude.md) | Una **sesion completa** con Claude: mapa fiscal, liquidacion, optimizaciones y guia paso a paso |

## Ejemplo rapido

```
$ python3 anonimizar.py ~/Descargas/borrador_renta_2025.pdf

============================================================
  EXTRACTOR FISCAL ANONIMO
  Modelo: gemma4:e4b (100% local)
  pdftotext: disponible
  Archivos: 1
============================================================

[1/1] Procesando: borrador_renta_2025.pdf
  Texto extraido: 299 lineas con contenido
  Paso 1/2: Redaccion automatica (regex)...
  Paso 2/2: Anonimizacion de nombres y direcciones (gemma4:e4b, local)...
  Verificacion OK - no se detectan datos personales residuales
  Cobertura: 298/299 lineas (100%)

============================================================
  EXTRACCION COMPLETADA
  Resultado: ./extracciones/fiscal_anonimo_20260420_201250.md
============================================================
```

Luego en Claude Code:

```
> /declaracion-renta
> Aqui tienes mi borrador anonimizado: ./extracciones/fiscal_anonimo_20260420_201250.md

Claude analiza tu borrador y te dice:
- Que deducciones te faltan
- Que casillas hay que corregir
- Cuanto puedes ahorrarte
- Paso a paso como hacerlo en Renta Web
```

## Como funciona la anonimizacion

El script aplica un proceso de dos pasos:

### Paso 1: Regex (instantaneo, determinista)
Detecta y redacta automaticamente patrones conocidos:
- NIF/DNI/NIE
- IBAN y cuentas bancarias
- Telefonos personales
- Emails
- Referencias catastrales
- Codigos seguros de verificacion

### Paso 2: Gemma 4 (IA local)
Solo se encarga de lo que las regex no pueden detectar:
- Nombres y apellidos de personas
- Nombres de empresas y entidades
- Direcciones postales completas

### Paso 3: Verificacion automatica
Despues de la anonimizacion, el script verifica que no quedan datos personales residuales.

## Formatos soportados

| Formato | Metodo de extraccion |
|---------|---------------------|
| PDF (con texto) | `pdftotext` (poppler) |
| PDF (escaneado) | Gemma 4 vision |
| Imagenes (JPG, PNG) | Gemma 4 vision |
| Texto plano | Lectura directa |
| XML | Lectura directa |

## Limitaciones

- **Solo Andalucia**: Las deducciones autonomicas estan configuradas para Andalucia. Se pueden adaptar a otras comunidades editando el SKILL.md.
- **Ejercicio 2025**: Las escalas y deducciones estan actualizadas para el ejercicio 2025. Se actualizaran anualmente.
- **No es asesoramiento profesional**: Esta herramienta es una ayuda, no sustituye al criterio de un asesor fiscal colegiado. Consulta con un profesional ante dudas sobre tu situacion particular.
- **Documentos muy largos**: Gemma 4 tiene un limite de contexto. Documentos de mas de ~1500 lineas pueden requerir procesamiento directo con regex (sin Gemma).

## Contribuir

Las contribuciones son bienvenidas. Algunas ideas:

- [ ] Anadir deducciones autonomicas de otras comunidades (Madrid, Cataluna, Valencia, etc.)
- [ ] Soporte para declaracion conjunta
- [ ] Integracion con datos abiertos de la AEAT
- [ ] Mejorar la extraccion de PDFs escaneados
- [ ] Tests automatizados con documentos de ejemplo anonimizados
- [ ] Soporte para actividades economicas (autonomos)

## Disclaimer

> **Esta herramienta no constituye asesoramiento fiscal profesional.** Los calculos y recomendaciones son orientativos. El contribuyente es el unico responsable de la veracidad y correccion de su declaracion de la renta. Ante cualquier duda sobre tu situacion fiscal particular, consulta con un asesor fiscal colegiado. Los creadores de esta herramienta no se responsabilizan de errores, omisiones o perjuicios derivados de su uso.

## Licencia

[MIT](LICENSE) - Usa, modifica y distribuye libremente.

---

Hecho con Claude Code + Gemma 4 | Privacidad por diseno
