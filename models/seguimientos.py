from utils.db import db
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship
from sqlalchemy import event


class UserRole(db.Model):
    __tablename__ = "user_role"
    __table_args__ = {"mysql_engine": "InnoDB"}
    user_id = db.Column(db.Integer, db.ForeignKey("base_user.id"), primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey("role.id"), primary_key=True)


def __init__(self, user_id, role_id):
    self.user_id = user_id
    self.role_id = role_id


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
    password_changed = db.Column(db.Boolean, default=False)
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
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, hashed_password, password):
        return check_password_hash(hashed_password, password)

    def change_password(self, new_password):
        self.password = generate_password_hash(new_password)
        self.password_changed = True

    def has_changed_password(self):
        return self.password_changed


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


class Ficha(db.Model):
    __tablename__ = "ficha"
    __table_args__ = {"mysql_engine": "InnoDB"}

    id_ficha = db.Column(db.Integer, primary_key=True)
    programa = db.Column(db.String(200))
    codigo_centro = db.Column(db.Integer, ForeignKey("centro.codigo_centro"))
    centro = relationship("Centro", foreign_keys=[codigo_centro])


class Aprendiz(BaseUser):
    __tablename__ = "aprendiz"
    __table_args__ = {"mysql_engine": "InnoDB"}

    documento = db.Column(
        db.String(15), db.ForeignKey("base_user.documento"), primary_key=True
    )
    alternativa = db.Column(db.String(50))
    ficha_id = db.Column(db.Integer, db.ForeignKey("ficha.id_ficha"))
    ficha = relationship("Ficha", foreign_keys=[ficha_id])

    __mapper_args__ = {
        "polymorphic_identity": "aprendiz",
    }

    def __init__(
        self,
        documento,
        nombre,
        apellido,
        alternativa,
        ficha_id,
        password,
        telefono,
        email,
    ):
        super().__init__(documento, nombre, apellido, email, password, telefono)
        self.alternativa = alternativa
        self.ficha_id = ficha_id


class Asignacion(db.Model):

    __table_args__ = {"mysql_engine": "InnoDB"}

    id_asignacion = db.Column(db.Integer, primary_key=True, autoincrement=True)
    documento_aprendiz = db.Column(db.String(15), ForeignKey("aprendiz.documento"))
    documento_instructor = db.Column(db.String(15), ForeignKey("instructor.documento"))
    fecha_inicio = db.Column(db.String(15))  # se extrae del excel con openpyxl
    fecha_fin = db.Column(db.String(15))  # se extrae del excel con openpyxl
    fecha_asignacion = db.Column(db.String(15))  # Fecha actual
    fecha_inicio_contrato = db.Column(db.String(15), index=True)
    fecha_fin_contrato = db.Column(db.String(15), index=True)

    aprendiz = relationship("Aprendiz", foreign_keys=[documento_aprendiz])
    instructor = relationship("Instructor", foreign_keys=[documento_instructor])


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
    descripcion = db.Column(db.String(255))

    def __init__(self, nombre, tipo, descripcion):
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
    documento_aprendiz_aprendiz = db.Column(
        db.String(15), ForeignKey("aprendiz.documento")
    )
    documento_instructor = db.Column(db.String(15), ForeignKey("instructor.documento"))
    reconocimiento = db.Column(db.String(50))

    aprendiz = relationship("Aprendiz", foreign_keys=[documento_aprendiz_aprendiz])
    empresa = relationship("Empresa", foreign_keys=[nit])
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


