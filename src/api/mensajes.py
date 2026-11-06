"""Traduce los errores de validación de FastAPI/Pydantic (en inglés y con rutas técnicas) a un mensaje
corto en español que entienda el usuario. Ejemplo: cursos.0.lugares, greater_than_equal 1
-> "El dato 'lugares' (curso 1) debe ser mayor o igual a 1."."""

NOMBRES = {
    "estudianteId": "estudiante", "cursoId": "curso", "cursos": "cursos", "lugares": "lugares",
    "autorizada": "autorizada", "promocionActiva": "promoción activa", "fecha": "fecha", "ahora": "fecha y hora",
    "hoy": "fecha", "motivo": "motivo", "nombre": "nombre", "correo": "correo", "telefono": "teléfono",
    "monto": "monto", "sesion": "sesión", "presente": "presente", "clave": "clave", "tipo": "tipo",
    "valor": "calificación", "grupoId": "grupo", "inscripcionId": "inscripción", "x-usuario": "X-Usuario",
}

FORMATOS = {
    "int_parsing": "debe ser un número entero", "int_type": "debe ser un número entero",
    "int_from_float": "debe ser un número entero", "float_parsing": "debe ser un número",
    "float_type": "debe ser un número", "decimal_parsing": "debe ser un importe, por ejemplo 566.00",
    "decimal_type": "debe ser un importe, por ejemplo 566.00", "bool_parsing": "debe ser true o false",
    "bool_type": "debe ser true o false", "string_type": "debe ser texto", "list_type": "debe ser una lista",
    "date_parsing": "debe ser una fecha con formato AAAA-MM-DD",
    "date_from_datetime_parsing": "debe ser una fecha con formato AAAA-MM-DD",
    "datetime_parsing": "debe ser fecha y hora con formato AAAA-MM-DDTHH:MM",
    "datetime_from_date_parsing": "debe ser fecha y hora con formato AAAA-MM-DDTHH:MM",
    "model_attributes_type": "debe ser un objeto JSON", "dict_type": "debe ser un objeto JSON",
}


def _campo(loc: tuple) -> str:
    """('body', 'cursos', 0, 'lugares') -> "'lugares' (curso 1)"."""
    partes = [p for p in loc[1:]]
    if not partes:
        return "el cuerpo de la petición"
    nombre = NOMBRES.get(str(partes[-1]), NOMBRES.get(str(partes[-1]).lower(), str(partes[-1])))
    posiciones = [p for p in partes if isinstance(p, int)]
    detalle = f" (curso {posiciones[-1] + 1})" if posiciones and "cursos" in partes else ""
    return f"'{nombre}'{detalle}"


def explicar(error: dict) -> str:
    tipo, loc, ctx = error.get("type", ""), tuple(error.get("loc", ())), error.get("ctx") or {}
    campo = _campo(loc)
    if tipo == "json_invalid":
        return "El cuerpo de la petición no es un JSON válido."
    if tipo == "missing":
        if loc and loc[0] == "header":
            return "Falta el encabezado X-Usuario: indica qué usuario hace la acción (por ejemplo inst-1)."
        return f"Falta el dato {campo} en la petición."
    if tipo in ("greater_than_equal", "greater_than", "less_than_equal", "less_than"):
        relacion = {"greater_than_equal": "mayor o igual a", "greater_than": "mayor que",
                    "less_than_equal": "menor o igual a", "less_than": "menor que"}[tipo]
        limite = next(iter(ctx.values()), "")
        return f"El dato {campo} debe ser {relacion} {limite}."
    if tipo in FORMATOS:
        return f"El dato {campo} {FORMATOS[tipo]}."
    return f"El dato {campo} no es válido."
