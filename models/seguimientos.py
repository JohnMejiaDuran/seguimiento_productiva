from utils.db import db
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship


class UserRole(db.Model):
    __tablename__ = "user_role"
    __table_args__ = {"mysql_engine": "InnoDB"}
    user_id = db.Column(db.Integer, db.ForeignKey("base_user.id"), primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey("role.id"), primary_key=True)


class Role(db.Model):
    __tablename__ = "role"
    __table_args__ = {"mysql_engine": "InnoDB"}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)


class BaseUser(db.Model, UserMixin):
    __tablename__ = "base_user"
    __table_args__ = {"mysql_engine": "InnoDB"}
    id = db.Column(db.Integer, primary_key=True)
    documento = db.Column(db.String(15), unique=True)
    nombre = db.Column(db.String(100))
    apellido = db.Column(db.String(100))
    email = db.Column(db.String(100))
    password = db.Column(db.String(162))
    telefono = db.Column(db.String(50))
    roles = db.relationship("Role", secondary="user_role", backref="users")

    def __init__(self, documento, nombre, apellido, email, password, telefono) -> None:
        self.documento = documento
        self.nombre = nombre
        self.apellido = apellido
        self.email = email
        self.password = password
        self.telefono = telefono
    @classmethod
    def check_password(self, hashed_password, password):
        return check_password_hash(hashed_password, password)


print(generate_password_hash("1098789300"))


class Administrador(BaseUser):
    __tablename__ = "administrador"
    __table_args__ = {"mysql_engine": "InnoDB"}
    documento = db.Column(
        db.String(15), db.ForeignKey("base_user.documento"), primary_key=True
    )
    cargo = db.Column(db.String(50))

    __mapper_args__ = {
        "polymorphic_identity": "administrador",
    }

    def __init__(
        self, documento, nombre, apellido, email, password, cargo=None
    ) -> None:
        super().__init__(documento, nombre, apellido, email, password)
        self.cargo = cargo


class Coordinador(BaseUser):
    __tablename__ = "coordinador"
    __table_args__ = {"mysql_engine": "InnoDB"}

    documento = db.Column(
        db.String(15), db.ForeignKey("base_user.documento"), primary_key=True
    )
    area = db.Column(db.String(50))

    __mapper_args__ = {
        "polymorphic_identity": "coordinador",
    }

    def __init__(self, documento, nombre, apellido, email, password, area=None) -> None:
        super().__init__(documento, nombre, apellido, email, password)
        self.area = area


class Instructor(BaseUser):
    __tablename__ = "instructor"
    __table_args__ = {"mysql_engine": "InnoDB"}

    documento = db.Column(
        db.String(15), db.ForeignKey("base_user.documento"), primary_key=True
    )
    vinculacion = db.Column(db.String(15), nullable=True)

    __mapper_args__ = {
        "polymorphic_identity": "instructor",
    }

    def __init__(
        self, documento, nombre, apellido, email, password, telefono, vinculacion
    ) -> None:
        super().__init__(documento, nombre, apellido, email, password, telefono)
        self.vinculacion = vinculacion

class Aprendiz(BaseUser):
    __tablename__ = "aprendiz"
    __table_args__ = {"mysql_engine": "InnoDB"}

    documento = db.Column(
        db.String(15), db.ForeignKey("base_user.documento"), primary_key=True
    )
    alternativa = db.Column(db.String(50))
    ficha_sin_decimal = db.Column(db.String(20))
    programa = db.Column(db.String(100))
    documento_instructor = db.Column(
        db.String(15), db.ForeignKey("instructor.documento")
    )

    __mapper_args__ = {
        "polymorphic_identity": "aprendiz",
    }

    def __init__(
        self,
        documento,
        nombre,
        apellido,
        alternativa,
        ficha_sin_decimal,
        programa,
        documento_instructor,
        email=None,
        password=None,
    ) -> None:
        super().__init__(documento, nombre, apellido, email, password)
        self.alternativa = alternativa
        self.ficha_sin_decimal = ficha_sin_decimal
        self.programa = programa
        self.documento_instructor = documento_instructor


class Asignacion(db.Model):

    __table_args__ = {"mysql_engine": "InnoDB"}

    id_asignacion = db.Column(db.Integer, primary_key=True)
    documento_aprendiz = db.Column(db.String(15), ForeignKey("aprendiz.documento"))
    documento_instructor = db.Column(db.String(15), ForeignKey("instructor.documento"))
    fecha_inicio = db.Column(db.String(15))  # se extrae del excel con openpyxl
    fecha_fin = db.Column(db.String(15))  # se extrae del excel con openpyxl
    fecha_asignacion = db.Column(db.String(15))  # Fecha actual
    fecha_inicio_contrato = db.Column(db.String(15))  # null, la actualiza el aprendiz
    fecha_fin_contrato = db.Column(db.String(15))  # null, la actualiza el apreniz

    aprendiz = relationship("Aprendiz", foreign_keys=[documento_aprendiz])
    instructor = relationship("Instructor", foreign_keys=[documento_instructor])

    def __init__(
        self,
        id_asignacion,
        documento_aprendiz,
        documento_instructor,
        fecha_inicio,
        fecha_fin,
        fecha_asignacion,
        fecha_inicio_contrato,
        fecha_fin_contrato,
    ):
        self.id_asignacion = id_asignacion
        self.documento_aprendiz = documento_aprendiz
        self.documento_instructor = documento_instructor
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.fecha_asignacion = fecha_asignacion
        self.fecha_inicio_contrato = fecha_inicio_contrato
        self.fecha_fin_contrato = fecha_fin_contrato


