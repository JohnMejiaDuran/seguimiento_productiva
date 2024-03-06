from flask import Blueprint, render_template, request, redirect, url_for, session
from flask_login import current_user
from models.seguimientos import Aprendiz
from flask_login import login_user, logout_user, login_required
from utils.db import db

pagina_instructor = Blueprint("pagina_instructor", __name__)


@pagina_instructor.route("/inicioinstructor")
@login_required
def inicioinstructor():
    title = current_user.nombre + " " + current_user.apellido
    new_password = session.pop("new_password", False)
    return render_template(
        "inicioinstructor.html", title=title, new_password=new_password
    )


@pagina_instructor.route("/aprendicesasignados")
def aprendizasignado():
    documento_usuario_actual = current_user.documento
    aprendices = Aprendiz.query.filter_by(
        documento_instructor=documento_usuario_actual
    ).all()
    title = "Aprendices"
    return render_template(
        "aprendicesasignados.html", title=title, aprendices=aprendices
    )


@pagina_instructor.route("/crearseguimiento")
def crearseguimiento():
    return render_template("crearseguimiento.html")


@pagina_instructor.route("/crearseguimiento2")
def crearseguimiento2():
    return render_template("crearseguimiento2.html")


@pagina_instructor.route(
    "/cambio_contrasena",
)
def cambiocontrasena():
    diferentes = session.pop("diferentes", False)

    return render_template(
        "auth/cambiocontrasena.html",
        diferentes=diferentes,
    )


@pagina_instructor.route("/confirmar_contrasena", methods=["POST"])
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
