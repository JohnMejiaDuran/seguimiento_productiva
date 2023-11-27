from flask import Flask, Blueprint, render_template, request, jsonify, redirect, url_for
from models.seguimientos import Aprendiz
from utils.db import db
from sqlalchemy.exc import IntegrityError
ruta_aprendices = Blueprint("ruta_aprendices",__name__)

@ruta_aprendices.route("/aprendiz")
def aprendices():
    title = "Aprendices"
    aprendices = Aprendiz.query.all()
    rol = "Administrador"
    logo = "/static/icons/user-icon.png"
    return render_template("aprendiz.html", title=title,aprendices=aprendices,rol=rol,logo=logo)

@ruta_aprendices.route("/guardar_aprendices", methods=['POST'])
def guardar_aprendices():
    if request.method == "POST" and 'asignar_instructor' in request.form:
        ficha_sin_decimal = request.form.get("ficha_sin_decimal")
        programa = request.form.get("programa")

        aprendices_a_agregar = []
        hay_aprendices = False

        # Recorre los datos del formulario y verifica los aprendices
        for key, value in request.form.items():
            if key.startswith('documento'):
                index = key.replace('documento', '')

                documento = request.form.get(f"documento{index}")
                nombre = request.form.get(f"nombre{index}")
                apellido = request.form.get(f"apellido{index}")
                alternativa = request.form.get(f"alternativa{index}")

                if documento and nombre and apellido and alternativa:
                    aprendiz_existente = Aprendiz.query.filter_by(documento=documento).first()

                    if not aprendiz_existente:
                        hay_aprendices = True
                        aprendiz = Aprendiz(
                            documento=documento,
                            nombre=nombre,
                            apellido=apellido,
                            alternativa=alternativa,
                            ficha_sin_decimal=ficha_sin_decimal,
                            programa=programa
                        )
                        aprendices_a_agregar.append(aprendiz)
                    else:
                        print(f"El aprendiz con documento {documento} ya está en la base de datos")

        if hay_aprendices:
            try:
                db.session.add_all(aprendices_a_agregar)
                db.session.commit()
                mensaje = "Todos los aprendices fueron agregados correctamente"
                return mensaje
            except IntegrityError as e:
                db.session.rollback()
                mensaje = "Error: Al menos un aprendiz ya existe con un documento duplicado"
                return redirect(url_for('centro_formacion.centros', mensaje=mensaje))

        return "No se enviaron datos para guardar o todos los aprendices ya existen en la base de datos"

    return "Acción no permitida"