def insert_regionales(*args, **kwargs):
    regionales = [
        {"codigo_regional": "05", "nombre_regional": "Regional Antioquia"},
        {"codigo_regional": "08", "nombre_regional": "Regional Atlantico"},
        {"codigo_regional": "11", "nombre_regional": "Regional Distrito Capital"},
        {"codigo_regional": "13", "nombre_regional": "Regional Bolívar"},
        {"codigo_regional": "15", "nombre_regional": "Regional Boyacá"},
        {"codigo_regional": "17", "nombre_regional": "Regional Caldas"},
        {"codigo_regional": "18", "nombre_regional": "Regional Caquetá"},
        {"codigo_regional": "19", "nombre_regional": "Regional Cauca"},
        {"codigo_regional": "20", "nombre_regional": "Regional Cesar"},
        {"codigo_regional": "23", "nombre_regional": "Regional Córdoba"},
        {"codigo_regional": "25", "nombre_regional": "Regional Cundinamarca"},
        {"codigo_regional": "27", "nombre_regional": "Regional Chocó"},
        {"codigo_regional": "41", "nombre_regional": "Regional Huila"},
        {"codigo_regional": "44", "nombre_regional": "Regional Guajira"},
        {"codigo_regional": "47", "nombre_regional": "Regional Magdalena"},
        {"codigo_regional": "50", "nombre_regional": "Regional Meta"},
        {"codigo_regional": "52", "nombre_regional": "Regional Nariño"},
        {"codigo_regional": "54", "nombre_regional": "Regional Norte de Satander"},
        {"codigo_regional": "63", "nombre_regional": "Regional Quindío"},
        {"codigo_regional": "66", "nombre_regional": "Regional Risaralda"},
        {"codigo_regional": "68", "nombre_regional": "Regional Santander"},
        {"codigo_regional": "70", "nombre_regional": "Regional Sucre"},
        {"codigo_regional": "73", "nombre_regional": "Regional Tolima"},
        {"codigo_regional": "76", "nombre_regional": "Regional Valle"},
        {"codigo_regional": "81", "nombre_regional": "Regional Arauca"},
        {"codigo_regional": "85", "nombre_regional": "Regional Casanare"},
        {"codigo_regional": "86", "nombre_regional": "Regional Putumayo"},
        {"codigo_regional": "88", "nombre_regional": "Regional San Andres"},
        {"codigo_regional": "91", "nombre_regional": "Regional Amazonas"},
        {"codigo_regional": "94", "nombre_regional": "Regional Guainía"},
        {"codigo_regional": "95", "nombre_regional": "Regional Guaviare"},
        {"codigo_regional": "97", "nombre_regional": "Regional Vaupés"},
        {"codigo_regional": "99", "nombre_regional": "Regional Vichada"},
    ]

    for regiones in regionales:
        regional = Regional(**regiones)
        db.session.add(regional)
    db.session.commit()


event.listen(Regional.__table__, "after_create", insert_regionales)


