from flask import (
    Flask,
    Blueprint,
    render_template,
    request,
    jsonify,
    redirect,
    url_for,
    session,
)
from models.seguimientos import Aprendiz, Instructor, Asignacion, Role, UserRole, Ficha
from utils.db import db
from sqlalchemy.exc import IntegrityError
from flask_login import login_required
from routes.consultar_fichas import admin_required
from werkzeug.security import generate_password_hash
from sqlalchemy.orm import aliased

ruta_aprendices = Blueprint("ruta_aprendices", __name__)


@ruta_aprendices.route("/aprendiz")
@login_required
@admin_required
def aprendices():
    title = "Aprendices"
    rol = "Administrador"
    logo = "/static/icons/user-icon.png"
    aprendiz_guardado = session.pop("aprendiz_guardado", False)
    asignaciones = Asignacion.query.all()

    for asignacion in asignaciones:
        if not asignacion.aprendiz.email:
            asignacion.aprendiz.email = "Sin actualizar"
        if not asignacion.aprendiz.telefono:
            asignacion.aprendiz.telefono = "Sin actualizar"
    return render_template(
        "aprendiz.html",
        title=title,
        asignaciones=asignaciones,
        rol=rol,
        logo=logo,
        aprendiz_guardado=aprendiz_guardado,
    )


@ruta_aprendices.route("/guardar_aprendices", methods=["POST"])
@login_required
def guardar_aprendices():
    if request.method == "POST" and "asignar_instructor" in request.form:
        ficha = request.form.get("ficha_sin_decimal")
        programa = request.form.get("programa")
        document_instructor = request.form.get("instructorSelect")
        fecha_inicio = request.form.get("fecha_sin_hora_inicio")
        fecha_fin = request.form.get("fecha_sin_hora")
        fecha_asignacion = request.form.get("fecha_actual")
        telefono = ""
        email = ""
        codigo_centro = request.form.get("codigo_centro")
        aprendices_a_agregar = []
        asignaciones_a_agregar = []

        hay_aprendices = False
        nueva_ficha = None
        # Crear nueva ficha una vez fuera del bucle
        existing_ficha = Ficha.query.filter_by(id_ficha=ficha).first()
        if existing_ficha:
            print(f"La ficha {ficha} ya existe.")
            nueva_ficha = existing_ficha
        else:
            nueva_ficha = Ficha(
                id_ficha=ficha,
                programa=programa,
                codigo_centro=codigo_centro,
            )
            db.session.add(nueva_ficha)
            try:
                db.session.commit()
                print("Ficha guardada exitosamente.")
            except IntegrityError as e:
                db.session.rollback()
                print(f"Error al guardar la ficha: {str(e)}")

        # Recorre los datos del formulario y verifica los aprendices
        for key, value in request.form.items():
            if key.startswith("documento"):
                index = key.replace("documento", "")

                documento = request.form.get(f"documento{index}")
                nombre = request.form.get(f"nombre{index}")
                apellido = request.form.get(f"apellido{index}")
                alternativa = request.form.get(f"alternativa{index}")
                password = documento
                hashed_password = generate_password_hash(password)
                print("documento:", documento)
                print("nombre:", nombre)
                print("apellido:", apellido)
                print("alternativa:", alternativa)
                if documento and nombre and apellido and alternativa:
                    aprendiz_existente = Aprendiz.query.filter_by(
                        documento=documento
                    ).first()

                    if aprendiz_existente:
                        # Asignar la nueva ficha al aprendiz existente si es diferente
                        if nueva_ficha and aprendiz_existente.ficha_id != nueva_ficha.id_ficha:
                            aprendiz_existente.ficha_id = nueva_ficha.id_ficha
                            aprendiz_existente.alternativa = alternativa
                            db.session.commit()
                            print("Se ha actualizado la ficha del aprendiz existente.")
                            hay_aprendices = True
                            
                    else:
                        aprendiz = Aprendiz(
                            documento=documento,
                            nombre=nombre,
                            apellido=apellido,
                            alternativa=alternativa,
                            ficha_id=nueva_ficha.id_ficha if nueva_ficha else ficha,
                            password=hashed_password,
                            telefono=telefono,
                            email=email,
                        )
                        db.session.add(aprendiz)
                        db.session.commit()
                        aprendiz_role = Role.query.filter_by(name="Aprendiz").first()
                        new_user_id = aprendiz.id

                        user_role = UserRole(
                            user_id=new_user_id, role_id=aprendiz_role.id
                        )
                        aprendices_a_agregar.append(aprendiz)
                        db.session.add(user_role)
                        db.session.commit()

                        asignacion = Asignacion(
                            documento_aprendiz=documento,
                            documento_instructor=document_instructor,
                            fecha_inicio=fecha_inicio,
                            fecha_fin=fecha_fin,
                            fecha_asignacion=fecha_asignacion,
                        )
                        asignaciones_a_agregar.append(asignacion)
                        hay_aprendices = True
        print("hay_aprendices:", hay_aprendices) 
        if hay_aprendices:
            try:
                db.session.add_all(aprendices_a_agregar)
                db.session.add_all(asignaciones_a_agregar)
                db.session.commit()
                aprendices_guardados = True
                session["aprendiz_guardado"] = aprendices_guardados
                return redirect(
                    url_for(
                        "ruta_aprendices.aprendices",
                        aprendices_guardados=aprendices_guardados,
                    )
                )

            except IntegrityError as e:
                db.session.rollback()
                mensaje = (
                    "Error: Al menos un aprendiz ya existe con un documento duplicado"
                )
                return redirect(url_for("centro_formacion.centros", mensaje=mensaje))

        return "No se enviaron datos para guardar o todos los aprendices ya existen en la base de datos"
    else:
        return "Acción no permitida"

