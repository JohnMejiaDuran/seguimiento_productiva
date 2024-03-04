from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user
from models.seguimientos import Aprendiz
from flask_login import login_user, logout_user, login_required

pagina_instructor = Blueprint("pagina_instructor", __name__)


@pagina_instructor.route("/inicioinstructor")
@login_required
def inicioinstructor():
    title = current_user.nombre + " " + current_user.apellido
    return render_template("inicioinstructor.html", title=title)


@pagina_instructor.route("/aprendicesasignados")
def aprendizasignado():
    documento_usuario_actual = current_user.documento
    aprendices = Aprendiz.query.filter_by(documento_instructor=documento_usuario_actual).all()
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