def insert_centros(*args, **kwargs):
    centros = [
        {
            "codigo_centro": "9101",
            "nombre_centro": "CENTRO DE LOS RECURSOS NATURALES RENOVABLES - LA SALADA",
            "codigo_regional": "05",
        },
        {
            "codigo_centro": "9127",
            "nombre_centro": "CENTRO DE FORMACIÓN MINERO AMBIENTAL",
            "codigo_regional": "05",
        },
        {
            "codigo_centro": "9201",
            "nombre_centro": "CENTRO DEL DISEÑO Y MANUFACTURA DEL CUERO",
            "codigo_regional": "05",
        },
        {
            "codigo_centro": "9202",
            "nombre_centro": "CENTRO DE FORMACIÓN EN DISEÑO, CONFECCIÓN Y MODA",
            "codigo_regional": "05",
        },
        {
            "codigo_centro": "9203",
            "nombre_centro": "CENTRO PARA EL DESARROLLO DEL HABITAT Y LA CONSTRUCCIÓN",
            "codigo_regional": "05",
        },
        {
            "codigo_centro": "9204",
            "nombre_centro": "CENTRO DE TECNOLOGÍA DE LA MANUFACTURA AVANZADA",
            "codigo_regional": "05",
        },
        {
            "codigo_centro": "9205",
            "nombre_centro": "CENTRO TECNOLÓGICO DEL MOBILIARIO",
            "codigo_regional": "05",
        },
        {
            "codigo_centro": "9206",
            "nombre_centro": "CENTRO TEXTIL Y DE GESTIÓN INDUSTRIAL",
            "codigo_regional": "05",
        },
        {
            "codigo_centro": "9301",
            "nombre_centro": "CENTRO DE COMERCIO",
            "codigo_regional": "05",
        },
        {
            "codigo_centro": "9401",
            "nombre_centro": "CENTRO DE SERVICIOS DE SALUD",
            "codigo_regional": "05",
        },
        {
            "codigo_centro": "9402",
            "nombre_centro": "CENTRO DE SERVICIOS Y GESTION EMPRESARIAL",
            "codigo_regional": "05",
        },
        {
            "codigo_centro": "9501",
            "nombre_centro": "COMPLEJO TECNOLOGICO PARA LA GESTION AGROEMPRESARIAL",
            "codigo_regional": "05",
        },
        {
            "codigo_centro": "9502",
            "nombre_centro": "COMPLEJO TECNOLÓGICO MINERO AGROEMPRESARIAL",
            "codigo_regional": "05",
        },
        {
            "codigo_centro": "9503",
            "nombre_centro": "CENTRO DE LA INNOVACIÓN, LA AGROINDUSTRIA Y LA AVIACIÓN",
            "codigo_regional": "05",
        },
        {
            "codigo_centro": "9504",
            "nombre_centro": "COMPLEJO TECNOLOGICO AGROINDUSTRIAL, PECUARIO Y TURISTICO",
            "codigo_regional": "05",
        },
        {
            "codigo_centro": "9549",
            "nombre_centro": "COMPLEJO TECNOLOGICO, TURISTICO Y AGROINDUSTRIAL DEL OCCIDENTE ANTIOQUEÑO",
            "codigo_regional": "05",
        },
        {
            "codigo_centro": "9103",
            "nombre_centro": "CENTRO PARA EL DESARROLLO AGROECOLÓGICO Y AGROINDUSTRIAL",
            "codigo_regional": "08",
        },
        {
            "codigo_centro": "9207",
            "nombre_centro": "CENTRO NACIONAL COLOMBO ALEMAN",
            "codigo_regional": "08",
        },
        {
            "codigo_centro": "9208",
            "nombre_centro": "CENTRO INDUSTRIAL Y DE AVIACION",
            "codigo_regional": "08",
        },
        {
            "codigo_centro": "9302",
            "nombre_centro": "CENTRO DE COMERCIO Y SERVICIOS",
            "codigo_regional": "08",
        },
        {
            "codigo_centro": "9209",
            "nombre_centro": "CENTRO DE TECNOLOGÍAS PARA LA CONSTRUCCIÓN Y LA MADERA",
            "codigo_regional": "11",
        },
        {
            "codigo_centro": "9210",
            "nombre_centro": "CENTRO DE ELECTRICIDAD, ELECTRÓNICA Y TELECOMUNICACIONES",
            "codigo_regional": "11",
        },
        {
            "codigo_centro": "9211",
            "nombre_centro": "CENTRO DE GESTION INDUSTRIAL",
            "codigo_regional": "11",
        },
        {
            "codigo_centro": "9212",
            "nombre_centro": "CENTRO DE MANUFACTURA EN TEXTILES Y CUERO",
            "codigo_regional": "11",
        },
        {
            "codigo_centro": "9213",
            "nombre_centro": "CENTRO DE TECNOLOGÍAS DEL TRANSPORTE",
            "codigo_regional": "11",
        },
        {
            "codigo_centro": "9214",
            "nombre_centro": "CENTRO METALMECANICO",
            "codigo_regional": "11",
        },
        {
            "codigo_centro": "9215",
            "nombre_centro": "CENTRO DE MATERIALES Y ENSAYOS",
            "codigo_regional": "11",
        },
        {
            "codigo_centro": "9216",
            "nombre_centro": "CENTRO DE DISEÑO Y METROLOGÍA",
            "codigo_regional": "11",
        },
        {
            "codigo_centro": "9217",
            "nombre_centro": "CENTRO PARA LA INDUSTRIA DE LA COMUNICACIÓN GRAFICA",
            "codigo_regional": "11",
        },
        {
            "codigo_centro": "9303",
            "nombre_centro": "CENTRO DE GESTION DE MERCADOS, LOGÍSTICA Y TECNOLOGÍAS DE LA INFORMACIÓN",
            "codigo_regional": "11",
        },
        {
            "codigo_centro": "9403",
            "nombre_centro": "CENTRO DE FORMACION DE TALENTO HUMANO EN SALUD",
            "codigo_regional": "11",
        },
        {
            "codigo_centro": "9404",
            "nombre_centro": "CENTRO DE GESTIÓN ADMINISTRATIVA",
            "codigo_regional": "11",
        },
        {
            "codigo_centro": "9405",
            "nombre_centro": "CENTRO DE SERVICIOS FINANCIEROS",
            "codigo_regional": "11",
        },
        {
            "codigo_centro": "9406",
            "nombre_centro": "CENTRO NACIONAL DE HOTELERIA, TURISMO Y ALIMENTOS",
            "codigo_regional": "11",
        },
        {
            "codigo_centro": "9508",
            "nombre_centro": "CENTRO DE FORMACIÓN EN ACTIVIDAD FÍSICA Y CULTURA",
            "codigo_regional": "11",
        },
        {
            "codigo_centro": "9104",
            "nombre_centro": "CENTRO AGROEMPRESARIAL Y MINERO",
            "codigo_regional": "13",
        },
        {
            "codigo_centro": "9105",
            "nombre_centro": "CENTRO INTERNACIONAL NÁUTICO, FLUVIAL Y PORTUARIO",
            "codigo_regional": "13",
        },
        {
            "codigo_centro": "9218",
            "nombre_centro": "CENTRO PARA LA INDUSTRIA PETROQUÍMICA",
            "codigo_regional": "13",
        },
        {
            "codigo_centro": "9304",
            "nombre_centro": "CENTRO DE COMERCIO Y SERVICIOS",
            "codigo_regional": "13",
        },
        {
            "codigo_centro": "9110",
            "nombre_centro": "CENTRO DE DESARROLLO AGROPECUARIO Y AGROINDUSTRIAL",
            "codigo_regional": "15",
        },
        {
            "codigo_centro": "9111",
            "nombre_centro": "CENTRO MINERO",
            "codigo_regional": "15",
        },
        {
            "codigo_centro": "9305",
            "nombre_centro": "CENTRO DE GESTION ADMINISTRATIVA Y FORTALECIMIENTO EMPRESARIAL",
            "codigo_regional": "15",
        },
        {
            "codigo_centro": "9514",
            "nombre_centro": "CENTRO INDUSTRIAL DE MANTENIMIENTO Y MANUFACTURA",
            "codigo_regional": "15",
        },
        {
            "codigo_centro": "9551",
            "nombre_centro": "CENTRO DE LA INNOVACIÓN AGROINDUSTRIAL Y DE SERVICIOS",
            "codigo_regional": "15",
        },
        {
            "codigo_centro": "9112",
            "nombre_centro": "CENTRO PARA LA FORMACION CAFETERA",
            "codigo_regional": "17",
        },
        {
            "codigo_centro": "9219",
            "nombre_centro": "CENTRO DE AUTOMATIZACION INDUSTRIAL",
            "codigo_regional": "17",
        },
        {
            "codigo_centro": "9220",
            "nombre_centro": "CENTRO DE PROCESOS INDUSTRIALES Y CONSTRUCCIÓN",
            "codigo_regional": "17",
        },
        {
            "codigo_centro": "9306",
            "nombre_centro": "CENTRO DE COMERCIO Y SERVICIOS",
            "codigo_regional": "17",
        },
        {
            "codigo_centro": "9515",
            "nombre_centro": "CENTRO PECUARIO Y AGROEMPRESARIAL",
            "codigo_regional": "17",
        },
        {
            "codigo_centro": "9516",
            "nombre_centro": "CENTRO TECNOLOGICO DE LA AMAZONÍA",
            "codigo_regional": "18",
        },
        {
            "codigo_centro": "9113",
            "nombre_centro": "CENTRO AGROPECUARIO",
            "codigo_regional": "19",
        },
        {
            "codigo_centro": "9221",
            "nombre_centro": "CENTRO DE TELEINFORMÁTICA Y PRODUCCIÓN INDUSTRIAL",
            "codigo_regional": "19",
        },
        {
            "codigo_centro": "9307",
            "nombre_centro": "CENTRO DE COMERCIO Y SERVICIOS",
            "codigo_regional": "19",
        },
        {
            "codigo_centro": "9114",
            "nombre_centro": "CENTRO BIOTECNOLOGICO DEL CARIBE",
            "codigo_regional": "20",
        },
        {
            "codigo_centro": "9520",
            "nombre_centro": "CENTRO AGROEMPRESARIAL",
            "codigo_regional": "20",
        },
        {
            "codigo_centro": "9521",
            "nombre_centro": "CENTRO DE OPERACIÓN Y MANTENIMIENTO MINERO",
            "codigo_regional": "20",
        },
        {
            "codigo_centro": "9115",
            "nombre_centro": "CENTRO AGROPECUARIO Y DE BIOTECNOLOGIA EL PORVENIR",
            "codigo_regional": "23",
        },
        {
            "codigo_centro": "9523",
            "nombre_centro": "CENTRO DE COMERCIO, INDUSTRIA Y TURISMO DE CORDOBA",
            "codigo_regional": "23",
        },
        {
            "codigo_centro": "9232",
            "nombre_centro": "CENTRO INDUSTRIAL Y DE DESARROLLO EMPRESARIAL DE SOACHA",
            "codigo_regional": "25",
        },
        {
            "codigo_centro": "9509",
            "nombre_centro": "CENTRO DE DESARROLLO AGROINDUSTRIAL Y EMPRESARIAL",
            "codigo_regional": "25",
        },
        {
            "codigo_centro": "9510",
            "nombre_centro": "CENTRO AGROECOLOGICO Y EMPRESARIAL",
            "codigo_regional": "25",
        },
        {
            "codigo_centro": "9511",
            "nombre_centro": "CENTRO DE LA TECNOLOGIA DEL DISEÑO Y LA PRODUCTIVIDAD EMPRESARIAL",
            "codigo_regional": "25",
        },
        {
            "codigo_centro": "9512",
            "nombre_centro": "CENTRO DE BIOTECNOLOGIA AGROPECUARIA",
            "codigo_regional": "25",
        },
        {
            "codigo_centro": "9513",
            "nombre_centro": "CENTRO DE DESARROLLO AGROEMPRESARIAL",
            "codigo_regional": "25",
        },
        {
            "codigo_centro": "9522",
            "nombre_centro": "CENTRO DE RECURSOS NATURALES, INDUSTRIA Y BIODIVERSIDAD",
            "codigo_regional": "27",
        },
        {
            "codigo_centro": "9116",
            "nombre_centro": "CENTRO DE FORMACION AGROINDUSTRIAL",
            "codigo_regional": "41",
        },
        {
            "codigo_centro": "9525",
            "nombre_centro": "CENTRO AGROEMPRESARIAL Y DESARROLLO PECUARIO DEL HUILA",
            "codigo_regional": "41",
        },
        {
            "codigo_centro": "9526",
            "nombre_centro": "CENTRO DE DESARROLLO AGROEMPRESARIAL Y TURISTICO DEL HUILA",
            "codigo_regional": "41",
        },
        {
            "codigo_centro": "9527",
            "nombre_centro": "CENTRO DE LA INDUSTRIA, LA EMPRESA Y LOS SERVICIOS",
            "codigo_regional": "41",
        },
        {
            "codigo_centro": "9528",
            "nombre_centro": "CENTRO DE GESTIÓN Y DESARROLLO SOSTENIBLE SURCOLOMBIANO",
            "codigo_regional": "41",
        },
        {
            "codigo_centro": "9222",
            "nombre_centro": "CENTRO INDUSTRIAL Y DE ENERGIAS ALTERNATIVAS",
            "codigo_regional": "44",
        },
        {
            "codigo_centro": "9524",
            "nombre_centro": "CENTRO AGROEMPRESARIAL Y ACUICOLA",
            "codigo_regional": "44",
        },
        {
            "codigo_centro": "9118",
            "nombre_centro": "CENTRO ACUÍCOLA Y AGROINDUSTRIAL DE GAIRA",
            "codigo_regional": "47",
        },
        {
            "codigo_centro": "9529",
            "nombre_centro": "CENTRO DE LOGÍSTICA Y PROMOCIÓN ECOTURÍSTICA DEL MAGDALENA",
            "codigo_regional": "47",
        },
        {
            "codigo_centro": "9117",
            "nombre_centro": "CENTRO AGROINDUSTRIAL DEL META",
            "codigo_regional": "50",
        },
        {
            "codigo_centro": "9532",
            "nombre_centro": "CENTRO DE INDUSTRIA Y SERVICIOS DEL META",
            "codigo_regional": "50",
        },
        {
            "codigo_centro": "9534",
            "nombre_centro": "CENTRO SUR COLOMBIANO DE LOGÍSTICA INTERNACIONAL",
            "codigo_regional": "52",
        },
        {
            "codigo_centro": "9535",
            "nombre_centro": "CENTRO AGROINDUSTRIAL Y PESQUERO DE LA COSTA PACÍFICA",
            "codigo_regional": "52",
        },
        {
            "codigo_centro": "9536",
            "nombre_centro": "CENTRO INTERNACIONAL DE PRODUCCIÓN LIMPIA - LOPE",
            "codigo_regional": "52",
        },
        {
            "codigo_centro": "9119",
            "nombre_centro": "CENTRO DE FORMACIÓN PARA EL DESARROLLO RURAL Y MINERO",
            "codigo_regional": "54",
        },
        {
            "codigo_centro": "9537",
            "nombre_centro": "CENTRO DE LA INDUSTRIA, LA EMPRESA Y LOS SERVICIOS",
            "codigo_regional": "54",
        },
        {
            "codigo_centro": "9120",
            "nombre_centro": "CENTRO AGROINDUSTRIAL",
            "codigo_regional": "63",
        },
        {
            "codigo_centro": "9231",
            "nombre_centro": "CENTRO PARA EL DESARROLLO TECNOLÓGICO DE LA CONSTRUCCIÓN Y LA INDUSTRIA",
            "codigo_regional": "63",
        },
        {
            "codigo_centro": "9538",
            "nombre_centro": "CENTRO DE COMERCIO Y TURISMO",
            "codigo_regional": "63",
        },
        {
            "codigo_centro": "9121",
            "nombre_centro": "CENTRO ATENCIÓN SECTOR AGROPECUARIO",
            "codigo_regional": "66",
        },
        {
            "codigo_centro": "9223",
            "nombre_centro": "CENTRO DE DISEÑO E INNOVACIÓN TECNOLÓGICA INDUSTRIAL",
            "codigo_regional": "66",
        },
        {
            "codigo_centro": "9308",
            "nombre_centro": "CENTRO DE COMERCIO Y SERVICIOS",
            "codigo_regional": "66",
        },
        {
            "codigo_centro": "9122",
            "nombre_centro": "CENTRO ATENCION SECTOR AGROPECUARIO",
            "codigo_regional": "68",
        },
        {
            "codigo_centro": "9224",
            "nombre_centro": "CENTRO INDUSTRIAL DE MANTENIMIENTO INTEGRAL",
            "codigo_regional": "68",
        },
        {
            "codigo_centro": "9225",
            "nombre_centro": "CENTRO INDUSTRIAL DEL DISEÑO Y LA MANUFACTURA",
            "codigo_regional": "68",
        },
        {
            "codigo_centro": "9309",
            "nombre_centro": "CENTRO DE SERVICIOS EMPRESARIALES Y TURÍSTICOS",
            "codigo_regional": "68",
        },
        {
            "codigo_centro": "9540",
            "nombre_centro": "CENTRO INDUSTRIAL Y DEL DESARROLLO TECNOLOGICO",
            "codigo_regional": "68",
        },
        {
            "codigo_centro": "9541",
            "nombre_centro": "CENTRO AGROTURÍSTICO",
            "codigo_regional": "68",
        },
        {
            "codigo_centro": "9545",
            "nombre_centro": "CENTRO AGROEMPRESARIAL Y TURISTICO DE LOS ANDES",
            "codigo_regional": "68",
        },
        {
            "codigo_centro": "9546",
            "nombre_centro": "CENTRO DE GESTION AGROEMPRESARIAL DEL ORIENTE",
            "codigo_regional": "68",
        },
        {
            "codigo_centro": "9542",
            "nombre_centro": "CENTRO DE LA INNOVACION, LA TECNOLOGIA Y LOS SERVICIOS",
            "codigo_regional": "70",
        },
        {
            "codigo_centro": "9123",
            "nombre_centro": "CENTRO AGROPECUARIO LA GRANJA",
            "codigo_regional": "73",
        },
        {
            "codigo_centro": "9226",
            "nombre_centro": "CENTRO DE INDUSTRIA Y CONSTRUCCION",
            "codigo_regional": "73",
        },
        {
            "codigo_centro": "9310",
            "nombre_centro": "CENTRO DE COMERCIO Y SERVICIOS",
            "codigo_regional": "73",
        },
        {
            "codigo_centro": "9124",
            "nombre_centro": "CENTRO AGROPECUARIO DE BUGA",
            "codigo_regional": "76",
        },
        {
            "codigo_centro": "9125",
            "nombre_centro": "CENTRO LATINOAMERICANO DE ESPECIES MENORES",
            "codigo_regional": "76",
        },
        {
            "codigo_centro": "9126",
            "nombre_centro": "CENTRO NAUTICO PESQUERO DE BUENAVENTURA",
            "codigo_regional": "76",
        },
        {
            "codigo_centro": "9227",
            "nombre_centro": "CENTRO DE ELECTRICIDAD Y AUTOMATIZACION INDUSTRIAL - CEAI",
            "codigo_regional": "76",
        },
        {
            "codigo_centro": "9228",
            "nombre_centro": "CENTRO DE LA CONSTRUCCION",
            "codigo_regional": "76",
        },
        {
            "codigo_centro": "9229",
            "nombre_centro": "CENTRO DE DISEÑO TECNOLOGICO INDUSTRIAL",
            "codigo_regional": "76",
        },
        {
            "codigo_centro": "9230",
            "nombre_centro": "CENTRO NACIONAL DE ASISTENCIA TECNICA A LA INDUSTRIA - ASTIN",
            "codigo_regional": "76",
        },
        {
            "codigo_centro": "9311",
            "nombre_centro": "CENTRO DE GESTION TECNOLÓGICA DE SERVICIOS",
            "codigo_regional": "76",
        },
        {
            "codigo_centro": "9543",
            "nombre_centro": "CENTRO DE TECNOLOGIAS AGROINDUSTRIALES",
            "codigo_regional": "76",
        },
        {
            "codigo_centro": "9544",
            "nombre_centro": "CENTRO DE BIOTECNOLOGIA INDUSTRIAL",
            "codigo_regional": "76",
        },
        {
            "codigo_centro": "9530",
            "nombre_centro": "CENTRO DE GESTION Y DESARROLLO AGROINDUSTRIAL DE ARAUCA",
            "codigo_regional": "81",
        },
        {
            "codigo_centro": "9519",
            "nombre_centro": "CENTRO AGROINDUSTRIAL Y FORTALECIMIENTO EMPRESARIAL DE CASANARE",
            "codigo_regional": "85",
        },
        {
            "codigo_centro": "9518",
            "nombre_centro": "CENTRO AGROFORESTAL Y ACUICOLA ARAPAIMA",
            "codigo_regional": "86",
        },
        {
            "codigo_centro": "9539",
            "nombre_centro": "CENTRO DE FORMACIÓN TURÍSTICA GENTE DE MAR Y DE SERVICIOS",
            "codigo_regional": "88",
        },
        {
            "codigo_centro": "9517",
            "nombre_centro": "CENTRO PARA LA BIODIVERSIDAD Y EL TURISMO DEL AMAZONAS",
            "codigo_regional": "91",
        },
        {
            "codigo_centro": "9547",
            "nombre_centro": "CENTRO AMBIENTAL Y ECOTURISTICO DEL NORORIENTE AMAZONICO",
            "codigo_regional": "94",
        },
        {
            "codigo_centro": "9533",
            "nombre_centro": "CENTRO DE DESARROLLO AGROINDUSTRIAL, TURISTICO Y TECNOLOGICO DEL GUAVIARE",
            "codigo_regional": "95",
        },
        {
            "codigo_centro": "9548",
            "nombre_centro": "CENTRO AGROPECUARIO Y DE SERVICIOS AMBIENTALES JIRI - JIRIMO",
            "codigo_regional": "97",
        },
        {
            "codigo_centro": "9531",
            "nombre_centro": "CENTRO DE PRODUCCIÓN Y TRANSFORMACION AGROINDUSTRIAL DE LA ORINOQUÍA",
            "codigo_regional": "99",
        },
    ]

    for centro in centros:
        datos_centros = Centro(**centro)
        db.session.add(datos_centros)
    db.session.commit()


