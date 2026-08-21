# ===== ARCHIVO 2: src/semana03_taxonomia.py =====
from dataclasses import dataclass
from pathlib import Path
import csv
import re
import unicodedata
ROOT = Path(__file__).resolve().parent.parent
CSV_FILE = ROOT / "data" / "casos_ia.csv"
REPORT_FILE = ROOT / "reports" / "semana03.md"


@dataclass(frozen=True)
class Category:
    name: str
    keywords: tuple[str, ...]


CATEGORIES = [
    Category("Visión por computador", (
        "imagen", "imagenes", "foto", "fotografia", "fotografias", "camara",
        "rostro", "rostros", "peaton", "peatones", "senal", "senales", "vehiculos", 
        "vehiculo","camara", "camaras"
    )),
    Category("Procesamiento de lenguaje natural", (
        "texto", "comentario", "comentarios", "correo", "correos", "chatbot",
        "contrato", "contratos", "nombres", "lenguaje"
    )),
    Category("Aprendizaje automático predictivo", (
        "predecir", "probabilidad", "demanda", "fraude", "fraudes", "sensores"
    )),
    Category("Sistemas de recomendación", (
        "recomendar", "preferencias", "historial de visualizacion", "sugerir"
    )),
    Category("Búsqueda y optimización", (
        "ruta", "rutas", "horario", "horarios", "combinacion optima",
        "optimizar", "capacidad maxima"
    )),
    Category("Sistemas expertos", (
        "diagnostico", "diagnosticos", "reglas", "politicas", "solicitud de credito"
    )),
    Category("Robótica y sistemas autónomos", (
        "robot", "robots", "dron", "drones", "vehiculo autonomo", "obstaculos"
    )),
]
# Cinco reglas de ejemplo. Cada estudiante debe reemplazarlas o ampliarlas
# con cinco reglas propias y justificar el cambio en reports/semana03.md.
CUSTOM_RULES = {
    "Visión por computador": (
        "matricula", "matriculas",
        "vehiculo", "vehiculos",
        "rostro", "rostros",
        "camara", "camaras",
        "imagen", "imagenes",
        "peaton", "peatones",
        "señal", "señales"
    ),
    "Procesamiento de lenguaje natural": (
        "sentimiento",
        "chatbot",
        "correo",
        "spam",
        "contrato",
        "entidades"
    ),
    "Aprendizaje automático predictivo": (
        "falla", "fallas",
        "fraude", "fraudes",
        "demanda",
        "abandono",
        "prediccion"
    ),
    "Sistemas expertos": (
        "sintoma", "sintomas",
        "diagnostico",
        "reglas",
        "credito"
    ),
    "Robótica y sistemas autónomos": (
        "trayectoria", "trayectorias",
        "robot",
        "dron",
        "obstaculo", "obstaculos"
    ),
    "Búsqueda y optimización": (
        "ruta",
        "optima",
        "horarios",
        "asignacion",
        "capacidad"
    ),
    "Sistemas de recomendación": (
        "recomendar",
        "recomendacion",
        "preferencias",
        "historial"
    ),
}
MANUAL_REFERENCE = [
    "Visión por computador",                  # 1. Detectar matrículas
    "Procesamiento de lenguaje natural",      # 2. Análisis de sentimiento
    "Aprendizaje automático predictivo",      # 3. Churn de clientes
    "Búsqueda y optimización",                # 4. Ruta más corta
    "Sistemas de recomendación",              # 5. Recomendar películas
    "Aprendizaje automático predictivo",      # 6. Detección de fraude
    "Visión por computador",                  # 7. Enfermedades de plantas por imágenes
    "Procesamiento de lenguaje natural",      # 8. Chatbot universitario
    "Aprendizaje automático predictivo",      # 9. Predicción de demanda energética
    "Sistemas expertos",                      # 10. Diagnóstico por síntomas
    "Búsqueda y optimización",                # 11. Problema de la mochila (knapsack)
    "Visión por computador",                  # 12. Reconocimiento facial
    "Procesamiento de lenguaje natural",      # 13. Clasificación de correos spam
    "Robótica y sistemas autónomos",          # 14. Robot móvil
    "Búsqueda y optimización",                # 15. Asignación de horarios
    "Aprendizaje automático predictivo",      # 16. Mantenimiento predictivo
    "Procesamiento de lenguaje natural",      # 17. Extracción de entidades en contratos
    "Visión por computador",                  # 18. Detección de peatones y señales
    "Sistemas expertos",                      # 19. Sistema basado en reglas para créditos
    "Robótica y sistemas autónomos",          # 20. Dron con ajuste de trayectoria
]

def normalize(text: str) -> str:
    text = text.strip().lower()
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def normalize_header(text: str) -> str: return normalize(text).replace(" ", "")


