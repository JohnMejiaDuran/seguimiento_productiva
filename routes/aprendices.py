from flask import Flask, Blueprint, render_template, request, jsonify, redirect, url_for,session
from models.seguimientos import Aprendiz,Instructor
from utils.db import db
from sqlalchemy.exc import IntegrityError
ruta_aprendices = Blueprint("ruta_aprendices",__name__)

@ruta_aprendices.route("/aprendiz")
def aprendices():
    title = "Aprendices"
    aprendices = Aprendiz.query.all()
    rol = "Administrador"
    logo = "/static/icons/user-icon.png"
    aprendiz_guardado = session.pop('aprendiz_guardado',False)

    for aprendiz in aprendices:
        # Obtener el nombre del instructor asociado a cada aprendiz
        instructor = Instructor.query.filter_by(documento=aprendiz.documento_instructor).first()
        # Asociar el nombre del instructor al aprendiz
        if instructor:
            aprendiz.nombre_instructor = instructor.nombre
        else:
            # Manejar caso en el que el instructor no existe o el campo documento_instructor está vacío
            aprendiz.nombre_instructor = "No asignado"
    return render_template("aprendiz.html", title=title,aprendices=aprendices,rol=rol,logo=logo,aprendiz_guardado=aprendiz_guardado, )

@ruta_aprendices.route("/guardar_aprendices", methods=['POST'])
def guardar_aprendices():
    if request.method == "POST" and 'asignar_instructor' in request.form:
        ficha_sin_decimal = request.form.get("ficha_sin_decimal")
        programa = request.form.get("programa")
        document_instructor = request.form.get("instructorSelect")
        
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
                            programa=programa,documento_instructor=document_instructor
                        )
                        aprendices_a_agregar.append(aprendiz)
                    else:
                        print(f"El aprendiz con documento {documento} ya está en la base de datos")

        if hay_aprendices:
            try:
                db.session.add_all(aprendices_a_agregar)
                db.session.commit()
                aprendices_guardados = True
                session['aprendiz_guardado'] = aprendices_guardados
                return redirect(url_for('ruta_aprendices.aprendices',aprendices_guardados=aprendices_guardados))
            
            except IntegrityError as e:
                db.session.rollback()
                mensaje = "Error: Al menos un aprendiz ya existe con un documento duplicado"
                return redirect(url_for('centro_formacion.centros', mensaje=mensaje))

        return "No se enviaron datos para guardar o todos los aprendices ya existen en la base de datos"

    else:
        return "Acción no permitida"

