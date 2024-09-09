from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    jsonify,
)
from flask_login import current_user

from models.seguimientos import (
    Aprendiz,
    Asignacion,
    Regional,
    Asociacion,
    Empresa,
    Variable,
    Seguimiento,
    Actividades,
    Valoracion,
)
from flask_login import login_user, logout_user, login_required
from utils.db import db
from functools import wraps
from routes.consultar_fichas import admin_required
from sqlalchemy import or_
from sqlalchemy import desc
from datetime import datetime
import pdfkit
from flask import render_template_string
import os

pagina_instructor = Blueprint("pagina_instructor", __name__)


def instructor_required(fn):
    @wraps(fn)
    def decorated_view(*args, **kwargs):
        if current_user.is_authenticated and any(
            role.name == "Instructor" for role in current_user.roles
        ):
            return fn(*args, **kwargs)
        else:
            flash("No tienes acceso a esta página.")
            return redirect(url_for("pagina_inicio.index"))

    return decorated_view


@pagina_instructor.route("/inicioinstructor")
@login_required
@instructor_required
def inicioinstructor():
    title = current_user.nombre + " " + current_user.apellido
    new_password = session.pop("new_password", False)
    return render_template(
        "inicioinstructor.html", title=title, new_password=new_password
    )


@pagina_instructor.route("/aprendicesasignados")
@login_required
@instructor_required
def aprendizasignado():
    documento_usuario_actual = current_user.documento
    asignaciones = Asignacion.query.filter_by(
        documento_instructor=documento_usuario_actual
    ).all()
    for asignacion in asignaciones:
        if not asignacion.aprendiz.email:
            asignacion.aprendiz.email = "Sin actualizar"
        if not asignacion.aprendiz.telefono:
            asignacion.aprendiz.telefono = "Sin actualizar"
    title = "Aprendices"
    return render_template(
        "aprendicesasignados.html", title=title, asignaciones=asignaciones
    )


@pagina_instructor.route("/crearseguimiento3", methods=["GET", "POST"])
@login_required
@instructor_required
def crearseguimiento():
    variables = Variable.query.all()
    regionales = Regional.query.all()
    aprendiz = Aprendiz.query.all()
    return render_template(
        "crearseguimiento3.html",
        regionales=regionales,
        variables=variables,
        aprendiz=aprendiz,
    )