class Regional(db.Model):
    __table_args__ = {"mysql_engine": "InnoDB"}
    codigo_regional = db.Column(db.Integer, primary_key=True)
    nombre_regional = db.Column(db.String(100))

    def __init__(self, codigo_regional, nombre_regional):
        self.codigo_regional = codigo_regional
        self.nombre_regional = nombre_regional


class Centro(db.Model):
    __table_args__ = {"mysql_engine": "InnoDB"}
    codigo_centro = db.Column(db.Integer, primary_key=True)
    nombre_centro = db.Column(db.String(100))
    codigo_regional = db.Column(db.Integer, ForeignKey("regional.codigo_regional"))

    regional = relationship("Regional", foreign_keys=[codigo_regional])

    def __init__(self, codigo_centro, nombre_centro, codigo_regional):
        self.codigo_regional = codigo_regional
        self.nombre_centro = nombre_centro
        self.codigo_centro = codigo_centro


class Variable(db.Model):
    __table_args__ = {"mysql_engine": "InnoDB"}
    id_variable = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    tipo = db.Column(db.String(100))
    descripcion = db.Column(db.String(100))

    def __init__(self, id_variable, nombre, tipo, descripcion):
        self.id_variable = id_variable
        self.nombre = nombre
        self.tipo = tipo
        self.descripcion = descripcion

    class Valoracion(db.Model):
        __table_args__ = {"mysql_engine": "InnoDB"}
        id_valoracion = db.Column(db.Integer, primary_key=True)
        id_variable = db.Column(db.Integer, ForeignKey("variable.id_variable"))
        id_seguimiento = db.Column(db.Integer, ForeignKey("seguimiento.id_seguimiento"))
        valoracion = db.Column(db.String(100))
        observacion = db.Column(db.String(100))

        variable = relationship("Variable", foreign_keys=[id_variable])

        def __init__(
            self, id_valoracion, id_variable, id_seguimiento, valoracion, observacion
        ):
            self.id_valoracion = id_valoracion
            self.id_variable = id_variable
            self.id_seguimiento = id_seguimiento
            self.valoracion = valoracion
            self.observacion = observacion


class Seguimiento(db.Model):
    __table_args__ = {"mysql_engine": "InnoDB"}
    id_seguimiento = db.Column(db.Integer, primary_key=True)
    tipo_seguimiento = db.Column(db.String(100))
    observacion = db.Column(db.String(100))
    fecha_inicio = db.Column(db.String(15))
    fecha_fin = db.Column(db.String(15))
    tipo = db.Column(db.String(100))
    nit = db.Column(db.Integer, ForeignKey("empresa.nit"))
    codigo_centro = db.Column(db.Integer, ForeignKey("centro.codigo_centro"))
    documento_aprendiz_aprendiz = db.Column(
        db.String(15), ForeignKey("aprendiz.documento")
    )
    documento_instructor = db.Column(db.String(15), ForeignKey("instructor.documento"))
    reconocimiento = db.Column(db.String(50))

    aprendiz = relationship("Aprendiz", foreign_keys=[documento_aprendiz_aprendiz])
    empresa = relationship("Empresa", foreign_keys=[nit])
    centro = relationship("Centro", foreign_keys=[codigo_centro])
    instructor = relationship("Instructor", foreign_keys=[documento_instructor])

    def __init__(
        self,
        id_seguimiento,
        tipo_seguimiento,
        observacion,
        fecha_inicio,
        fecha_fin,
        tipo,
        nit,
        codigo_centro,
        documento_aprendiz,
        documento_instructor,
        reconocimiento,
    ):
        self.id_seguimiento = id_seguimiento
        self.tipo_seguimiento = tipo_seguimiento
        self.observacion = observacion
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.tipo = tipo
        self.nit = nit
        self.codigo_centro = codigo_centro
        self.documento_aprendiz = documento_aprendiz
        self.documento_instructor = documento_instructor
        self.reconocimiento = reconocimiento


class Empresa(db.Model):
    __table_args__ = {"mysql_engine": "InnoDB"}
    nit = db.Column(db.Integer, primary_key=True)
    razon_social = db.Column(db.String(100))
    direccion = db.Column(db.String(100))

    def __init__(self, nit, razon_social, direccion):
        self.nit = nit
        self.razon_social = razon_social
        self.direccion = direccion
