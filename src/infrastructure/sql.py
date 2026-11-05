"""Persistencia con SQLAlchemy Core: el mismo código funciona con PostgreSQL (Docker y producción)
y con SQLite (desarrollo y pruebas). El motor se elige con la variable de entorno DATABASE_URL.

Simplificación (ADR-07): cada Aggregate se guarda serializado en la columna `datos`; las columnas que
usan las consultas y los modelos de lectura (estado, saldo, folio…) se guardan aparte."""
import pickle
from datetime import date
from decimal import Decimal

from sqlalchemy import Column, Date, LargeBinary, MetaData, Numeric, String, Table, create_engine, func, select
from sqlalchemy.engine import Connection
from sqlalchemy.pool import StaticPool

from ..application.puertos import (
    EstadoDePagoDto,
    EstadoDePagoReader,
    UnitOfWork,
    VerificacionPublicaDto,
    VerificacionPublicaReader,
)
from ..domain.errores import NoEncontrado
from ..domain.repositorios import (
    ActaRepository,
    CertificadoRepository,
    CursoRepository,
    EstudianteRepository,
    ExpedienteRepository,
    GrupoRepository,
    InscripcionRepository,
    SolicitudRepository,
)

metadata = MetaData()


def _tabla(nombre: str, *extra) -> Table:
    return Table(nombre, metadata, Column("id", String(40), primary_key=True), *extra,
                 Column("datos", LargeBinary, nullable=False))


cursos = _tabla("cursos")
grupos = _tabla("grupos")
estudiantes = _tabla("estudiantes")
expedientes = _tabla("expedientes")
actas = _tabla("actas")
inscripciones = _tabla("inscripciones", Column("grupo", String(40), index=True), Column("estado", String(20)),
                       Column("saldo", Numeric(12, 2)), Column("fecha_limite", Date))
solicitudes = _tabla("solicitudes", Column("estudiante", String(40), index=True), Column("estado", String(20)),
                     Column("total", Numeric(12, 2)), Column("folio", String(40)))
certificados = Table("certificados", metadata, Column("folio", String(40), primary_key=True),
                     Column("inscripcion", String(40), unique=True, nullable=False),   # INV-25
                     Column("datos", LargeBinary, nullable=False))
verificacion_publica = Table("verificacion_publica", metadata, Column("folio", String(40), primary_key=True),
                             Column("titular", String(120)), Column("curso", String(120)),
                             Column("fecha_conclusion", Date), Column("vigencia", String(20)))


class BaseDeDatos:
    """Una conexión compartida por los repositorios y la Unidad de Trabajo.

    Dentro de una transacción (Unit of Work) los cambios esperan al COMMIT; fuera de ella cada
    operación se confirma sola, para que las lecturas sueltas no dejen transacciones abiertas."""

    def __init__(self, url: str):
        opciones = {}
        if url.startswith("sqlite"):
            opciones["connect_args"] = {"check_same_thread": False}
            if url in ("sqlite://", "sqlite:///:memory:"):
                opciones["poolclass"] = StaticPool       # en memoria: una sola base para todos los hilos
        self.engine = create_engine(url, **opciones)
        metadata.create_all(self.engine)
        self.conexion: Connection = self.engine.connect()
        self.enTransaccion = False

    def ejecutar(self, sentencia, parametros=None):
        resultado = self.conexion.execute(sentencia, parametros) if parametros else self.conexion.execute(sentencia)
        filas = resultado.fetchall() if resultado.returns_rows else None
        if not self.enTransaccion and self.conexion.in_transaction():
            self.conexion.commit()
        return filas

    def cerrar(self) -> None:
        self.conexion.close()
        self.engine.dispose()


class SqlUnitOfWork(UnitOfWork):
    def __init__(self, db: BaseDeDatos):
        self.db = db

    def iniciar(self) -> None:
        if self.db.conexion.in_transaction():
            self.db.conexion.commit()
        self.db.conexion.begin()
        self.db.enTransaccion = True

    def confirmar(self) -> None:
        self.db.conexion.commit()
        self.db.enTransaccion = False

    def cancelar(self) -> None:
        self.db.conexion.rollback()
        self.db.enTransaccion = False


class _SqlBase:
    tabla: Table

    def __init__(self, db: BaseDeDatos):
        self.db = db

    def _obtener(self, clave: str):
        filas = self.db.ejecutar(select(self.tabla.c.datos).where(self.tabla.c.id == clave))
        if not filas:
            raise NoEncontrado(f"No existe {clave} en {self.tabla.name}")
        return pickle.loads(filas[0][0])

    def _todos(self) -> list:
        return [pickle.loads(f[0]) for f in self.db.ejecutar(select(self.tabla.c.datos).order_by(self.tabla.c.id))]

    def _guardar(self, clave: str, objeto, **columnas) -> None:
        valores = {"datos": pickle.dumps(objeto), **columnas}
        existe = self.db.ejecutar(select(self.tabla.c.id).where(self.tabla.c.id == clave))
        if existe:
            self.db.ejecutar(self.tabla.update().where(self.tabla.c.id == clave).values(**valores))
        else:
            self.db.ejecutar(self.tabla.insert().values(id=clave, **valores))

    def _contar(self) -> int:
        return self.db.ejecutar(select(func.count()).select_from(self.tabla))[0][0]