@pagina_instructor.route("/guardar_seguimiento", methods=["POST"])
@login_required
@instructor_required
def guardarseguimiento():
    id_instructor = current_user.documento
    print(id_instructor)
    tipo_reunion = request.form["tipo_reunion"]
    documento = request.form["documento"]
    observaciones = request.form["observaciones"]
    tipo = request.form["tipoInforme"]
    inicio_periodo = request.form["inicio_periodo"]
    final_periodo = request.form["final_periodo"]
    juicio_final = request.form.get("juicio_final")
    jefe_inmediato = request.form["jefe_inmediato"]
    cargo_jefe = request.form["cargo_jefe"]
    telefono_jefe = request.form["telefono_jefe"]
    email_jefe = request.form["email_jefe"]
    regional = request.form["regional"]
    desempeno = request.form.get("desempeno")
    reconocimiento = request.form.get("observaciones_desempeno")
    print(reconocimiento)
    observaciones_finales = request.form["observaciones_finales"]
    observaciones_finales_aprendiz = request.form["observaciones_finales_aprendiz"]
    asociacion = Asociacion.query.filter_by(id_aprendiz=documento).first()
    id_asociacion = asociacion.id_asociacion
    nombre_instructor = current_user.nombre + " " + current_user.apellido
    print(id_asociacion)
    # Create a new Seguimiento instanc
    ficha_aprendiz = Aprendiz.query.filter(Aprendiz.documento == documento).first()

    print(ficha_aprendiz.ficha.centro.nombre_centro)
    if not juicio_final:
        juicio_final = None
    if reconocimiento is None or reconocimiento == "":
        reconocimiento = None
    if not observaciones_finales:
        observaciones_finales = None
    if not observaciones_finales_aprendiz:
        observaciones_finales_aprendiz = None
    nuevo_seguimiento = Seguimiento(
        tipo_seguimiento=tipo_reunion,
        observacion=observaciones,
        fecha_inicio=inicio_periodo,
        fecha_fin=final_periodo,
        tipo=tipo,
        documento_aprendiz=documento,
        documento_instructor=id_instructor,
        id_asociacion=id_asociacion,
        reconocimiento=reconocimiento,
        juicio=juicio_final,
        observaciones_finales=observaciones_finales,
        observaciones_finales_aprendiz=observaciones_finales_aprendiz,
        nombre_instructor=nombre_instructor,
    )

    db.session.add(nuevo_seguimiento)
    db.session.commit()

    actividades = request.form.getlist("actividades[]")
    evidencias = request.form.getlist("evidencias[]")
    fechas_inicio = request.form.getlist("fecha_inicio_actividad[]")
    fechas_fin = request.form.getlist("fecha_fin_actividad[]")
    lugares = request.form.getlist("lugar_actividad[]")

    # Iterar sobre las listas y crear instancias de Actividades
    for actividad, evidencia, fecha_inicio, fecha_fin, lugar in zip(
        actividades, evidencias, fechas_inicio, fechas_fin, lugares
    ):
        nueva_actividad = Actividades(
            id_seguimiento=nuevo_seguimiento.id_seguimiento,  # Id del seguimiento recién creado
            descripcion_actividad=actividad,  # Utilizando el nombre de la actividad como descripción
            evidencia=evidencia,
            fecha_inicio=datetime.strptime(fecha_inicio, "%Y-%m-%d").date(),
            fecha_fin=datetime.strptime(fecha_fin, "%Y-%m-%d").date(),
            lugar=lugar,
        )
        db.session.add(nueva_actividad)

    db.session.commit()

    lista_valoraciones = []

    for variable_id, valoracion in request.form.items():
        if variable_id.startswith("satisfactorio_"):
            variable_id = variable_id.split("_")[-1]
            observacion = request.form.get("observacion_" + variable_id, "")
            variable_nombre = request.form.get(
                "nombre_" + variable_id, ""
            )  # Agregar este campo
            variable_descripcion = request.form.get(
                "descripcion_" + variable_id, ""
            )  # Agregar este campo
            # Crear un diccionario para cada valoración
            valoracion_data = {
                "id_variable": variable_id,
                "valoracion": valoracion,
                "observacion": observacion,
                "nombre_variable": variable_nombre,  # Agregar el nombre de la variable
                "descripcion_variable": variable_descripcion,  # Agregar la descripción de la variable
            }
            lista_valoraciones.append(valoracion_data)
            # Guardar las valoraciones en la base de datos
            valoracion_aprendiz = Valoracion(
                id_variable=variable_id,
                id_seguimiento=nuevo_seguimiento.id_seguimiento,
                valoracion=valoracion,
                observacion=observacion,
            )
            db.session.add(valoracion_aprendiz)
    print(lista_valoraciones)
    # Commit después de agregar todas las valoraciones
    db.session.commit()
    asignacion = Asignacion.query.filter_by(documento_aprendiz=documento).first()
    asociacion = (
        Asociacion.query.filter_by(id_aprendiz=documento)
        .order_by(desc(Asociacion.id_asociacion))
        .first()
    )
    if asociacion:
        nit = asociacion.nit_empresa
        empresa = Empresa.query.filter_by(nit=nit).first()

        if empresa:
            # Si se encuentra la empresa, obtener sus datos
            razon_social = empresa.razon_social
            direccion = empresa.direccion

    lista_actividades = []

    for actividad, evidencia, fecha_inicio, fecha_fin, lugar in zip(
        actividades, evidencias, fechas_inicio, fechas_fin, lugares
    ):
        nueva_actividad = {
            "descripcion_actividad": actividad,
            "evidencia": evidencia,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "lugar": lugar,
        }
        lista_actividades.append(nueva_actividad)

    fecha_actual = datetime.now()
    fecha_formateada = fecha_actual.strftime("%d/%m/%Y")
    data = {
        "regional": regional,
        "centro": ficha_aprendiz.ficha.centro.nombre_centro,
        "programa": ficha_aprendiz.ficha.programa,
        "ficha": ficha_aprendiz.ficha_id,
        "nombre_aprendiz": ficha_aprendiz.nombre + " " + ficha_aprendiz.apellido,
        "documento_aprendiz": documento,
        "telefono_aprendiz": "Sin actualizar",
        "email_aprendiz": "Sin actualizar",
        "alternativa": ficha_aprendiz.alternativa,
        "razon_social": razon_social,
        "nit": nit,
        "direccion": direccion,
        "jefe_inmediato": jefe_inmediato,
        "cargo_jefe": cargo_jefe,
        "telefono_jefe": telefono_jefe,
        "email_jefe": email_jefe,
        "actividades": lista_actividades,
        "observaciones_actividades": observaciones,
        "tipo_informe": tipo,
        "periodo_inicio": inicio_periodo,
        "periodo_finalizacion": final_periodo,
        "valoraciones": lista_valoraciones,
        "observaciones_ente": observaciones_finales,
        "observaciones_aprendiz": observaciones_finales_aprendiz,
        "juicio_final": juicio_final,
        "reconocimiento_especial": desempeno,
        "reconocimiento": reconocimiento,
        "fecha_actual": fecha_formateada,
    }
    path_to_wkhtmltopdf = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
    # def convertir_html_a_pdf(data):
    #     path_to_wkhtmltopdf = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
    #     html_content = render_template("formato.html", data=data)

    #     # Guardar el HTML generado en un archivo temporal
    #     with open("temp.html", "w", encoding="utf-8") as f:
    #         f.write(html_content)

    #     path_to_file = "temp.html"  # Ruta al archivo HTML generado
    #     config = pdfkit.configuration(wkhtmltopdf=path_to_wkhtmltopdf)

    #     # Opciones de PDF para especificar tamaño de página y escala
    #     css_path = os.path.join(os.getcwd(), "static", "src", "formato.css")
    #     pdf_options = {
    #         "page-size": "A4",
    #         "zoom": 0.5,  # Escala del 100%, sin escalamiento
    #         "print-media-type": None,  # Imprimir usando estilos de medios
    #         "enable-local-file-access": None,  # Permitir acceso a archivos locales
    #         "user-style-sheet": css_path,  # Ruta al archivo CSS
    #     }

    #     try:
    #         pdfkit.from_file(
    #             path_to_file,
    #             output_path="formatoseguimiento.pdf",
    #             configuration=config,
    #             options=pdf_options,
    #         )
    #     except OSError as e:
    #         print("Error al convertir HTML a PDF:", e)

    # # Llamada a la función con los datos necesarios
    # convertir_html_a_pdf(data)
    html_content = render_template("formato.html", data=data)

    # Guardar el HTML generado en un archivo temporal
    with open("temp.html", "w", encoding="utf-8") as f:
        f.write(html_content)

    # Ruta al archivo HTML generado
    path_to_file = "temp.html"

    # Configuración de pdfkit con la ruta al ejecutable
    config = pdfkit.configuration(wkhtmltopdf=path_to_wkhtmltopdf)

    # Generar el archivo PDF
    try:
        pdfkit.from_file(path_to_file, "output.pdf", configuration=config)
        print("Archivo PDF generado con éxito.")
    except Exception as e:
        print("Error al generar el archivo PDF:", e)



    return render_template("formato.html", data=data)


