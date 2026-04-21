# Ejemplo de sesión con Claude Code

> Este es un ejemplo ficticio que muestra cómo Claude Code analiza
> los datos anonimizados y guía al contribuyente paso a paso.
> Todos los datos son inventados.

---

## 1. El contribuyente activa el skill y comparte sus datos anonimizados

```
> /declaracion-renta
> Aquí tienes mis datos anonimizados: ./extracciones/fiscal_anonimo.md
```

## 2. Claude genera el Mapa Fiscal

```
════════════════════════════════════════
         MAPA FISCAL — CONTRIBUYENTE
         Ejercicio 2025 | Andalucía
════════════════════════════════════════

RENTAS
├── Trabajo personal ............. €32.000,00
├── Capital mobiliario ........... €425,30
├── Capital inmobiliario ......... €0,00
├── Actividades económicas ....... €0,00
├── Ganancias patrimoniales ...... €0,00
└── RENTA TOTAL .................. €32.425,30

RETENCIONES YA PRACTICADAS
├── Trabajo ...................... €4.800,00
├── Capital ...................... €80,81
└── TOTAL RETENCIONES ............ €4.880,81

SITUACIÓN FAMILIAR
├── Declaración: individual
├── Mínimo personal: €5.550
├── Mínimo por descendientes: €2.400 (1 hijo < 3 años: €4.650)
└── Mínimo por discapacidad: €0
```

## 3. Claude calcula la liquidación base

```
════════════════════════════════════════
         LIQUIDACIÓN IRPF 2025
════════════════════════════════════════

Base imponible general:            €27.574,70
Base imponible del ahorro:            €425,30
Reducción plan pensiones:          -€1.500,00
Base liquidable general:           €26.074,70
Base liquidable del ahorro:           €425,30

Cuota íntegra estatal:              €2.487,12
Cuota íntegra autonómica:          €2.453,67
Cuota íntegra total:                €4.940,79

Deducciones:
├── Deducción maternidad:          -€1.200,00
├── Deducción alquiler (Andalucía): -€500,00
├── Deducción deporte (Andalucía):   -€45,00
└── Total deducciones:             -€1.745,00

Cuota líquida:                      €3.195,79
Retenciones:                       -€4.880,81

RESULTADO: A DEVOLVER €1.685,02
════════════════════════════════════════
```

## 4. Claude encuentra optimizaciones

```
════════════════════════════════════════
      PROPUESTA DE OPTIMIZACIÓN
════════════════════════════════════════

RESULTADO SIN OPTIMIZAR: A devolver €985,02

OPTIMIZACIÓN #1: Deducción por alquiler de vivienda habitual
  ├── Qué: Deducción autonómica del 15% del alquiler
  ├── Base legal: Decreto-ley Andalucía, art. 1.1
  ├── Ahorro estimado: €500
  └── Requisitos: Base imponible < €25.000 (individual)
       ⚠ Tu base es €27.574 — NO APLICA (superas el límite)

OPTIMIZACIÓN #2: Deducción por práctica deportiva
  ├── Qué: 15% de cuotas de gimnasio
  ├── Base legal: Ley IRPF Andalucía
  ├── Ahorro estimado: €45
  └── Requisitos: Factura con NIF del gimnasio

OPTIMIZACIÓN #3: Aportación a plan de pensiones
  ├── Qué: Aportar €1.500 al plan de pensiones
  ├── Base legal: Art. 52 LIRPF
  ├── Ahorro estimado: €450 (al tipo marginal del 30%)
  └── Requisitos: Hacer la aportación antes del 31/12

OPTIMIZACIÓN #4: Donativo a ONG
  ├── Qué: Donar €250 a una entidad acogida a Ley 49/2002
  ├── Base legal: Art. 68.3 LIRPF
  ├── Ahorro estimado: €200 (80% sobre los primeros €250)
  └── Requisitos: Certificado de donación

────────────────────────────────────────
RESULTADO OPTIMIZADO: A devolver €1.685,02
AHORRO TOTAL: €700
════════════════════════════════════════
```

## 5. Claude guía paso a paso en Renta Web

```
PASO 1 — Verifica los rendimientos del trabajo
  → Casilla 0003: debe mostrar €32.000,00
  → Casilla 0596: retenciones €4.800,00

PASO 2 — Añade los intereses bancarios
  → Casilla 0027: €425,30
  → Retenciones: €80,81

PASO 3 — Aplica la deducción de deporte
  → Sección: Deducciones autonómicas de Andalucía
  → NIF del gimnasio: [el que corresponda]
  → Importe: €300,00 (cuota anual)
  → Deducción calculada: €45,00

PASO 4 — Verifica el resultado
  → Casilla 0670: debe mostrar -€1.685,02 (a devolver)
```

## 6. Comparativa interanual

```
════════════════════════════════════════════════════════════════
          EVOLUCIÓN PATRIMONIAL 2024 → 2025
════════════════════════════════════════════════════════════════

                              2024          2025           Δ
─────────────────────────────────────────────────────────────
Salario bruto            €30.000,00    €32.000,00    +€2.000
Capital mobiliario          €310,50       €425,30      +€115
Tipo efectivo               14,2%         15,2%      +1,0 pp
Resultado               -€1.420,00    -€1.685,02      -€265
════════════════════════════════════════════════════════════════
```

---

> **Nota**: Este ejemplo usa datos ficticios con un salario más bajo para
> ilustrar cómo algunas deducciones autonómicas tienen límites de renta.
> La herramienta se adapta automáticamente a cualquier nivel de ingresos
> y situación personal.