def contains_keyword(text: str, keyword: str) -> bool:
    # Compara palabras/frases completas para evitar falsos positivos como
    # "plan" dentro de "plantas".
    normalized_text = f" {normalize(text)} "
    normalized_keyword = normalize(keyword)
    return f" {normalized_keyword} " in normalized_text


def build_categories() -> list[Category]:
    result = []
    for category in CATEGORIES:
        extra = CUSTOM_RULES.get(category.name, ())
    result.append(Category(category.name, category.keywords + tuple(extra)))
    return result

def classify_problem(text: str) -> tuple[str, list[str], dict[str, int]]:
    scores = {}

    for category in build_categories():
        score = sum(
            contains_keyword(text, keyword)
            for keyword in category.keywords
        )
        scores[category.name] = score

    matches = [
        (score, index, category.name)
        for index, category in enumerate(build_categories())
        if (score := scores[category.name]) > 0
    ]

    matches.sort(key=lambda item: (-item[0], item[1]))

    detected = [name for _, _, name in matches]
    primary = detected[0] if detected else "Requiere análisis"

    return primary, detected or ["Requiere análisis"], scores

def read_cases() -> list[str]:
    if not CSV_FILE.exists():
        raise FileNotFoundError(
            f"No existe {CSV_FILE}. Crea data/casos_ia.csv antes de ejecutar la práctica."
        )

    with CSV_FILE.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        if not reader.fieldnames:
            raise ValueError("El CSV está vacío o no contiene encabezados.")

        original_headers = list(reader.fieldnames)

        reader.fieldnames = [
            normalize_header(name)
            for name in reader.fieldnames
        ]

        if "descripcion" not in reader.fieldnames:
            raise ValueError(
                "No se encontró la columna 'descripcion'. "
                f"Encabezados encontrados: {original_headers}"
            )

        # IMPORTANTE: cases debe estar aquí, antes del for
        cases = []

        for row in reader:
            description = (row.get("descripcion") or "").strip()

            if description:
                cases.append(description)

    # IMPORTANTE: este if debe estar DESPUÉS del for
    if len(cases) < 20:
        raise ValueError(
            f"La práctica requiere al menos 20 casos Sy el archivo contiene {len(cases)}."
        )

    return cases
def write_report(results: list[dict]) -> None:
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    reference_count = min(len(results), len(MANUAL_REFERENCE))
    matches = sum(
        results[i]["primary"] == MANUAL_REFERENCE[i]
        for i in range(reference_count)
    )
    accuracy = 100 * matches / reference_count if reference_count else 0.0 
    lines = [
        "# Semana 03 - Taxonomía de Inteligencia Artificial",
        "",
        "## Resultado automático frente a clasificación manual de referencia",
        "",
        "| Caso | Categoría automática principal | Categorías detectadas | Manual | Estado |",
        "|---:|---|---|---|---|",
    ]
    for i, result in enumerate(results, start=1):
        manual = MANUAL_REFERENCE[i -
                                  1] if i <= len(MANUAL_REFERENCE) else "Pendiente" 
        status = "Coincide" if result["primary"] == manual else "Revisar"
        detected = ", ".join(result["detected"])
        lines.append(
        f"| {i} | {result['primary']} | {detected} | {manual} | {status} |")
        lines += [
        "",
        f"Coincidencia con la referencia: **{accuracy:.2f}%** ({matches}/{reference_count}).",
        "",
        "## Cinco reglas propias",
        "", "Reemplaza o amplía las cinco reglas de ejemplo de `CUSTOM_RULES` y explica aquí por qué son pertinentes para tu dominio.",
        "",
        "## Discrepancias y análisis",
        "",
        "Para cada discrepancia explica: (1) qué palabra o frase activó la regla, (2) por qué la clasificación manual difiere y (3) qué regla modificarías.",
        "",
        "## Nota técnica",
        "",
        "Un problema real puede pertenecer a varias áreas de IA. La columna 'principal' usa la categoría con mayor cantidad de coincidencias; las demás coincidencias se conservan como categorías secundarias.",
    ]
    REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    cases = read_cases()
    results = []
    print("=" * 80)
    print("SEMANA 03 - TAXONOMÍA DE INTELIGENCIA ARTIFICIAL")
    print("=" * 80)
    for i, case in enumerate(cases, start=1):
        primary, detected, scores = classify_problem(case)
        results.append({
            "description": case,
            "primary": primary,
            "detected": detected,
            "scores": scores,
    }) 
        print("=" * 80)
        print(f"||{i:02d}. {case}||")
        #print("=" * 80)
        print(f"||Principal: {primary}||")
        #print("=" * 80)
        print(f"||Áreas detectadas: {', '.join(detected)}||")
        print("=" * 80)
    write_report(results)
    print(f"\nCasos procesados: {len(results)}")
    print(f"Reporte generado: {REPORT_FILE}")


if __name__ == "__main__":
    main()