@pagina_instructor.route("/formato_seguimiento")
def formato_seguimiento():
    return render_template("/formato.html")


@pagina_instructor.route("/buscar_aprendiz", methods=["POST", "GET"])
def buscar_aprendiz():
    if request.method == "POST":
        searchbox = request.form.get("text")
    elif request.method == "GET":
        searchbox = request.args.get("text")

    # Obtener el documento del instructor actual
    documento_instructor_actual = current_user.documento

    # Filtrar las asignaciones solo para el instructor actual y con alternativa diferente a "Sin Alternativa"
    asignaciones = (
        Asignacion.query.join(Aprendiz)
        .join(Asociacion)  # Unimos con la tabla Asociacion
        .filter(
            Asignacion.documento_instructor == documento_instructor_actual,
            Aprendiz.alternativa != "Sin Alternativa",
            or_(
                Aprendiz.documento.ilike(f"%{searchbox}%"),
                Asignacion.documento_aprendiz.ilike(f"%{searchbox}%"),
                Asociacion.id_aprendiz.ilike(
                    f"%{searchbox}%"
                ),  # Validar documento en Asociacion
            ),
        )
        .all()
    )
    print("Resultados de la consulta SQL:", asignaciones)

    # Preparar los datos para enviarlos como respuesta
    resultados = [
        {"documento": asignacion.documento_aprendiz} for asignacion in asignaciones
    ]

    # Devolver los resultados en formato JSON
    return jsonify(resultados)


