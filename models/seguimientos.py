from utils.db import db
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

class Instructor(db.Model):
    documento = db.Column(db.Integer, primary_key=True)
    estado = db.Column(db.String(15))
    nombre = db.Column(db.String(50))
    email = db.Column(db.String(50))
    telefono = db.Column(db.String(50))

    def __init__(self,documento,estado,nombre,email,telefono):
        self.documento = documento
        self.estado = estado
        self.nombre = nombre
        self.email = email
        self.telefono = telefono

class Aprendiz(db.Model):
    documento = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50))
    apellido = db.Column(db.String(50))
    alternativa = db.Column(db.String(50))
    ficha_sin_decimal = db.Column(db.String(20))
    programa = db.Column(db.String(100))

    def __init__(self,documento,nombre,apellido,alternativa,ficha_sin_decimal,programa):
        self.documento = documento
        self.nombre = nombre
        self.apellido = apellido
        self.alternativa = alternativa
        self.ficha_sin_decimal = ficha_sin_decimal
        self.programa = programa

class Asignacion(db.Model):
    id_asignacion = db.Column(db.Integer, primary_key=True)
    documento_aprendiz = db.Column(db.Integer, ForeignKey('aprendiz.documento'))
    documento_instructor = db.Column(db.Integer, ForeignKey('instructor.documento'))
    fecha_inicio = db.Column(db.String(15)) # se extrae del excel con openpyxl
    fecha_fin = db.Column(db.String(15))# se extrae del excel con openpyxl
    fecha_asignacion = db.Column(db.String(15)) # Fecha actual
    fecha_inicio_contrato = db.Column(db.String(15)) # null, la actualiza el aprendiz
    fecha_fin_contrato = db.Column(db.String(15)) # null, la actualiza el apreniz

    aprendiz = relationship("Aprendiz", foreign_keys=[documento_aprendiz])
    instructor = relationship("Instructor", foreign_keys=[documento_instructor])

    def __init__(self,id_asignacion,documento_aprendiz,documento_instructor,fecha_inicio,fecha_fin,fecha_asignacion,fecha_inicio_contrato,fecha_fin_contrato):
        self.id_asignacion = id_asignacion
        self.documento_aprendiz = documento_aprendiz
        self.documento_instructor = documento_instructor
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.fecha_asignacion = fecha_asignacion
        self.fecha_inicio_contrato = fecha_inicio_contrato
        self.fecha_fin_contrato = fecha_fin_contrato
    