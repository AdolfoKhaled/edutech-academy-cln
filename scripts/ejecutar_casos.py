"""Ejecuta los 120 casos de casos_prueba.csv y las 20 pruebas de transiciones_prueba.csv del paquete
del profesor con el código de EduTech, y escribe el resultado real de cada uno en evidencias/.

Uso:  python scripts/ejecutar_casos.py

Cómo se interpreta cada acción del paquete con la máquina de estados de EduTech:
  aprobar            -> formalizar                (Preinscrito -> Inscrito)
  completar          -> formalizar y concluir     (Preinscrito -> Inscrito -> Concluido)
  cancelar           -> cancelar                  (Preinscrito -> Liberada)
  repetir_aprobacion -> formalizar dos veces      (la segunda debe rechazarse)
  saltar_estado      -> concluir sin formalizar   (debe rechazarse)
Cada caso usa una base nueva en memoria para que uno no afecte al siguiente."""
import csv
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from src.domain.errores import ErrorDeDominio  # noqa: E402
from src.infrastructure.carga_csv import cargar_datos, leer  # noqa: E402
from src.sistema import Sistema  # noqa: E402

DATOS = RAIZ / "datos"
SALIDA = RAIZ / "evidencias"

PASOS = {
    "aprobar": ["formalizar"],
    "completar": ["formalizar", "concluir"],
    "cancelar": ["cancelar"],
    "repetir_aprobacion": ["formalizar", "formalizar"],
    "saltar_estado": ["concluir"],
}


def sistema_nuevo() -> Sistema:
    s = Sistema({}, "sqlite://")
    cargar_datos(s, DATOS)
    return s


def ejecutar_caso(s: Sistema, caso: dict) -> dict:
    ev = s.solicitud.evaluar(caso["operacion_id"])
    if caso["tipo_prueba"] == "validar_operacion":
        resultado = "PROCESABLE" if ev.puedeProcesarse else "NO PROCESABLE: falta " + ", ".join(ev.motivos)
    else:
        resultado = "BENEFICIO APLICA" if ev.beneficioReferencia else "BENEFICIO NO APLICA"
    return {**caso, "resultado_alumno": resultado, "total_mxn": ev.total}


def ejecutar_transicion(caso: dict) -> dict:
    s = sistema_nuevo()
    sid, bitacora = caso["operacion_id"], []
    for paso in PASOS[caso["accion_sugerida"]]:
        antes = len(s.solicitud.obtener(sid).eventos)
        try:
            sol = getattr(s.solicitud, paso)(sid)
            nuevos = [type(e).__name__ for e in sol.eventos[antes:]]
            bitacora.append(f"{paso}: OK -> {sol.estado.value} ({', '.join(nuevos)})")
        except ErrorDeDominio as exc:
            bitacora.append(f"{paso}: RECHAZADO {type(exc).__name__}: {exc}")
            break
    final = s.solicitud.obtener(sid)
    s.cerrar()
    return {**caso, "resultado_alumno": " | ".join(bitacora), "estado_final": final.estado.value,
            "eventos": ", ".join(type(e).__name__ for e in final.eventos)}


def escribir(nombre: str, filas: list[dict]) -> None:
    SALIDA.mkdir(exist_ok=True)
    with (SALIDA / nombre).open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0]))
        w.writeheader()
        w.writerows(filas)


def main() -> None:
    s = sistema_nuevo()
    casos = [ejecutar_caso(s, c) for c in leer(DATOS, "casos_prueba.csv")]
    s.cerrar()
    escribir("resultados_casos_prueba.csv", casos)
    transiciones = [ejecutar_transicion(c) for c in leer(DATOS, "transiciones_prueba.csv")]
    escribir("resultados_transiciones.csv", transiciones)

    procesables = sum(c["resultado_alumno"] == "PROCESABLE" for c in casos if c["tipo_prueba"] == "validar_operacion")
    beneficio = sum(c["resultado_alumno"] == "BENEFICIO APLICA" for c in casos)
    print(f"casos_prueba: {len(casos)} ejecutados · {procesables}/60 procesables · {beneficio}/60 con beneficio")
    for t in transiciones:
        print(f"{t['caso_id']} {t['operacion_id']} {t['accion_sugerida']:<19} -> {t['estado_final']:<11} "
              f"{t['resultado_alumno']}")


if __name__ == "__main__":
    main()