# @pagina_instructor.route("/get_centros/<regional_id>", methods=["GET"])
# @login_required
# @instructor_required
# def get_centros(regional_id):
#     centros = Centro.query.filter_by(codigo_regional=regional_id).all()
#     centros_data = [
#         {"codigo_centro": centro.codigo_centro, "nombre_centro": centro.nombre_centro}
#         for centro in centros
#     ]
#     return jsonify({"centros": centros_data})


@pagina_instructor.route("/get_aprendiz/<documento>", methods=["GET"])
@login_required
@instructor_required
def aprendiz(documento):
    # Buscar la asignación del aprendiz basada en el número de documento
    asignacion = Asignacion.query.filter_by(documento_aprendiz=documento).first()
    asociacion = (
        Asociacion.query.filter_by(id_aprendiz=documento)
        .order_by(desc(Asociacion.id_asociacion))
        .first()
    )

    if asignacion:
        # Si se encuentra la asignación, obtener los datos de la empresa del aprendiz
        nit = None
        razon_social = None
        telefono = None
        direccion = None
        email = None

        if asociacion:
            nit = asociacion.nit_empresa
            empresa = Empresa.query.filter_by(nit=nit).first()

            if empresa:
                # Si se encuentra la empresa, obtener sus datos
                razon_social = empresa.razon_social
                telefono = empresa.telefono
                direccion = empresa.direccion
                email = empresa.email

        aprendiz = asignacion.aprendiz
        nombre_aprendiz = aprendiz.nombre
        apellido_aprendiz = aprendiz.apellido

        # Obtener la información adicional del aprendiz (ficha, centro y regional)
        ficha = aprendiz.ficha
        codigo_ficha = ficha.id_ficha
        programa = ficha.programa

        centro = ficha.centro
        nombre_centro = centro.nombre_centro

        regional = centro.regional
        nombre_regional = regional.nombre_regional

        # Establecer los valores predeterminados si no se encuentra una empresa asociada
        if nit is None:
            nit = "No disponible"
            razon_social = "No disponible"
            telefono = "No disponible"
            direccion = "No disponible"
            email = "No disponible"

        # Construir el diccionario con la información del aprendiz
        aprendiz_data = {
            "nombre_aprendiz": nombre_aprendiz,
            "apellido_aprendiz": apellido_aprendiz,
            "nombre_centro": nombre_centro,
            "nombre_regional": nombre_regional,
            "programa": programa,
            "codigo_ficha": codigo_ficha,
            "nit": nit,
            "razon_social": razon_social,
            "direccion": direccion,
            "email": email,
            "telefono": telefono,
        }

        return jsonify(aprendiz_data)
    else:
        # Si no se encuentra la asignación, devolver un mensaje de error
        flash("No se encontró ningún aprendiz con ese número de documento.", "error")
        return (
            jsonify(
                {"error": "No se encontró ningún aprendiz con ese número de documento"}
            ),
            404,
        )


@pagina_instructor.route(
    "/cambio_contrasena",
)
@login_required
@instructor_required
def cambiocontrasena():
    diferentes = session.pop("diferentes", False)

    return render_template(
        "auth/cambiocontrasena.html",
        diferentes=diferentes,
    )


@pagina_instructor.route("/confirmar_contrasena", methods=["POST"])
@login_required
@instructor_required
def confirmarcontrasena():
    if request.method == "POST":
        new_password = request.form["new_password"]
        confirm_new_password = request.form["confirm_new_password"]

        # Verificar si las contraseñas coinciden
        if new_password != confirm_new_password:
            session["diferentes"] = True
            return redirect(url_for("pagina_instructor.cambiocontrasena"))

        usuario_actual = current_user

        usuario_actual.change_password(new_password)

        db.session.commit()
        session["new_password"] = True
        return redirect(url_for("pagina_instructor.inicioinstructor"))
    session.pop("diferentes", None)
    session.pop("new_password", None)
