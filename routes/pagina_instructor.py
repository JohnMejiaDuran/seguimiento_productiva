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
)
from flask_login import login_user, logout_user, login_required
from utils.db import db
from functools import wraps
from routes.consultar_fichas import admin_required
from sqlalchemy import or_
from sqlalchemy import desc

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
    print(request.form["tipo_reunion"])
    print(request.form["documento"])
    print(request.form["aprendiz"])
    print(request.form["regional"])
    print(request.form["centro"])
    print(request.form["ficha"])
    print(request.form["programa"])
    print(request.form["razonsocial"])
    print(request.form["cargo_jefe"])
    print(request.form["nit"])
    print(request.form["telefono_jefe"])
    print(request.form["direccion"])
    print(request.form["actividades"])
    print(request.form["evidencias"])
    print(request.form["fecha_inicio_actividad"])
    print(request.form["fecha_fin_actividad"])
    print(request.form["lugar_actividad"])
    print(request.form["observaciones"])
    print(request.form["tipoInforme"])
    print(request.form["inicio_periodo"])
    print(request.form["final_periodo"])
    for variable_id, valoracion in request.form.items():
        if variable_id.startswith("satisfactorio_"):
            variable_id = variable_id.split("_")[-1]
            tipo_variable = request.form.get("tipo_" + variable_id, "")
            observacion = request.form.get("observacion_" + variable_id, "")
            # Aquí puedes guardar la valoración y observación en tu base de datos o hacer lo que necesites con ellas
            print(valoracion)
            print(observacion)
            print(tipo_variable)
            print(variable_id)
    print(request.form["observaciones_finales"])
    print(request.form["observaciones_finales_aprendiz"])
    print(request.form["juicio"])
    print(request.form["desempeño"])
    print(request.form["observaciones_desempeño"])
    return "Seguimiento guardado"


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
        .filter(
            Asignacion.documento_instructor == documento_instructor_actual,
            Aprendiz.alternativa != "Sin Alternativa",
            or_(
                Aprendiz.documento.ilike(f"%{searchbox}%"),
                Asignacion.documento_aprendiz.ilike(f"%{searchbox}%"),
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
        # Si se encuentra la asignación, obtener los datos del aprendiz
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