event.listen(Centro.__table__, "after_create", insert_centros)


def insert_rol(*args, **kwargs):
    roles = [
        {"id": "1", "name": "Administrador"},
        {"id": "2", "name": "Coordinador"},
        {"id": "3", "name": "Instructor"},
        {"id": "4", "name": "Aprendiz"},
    ]

    for rol in roles:
        nombre_roles = Role(**rol)
        db.session.add(nombre_roles)
    db.session.commit()


event.listen(Role.__table__, "after_create", insert_rol)


def create_admin_user():
    existing_admin = BaseUser.query.filter_by(documento="1098789300").first()
    if existing_admin:
        print("El usuario administrador ya existe.")
        return

    admin_role = Role.query.get(1)  # Obtiene el rol con ID 1
    if not admin_role:
        print(
            "Error: No se encontró el rol de Administrador con ID 1 en la base de datos."
        )
        return

    admin_user = BaseUser(
        documento="1098789300",
        nombre="Admin",
        apellido="User",
        email="admin@example.com",
        password="scrypt:32768:8:1$rJ34NsDBJ6HcEnVB$229879aafe5ce98332ffb0b1bfa6febd4b8490e2cc7b619438de8cc43d426b4d8f0017fb876b11e434facb73613fbdbac68e18ecd6699938a5047ad0f7e85bc8",  # Should be a secure password
        telefono="123456789",
    )
    db.session.add(admin_user)
    db.session.commit()

    admin_user_id = admin_user.id

    user_role = UserRole(user_id=admin_user_id, role_id=admin_role.id)
    db.session.add(user_role)
    db.session.commit()


