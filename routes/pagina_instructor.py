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
from models.seguimientos import Aprendiz, Asignacion, Regional, Centro
from flask_login import login_user, logout_user, login_required
from utils.db import db
from functools import wraps
from routes.consultar_fichas import admin_required
from sqlalchemy import or_

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
    regionales = Regional.query.all()
    return render_template("crearseguimiento3.html", regionales=regionales)


@pagina_instructor.route("/buscar_aprendiz", methods=["POST", "GET"])
def buscar_aprendiz():
    if request.method == "POST":
        searchbox = request.form.get("text")
    elif request.method == "GET":
        searchbox = request.args.get("text")

    # Obtener el documento del instructor actual
    documento_instructor_actual = current_user.documento

    # Filtrar las asignaciones solo para el instructor actual
    asignaciones = (
        Asignacion.query.join(Aprendiz)
        .filter(
            Asignacion.documento_instructor == documento_instructor_actual,
            or_(
                Aprendiz.documento.ilike(f"%{searchbox}%"),
                Asignacion.documento_aprendiz.ilike(f"%{searchbox}%"),
            )
        )
        .all()
    )

    # Preparar los datos para enviarlos como respuesta
    resultados = [
        {"documento": asignacion.documento_aprendiz} for asignacion in asignaciones
    ]
    
    # Devolver los resultados en formato JSON
    return jsonify(resultados)


@pagina_instructor.route("/get_centros/<regional_id>", methods=["GET"])
@login_required
@instructor_required
def get_centros(regional_id):
    centros = Centro.query.filter_by(codigo_regional=regional_id).all()
    centros_data = [
        {"codigo_centro": centro.codigo_centro, "nombre_centro": centro.nombre_centro}
        for centro in centros
    ]
    return jsonify({"centros": centros_data})


@pagina_instructor.route("/crearseguimiento2")
@login_required
@instructor_required
def crearseguimiento2():
    return render_template("crearseguimiento2.html")


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
