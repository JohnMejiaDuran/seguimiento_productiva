from flask import Flask, Blueprint, render_template, request, jsonify
from models.seguimientos import Aprendiz
from utils.db import db
ruta_aprendices = Blueprint("ruta_aprendices",__name__)

@ruta_aprendices.route("/aprendiz")
def aprendices():
    title = "Aprendices"
    aprendices = Aprendiz.query.all()
    return render_template("aprendiz.html", title=title,aprendices=aprendices)

@ruta_aprendices.route("/guardar_aprendices", methods=['POST'])
def guardar_aprendices():
    if request.method == "POST" and 'asignar_instructor' in request.form:
        # Obtener todos los datos del formulario
        # Procesar los datos y guardarlos en la base de datos

        # Ejemplo de cómo podrías recuperar los datos de la tabla
        cantidad_filas = len([key for key in request.form if key.startswith('documento')])

        for i in range(cantidad_filas):
            documento = request.form.get(f"documento{i}")
            nombre = request.form.get(f"nombre{i}")
            apellido = request.form.get(f"apellido{i}")
            alternativa = request.form.get(f"alternativa{i}")

            if documento and nombre and apellido and alternativa:
                # Crear una instancia del modelo Aprendiz y guardar en la base de datos
                aprendiz = Aprendiz(documento=documento, nombre=nombre, apellido=apellido, alternativa=alternativa)
                db.session.add(aprendiz)

                db.session.commit()  # Confirmar los cambios en la base de datos después de agregar todos los aprendices

        return "Datos guardados en la base de datos"
    else:
        return "No se enviaron datos para guardar"