def insert_variable(*args, **kwargs):
    variables = [
        {
            "nombre": "Relaciones Interpersonales",
            "tipo": "Actitudinal",
            "descripcion": "Desarrolla relaciones interpersonales con las personas de los diferentes niveles del ente coformador en forma armoniosa,respetuosa y enmarcada dentro de los principios de convivencia social",
        },
        {
            "nombre": "Trabajo en equipo",
            "tipo": "Actitudinal",
            "descripcion": "Participa en forma activa y propositiva en equipos de trabajo asumiendo los roles, de acuerdo a sus fortalezas.",
        },
        {
            "nombre": "solucion de problemas",
            "tipo": "Actitudinal",
            "descripcion": "Propone alternativas de solucion a situaciones problematicas en el contexto del desarrollo de su etapa productiva.",
        },
        {
            "nombre": "Cumplimiento",
            "tipo": "Actitudinal",
            "descripcion": "Asume compromiso de las funciones y responsabilidades asignadas en el desarrollo de su trabajo.",
        },
        {
            "nombre": "Organizacion",
            "tipo": "Actitudinal",
            "descripcion": "Demuestra capacidad para ordenar y disponer los elementos necesarios e informacion para facilitar la ejecucion de un trabajo y el logro de los objetivos.",
        },
        {
            "nombre": "Transferencia de conocimiento",
            "tipo": "Tecnica",
            "descripcion": "Demuestra las competencias específicas delprograma de formación en situaciones reales detrabajo.",
        },
        {
            "nombre": "Mejora continua",
            "tipo": "Tecnica",
            "descripcion": "Aporta al mejoramiento de los procesos propios de su desempeño.",
        },
        {
            "nombre": "Fortalecimiento Ocupacional",
            "tipo": "Tecnica",
            "descripcion": "Autogestiona acciones que fortalezca su perfil ocupacional en el marco de su proyecto de vida.",
        },
        {
            "nombre": "Oportunidad y calidad",
            "tipo": "Tecnica",
            "descripcion": "Presenta con oportunidad y calidad los productos generados en el desarrollo de sus funciones y actividades.",
        },
        {
            "nombre": "Responsabilidad ambiental",
            "tipo": "Tecnica",
            "descripcion": "Administra los recursos para el desarrollo de sus actividades con criterios de responsabilidad ambiental.",
        },
        {
            "nombre": "Administracion de recursos",
            "tipo": "Tecnica",
            "descripcion": "Utiliza de manera racional los materiales, equipos y herramientas suministrados para el desempeño de sus actividades o funciones",
        },
        {
            "nombre": "Seguridad ocupacional e industrial",
            "tipo": "Tecnica",
            "descripcion": "Utiliza los elementos de seguridad y salud ocupacional de acuerdo con la normatividad vigente establecida para sus actividades o funciones.",
        },
        {
            "nombre": "Documentacion etapa productiva",
            "tipo": "Tecnica",
            "descripcion": "Actualiza permanentemente el portafolio de evidencias",
        },
    ]

    for variable in variables:
        nombre_variables = Variable(**variable)
        db.session.add(nombre_variables)
    db.session.commit()


event.listen(Variable.__table__, "after_create", insert_variable)
