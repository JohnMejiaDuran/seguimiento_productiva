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
from models.seguimientos import Aprendiz, Instructor, Asignacion, Role, UserRole
from utils.db import db
from sqlalchemy.exc import IntegrityError
from flask_login import login_required
from routes.consultar_fichas import admin_required
from werkzeug.security import generate_password_hash

ruta_aprendices = Blueprint("ruta_aprendices", __name__)


@ruta_aprendices.route("/aprendiz")
@login_required
@admin_required
def aprendices():
    title = "Aprendices"
    aprendices = Aprendiz.query.all()
    rol = "Administrador"
    logo = "/static/icons/user-icon.png"
    aprendiz_guardado = session.pop("aprendiz_guardado", False)

    for aprendiz in aprendices:
        # Obtener el nombre del instructor asociado a cada aprendiz
        instructor = Instructor.query.filter_by(
            documento=aprendiz.documento_instructor
        ).first()
        # Asociar el nombre del instructor

        if instructor:
            aprendiz.nombre_instructor = instructor.nombre
            aprendiz.apellido_instructor = instructor.apellido
        else:
            # Manejar caso en el que el instructor no existe o el campo documento_instructor está vacío
            aprendiz.nombre_instructor = "No asignado"
    return render_template(
        "aprendiz.html",
        title=title,
        aprendices=aprendices,
        rol=rol,
        logo=logo,
        aprendiz_guardado=aprendiz_guardado,
    )


@ruta_aprendices.route("/guardar_aprendices", methods=["POST"])
@login_required
def guardar_aprendices():
    if request.method == "POST" and "asignar_instructor" in request.form:
        ficha_sin_decimal = request.form.get("ficha_sin_decimal")
        programa = request.form.get("programa")
        document_instructor = request.form.get("instructorSelect")
        fecha_inicio = request.form.get("fecha_sin_hora_inicio")
        fecha_fin = request.form.get("fecha_sin_hora")
        fecha_asignacion = request.form.get("fecha_actual")
        telefono = ""
        email = ""
        aprendices_a_agregar = []
        asignaciones_a_agregar = []
        hay_aprendices = False

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
                if documento and nombre and apellido and alternativa:
                    aprendiz_existente = Aprendiz.query.filter_by(
                        documento=documento
                    ).first()

                    if not aprendiz_existente:
                        hay_aprendices = True
                        aprendiz = Aprendiz(
                            documento=documento,
                            nombre=nombre,
                            apellido=apellido,
                            alternativa=alternativa,
                            ficha_sin_decimal=ficha_sin_decimal,
                            programa=programa,
                            documento_instructor=document_instructor,
                            password=hashed_password,
                            telefono=telefono,
                            email=email,
                        )
                        db.session.add(aprendiz)
                        db.session.commit()             
                        aprendiz_role = Role.query.filter_by(name="Aprendiz").first()
                        new_user_id = aprendiz.id

                        user_role = UserRole(user_id=new_user_id, role_id=aprendiz_role.id)
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
                    else:
                        print(
                            f"El aprendiz con documento {documento} ya está en la base de datos"
                        )

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
