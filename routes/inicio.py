from flask import Flask, Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from routes.consultar_fichas import consultarficha
from models.ModelUser import ModelUser
from models.seguimientos import User


pagina_inicio = Blueprint("pagina_inicio", __name__)


@pagina_inicio.route("/")
def index():
    return redirect(url_for("pagina_inicio.inicio"))


@pagina_inicio.route("/login", methods=["GET", "POST"])
def inicio():
    title = "Página de inicio"

    if request.method == "POST":
        documento = request.form["documento"]
        password = request.form["password"]
        logged_user = ModelUser.login(documento, password)
        if logged_user:
            login_user(logged_user)
            return redirect(url_for("consultar_ficha.consultarficha"))
        else:
            flash("Usuario o contraseña no válidos")
            return render_template("auth/paginainicio.html", title=title)
    else:
        return render_template("auth/paginainicio.html", title=title)


@pagina_inicio.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("pagina_inicio.index"))


@pagina_inicio.errorhandler(401)
def unauthorized(error):
    return redirect(url_for("pagina_inicio.index"))

@pagina_inicio.errorhandler(404)
def status_404(error):
    return "<h1>Página no encontrada</h1>"