from utils.db import db

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


# class Aprendiz(db.Model):
#     documento = db.Column(db.Integer, primary_key=True)
#     nombre = db.Column(db.String(50))
#     apellido = db.Column(db.String(50))
#     email = db.Column(db.String(50))
#     telefono = db.Column(db.String(50))

#     def __init__(self,documento,nombre,apellido,email,telefono):
#         self.documento = documento
#         self.nombre = nombre
#         self.apellido = apellido
#         self.email = email
#         self.telefono = telefono

# class Asignacion(db.Model):
#     documento = db.Column(db.Integer, primary_key=True)
#     nombre = db.Column(db.String(50))
#     apellido = db.Column(db.String(50))
#     email = db.Column(db.String(50))
#     telefono = db.Column(db.String(50))

#     def __init__(self,documento,nombre,apellido,email,telefono):
#         self.documento = documento
#         self.nombre = nombre
#         self.apellido = apellido
#         self.email = email
#         self.telefono = telefono

    