class SqlCursoRepository(_SqlBase, CursoRepository):
    tabla = cursos
    def obtener(self, cursoId): return self._obtener(cursoId)
    def guardar(self, curso): self._guardar(curso.cursoId, curso)
    def todos(self): return self._todos()


class SqlGrupoRepository(_SqlBase, GrupoRepository):
    tabla = grupos
    def obtener(self, grupoId): return self._obtener(grupoId)
    def guardar(self, grupo): self._guardar(grupo.grupoId, grupo)
    def todos(self): return self._todos()


class SqlEstudianteRepository(_SqlBase, EstudianteRepository):
    tabla = estudiantes
    def obtener(self, estudianteId): return self._obtener(estudianteId)
    def guardar(self, estudiante): self._guardar(estudiante.estudianteId, estudiante)
    def todos(self): return self._todos()


class SqlInscripcionRepository(_SqlBase, InscripcionRepository):
    tabla = inscripciones

    def obtener(self, inscripcionId): return self._obtener(inscripcionId)

    def agregar(self, inscripcion): self.guardar(inscripcion)

    def guardar(self, i):
        self._guardar(i.inscripcionId, i, grupo=i.grupoId, estado=i.estado.value, saldo=i.saldoPendiente,
                      fecha_limite=i.fechaLimitePago)

    def delGrupo(self, grupoId):
        filas = self.db.ejecutar(select(inscripciones.c.datos).where(inscripciones.c.grupo == grupoId)
                                 .order_by(inscripciones.c.id))
        return [pickle.loads(f[0]) for f in filas]

    def siguienteId(self):
        return f"{self._contar() + 1:05d}"


class SqlSolicitudRepository(_SqlBase, SolicitudRepository):
    tabla = solicitudes

    def obtener(self, solicitudId): return self._obtener(solicitudId)
    def todas(self): return self._todos()

    def guardar(self, s):
        self._guardar(s.solicitudId, s, estudiante=s.estudianteId, estado=s.estado.value, total=s.total.monto,
                      folio=s.folio)

    def siguienteId(self):
        return f"SOL-{self._contar() + 1:04d}"


class SqlExpedienteRepository(_SqlBase, ExpedienteRepository):
    tabla = expedientes
    def obtener(self, inscripcionId): return self._obtener(inscripcionId)
    def guardar(self, expediente): self._guardar(expediente.inscripcionId, expediente)


class SqlActaRepository(_SqlBase, ActaRepository):
    tabla = actas
    def obtener(self, grupoId): return self._obtener(grupoId)
    def guardar(self, acta): self._guardar(acta.grupoId, acta)


class SqlCertificadoRepository(CertificadoRepository):
    def __init__(self, db: BaseDeDatos):
        self.db = db

    def agregar(self, c):
        # La restricción UNIQUE de la columna inscripcion refuerza INV-25.
        self.db.ejecutar(certificados.insert().values(folio=c.folio, inscripcion=c.inscripcionId,
                                                      datos=pickle.dumps(c)))
        # La proyección de la verificación pública se actualiza en la misma transacción (ADR-03).
        self.db.ejecutar(verificacion_publica.insert().values(folio=c.folio, titular=c.titular, curso=c.curso,
                                                              fecha_conclusion=c.fechaConclusion,
                                                              vigencia=c.vigencia))


class VerificacionPublicaSqlReader(VerificacionPublicaReader):
    def __init__(self, db: BaseDeDatos):
        self.db = db

    def consultar(self, folio):
        t = verificacion_publica
        filas = self.db.ejecutar(select(t.c.titular, t.c.curso, t.c.fecha_conclusion, t.c.vigencia)
                                 .where(t.c.folio == folio))
        return VerificacionPublicaDto(*filas[0]) if filas else None


class EstadoDePagoSqlReader(EstadoDePagoReader):
    def __init__(self, db: BaseDeDatos):
        self.db = db

    def consultar(self, inscripcionId):
        t = inscripciones
        filas = self.db.ejecutar(select(t.c.estado, t.c.saldo, t.c.fecha_limite).where(t.c.id == inscripcionId))
        if not filas:
            return None
        estado, saldo, limite = filas[0]
        saldo = Decimal(str(saldo)).quantize(Decimal("0.01"))
        return EstadoDePagoDto(estado, saldo, limite if isinstance(limite, date) else date.fromisoformat(limite))
