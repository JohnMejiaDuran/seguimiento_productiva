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
from models.seguimientos import (
    Aprendiz,
    Asociacion,
    Asignacion,
    Role,
    UserRole,
    Ficha,
    Empresa,
    Instructor,
)
from utils.db import db
from sqlalchemy.exc import IntegrityError
from flask_login import login_required
from routes.consultar_fichas import admin_required
from werkzeug.security import generate_password_hash
from sqlalchemy.orm import aliased
from datetime import datetime

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
    instructores = Instructor.query.all()
    asociacion_exitosa = session.pop("asociacion_exitosa", False)
    aprendiz_actualizado = session.pop("aprendiz_actualizado", False)
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
        asociacion_exitosa=asociacion_exitosa,
        instructores=instructores,
        aprendiz_actualizado=aprendiz_actualizado,
    )


@ruta_aprendices.route("/buscar_empresa", methods=["POST", "GET"])
def buscarempresa():
    if request.method == "POST":
        searchbox = request.form.get("text")
    elif request.method == "GET":
        searchbox = request.args.get("text")

    # Filtrar las asignaciones solo para el instructor actual
    empresas_encontradas = Empresa.query.filter(
        Empresa.nit.ilike(f"%{searchbox}%")
    ).all()

    # Preparar los datos para enviarlos como respuesta
    resultados_empresas = [{"nit": empresa.nit} for empresa in empresas_encontradas]
    # Devolver los resultados en formato JSON
    return jsonify(resultados_empresas)


@ruta_aprendices.route("/get_empresa/<nit>", methods=["GET"])
def encontrar_empresa(nit):
    buscar_empresa = Empresa.query.filter_by(nit=nit).first()

    if buscar_empresa:
        razon_social = buscar_empresa.razon_social

        empresa_data = {"razon_social": razon_social}

        return jsonify(empresa_data)
    else:
        # Si no se encuentra la asignación, devolver un mensaje de error
        return jsonify(
            {"error": "No se encontró ningún aprendiz con ese número de documento."}
        )


@ruta_aprendices.route("/asociar_aprendiz", methods=["POST"])
def asociaraprendiz():
    # Obtener los datos del formulario
    nit_empresa = request.form.get("nit")
    fecha_inicio_str = request.form.get("fechaInicio")
    fecha_inicio = datetime.strptime(fecha_inicio_str, "%Y-%m-%d").date()

    # Obtener la fecha de fin del formulario y quitar la parte de la hora
    fecha_fin_str = request.form.get("fechaFin")
    fecha_fin = datetime.strptime(fecha_fin_str, "%Y-%m-%d").date()
    # Suponiendo que tienes una función para buscar el aprendiz por su documento
    documento_aprendiz = request.form.get(
        "aprendizDocumento"
    )  # Asegúrate de tener este campo en tu formulario
    aprendiz = Aprendiz.query.filter_by(documento=documento_aprendiz).first()

    if aprendiz:
        # Crear una nueva instancia de Asociacion
        nueva_asociacion = Asociacion(
            nit_empresa=nit_empresa,
            id_aprendiz=aprendiz.documento,
            fecha_inicio_contrato=fecha_inicio,
            fecha_fin_contrato=fecha_fin,
        )

        # Agregar la nueva asociación a la sesión y guardarla en la base de datos
        db.session.add(nueva_asociacion)
        db.session.commit()

        # Redireccionar a la ruta deseada en caso de éxito
        asociacion_exitosa = True
        session["asociacion_exitosa"] = asociacion_exitosa
        return redirect(
            url_for("ruta_aprendices.aprendices", asociacion_exitosa=asociacion_exitosa)
        )
    else:
        # Si no se encuentra el aprendiz, redireccionar a otra ruta
        return redirect(url_for("ruta_aprendices.aprendices"))


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
            print(nueva_ficha)
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
                if documento and nombre and apellido and alternativa:
                    aprendiz_existente = Aprendiz.query.filter_by(
                        documento=documento
                    ).first()
                    print(aprendiz_existente)
                    asignacion_existente = Asignacion.query.filter_by(
                        documento_aprendiz=documento
                    ).first()
                    print(asignacion_existente)
                    if aprendiz_existente and asignacion_existente:
                        # Asignar la nueva ficha al aprendiz existente si es diferente
                        if nueva_ficha:
                            if (
                                aprendiz_existente.ficha_id != nueva_ficha.id_ficha
                                or aprendiz_existente.ficha_id == nueva_ficha.id_ficha
                            ):
                                aprendiz_existente.ficha_id = nueva_ficha.id_ficha
                                aprendiz_existente.alternativa = alternativa
                                asignacion_existente.documento_instructor = (
                                    document_instructor
                                )

                                db.session.commit()
                                print(
                                    "Se ha actualizado la ficha del aprendiz existente."
                                )
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


@ruta_aprendices.route("/actualizar_aprendiz/<id_aprendiz>", methods=["GET", "POST"])
def actualizar_aprendiz(id_aprendiz):
    # Obtener todos los instructores disponibles

    if request.method == "POST":
        # Obtener los datos enviados desde el formulario
        aprendiz = Aprendiz.query.filter_by(documento=id_aprendiz).first()
        aprendiz.alternativa = request.form["alternativa"]
        db.session.commit()
        asignacion = Asignacion.query.filter_by(documento_aprendiz=id_aprendiz).first()
        asignacion.documento_instructor = request.form["instructorSelect"]

        # Guardar los cambios en la base de datos
        db.session.commit()
        aprendiz_actualizado = True
        session["aprendiz_actualizado"] = aprendiz_actualizado
        # Redirigir o mostrar un mensaje de éxito
        return redirect(
            url_for(
                "ruta_aprendices.aprendices",
                id_aprendiz=id_aprendiz,
                aprendiz_actualizado=aprendiz_actualizado,
            )
        )

    else:
        pass
