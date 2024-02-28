from flask import Flask, Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from routes.consultar_fichas import consultarficha
from routes.pagina_instructor import pagina_instructor
from routes.aprendices import aprendices
from models.ModelUser import ModelUser
from models.seguimientos import BaseUser, Role


pagina_inicio = Blueprint("pagina_inicio", __name__)


@pagina_inicio.route("/")
def index():
    return redirect(url_for("pagina_inicio.inicio"))


@pagina_inicio.route("/login", methods=["GET", "POST"])
def inicio():
    title = "Página de inicio"
    if current_user.is_authenticated:  # Verificar si el usuario ya está autenticado
        # Redirigir al usuario a la página correspondiente según su rol
        if "Instructor" in [role.name for role in current_user.roles]:
            return redirect(url_for("pagina_instructor.inicioinstructor"))
        elif "Aprendiz" in [role.name for role in current_user.roles]:
            return redirect(url_for("pagina_aprendiz.inicioaprendiz"))
        elif "Administrador" in [role.name for role in current_user.roles]:
            return redirect(url_for("consultar_ficha.consultarficha"))
        elif "Coordinador" in [role.name for role in current_user.roles]:
            return redirect(url_for("pagina_coordinador.iniciocoordinador"))
        
    if request.method == "POST":
        documento = request.form["documento"]
        password = request.form["password"]

        user = BaseUser.query.filter_by(documento=documento).first()

        if user and user.check_password(user.password, password):
            for role in user.roles:
                login_user(user, remember=True)
        if user is not None and "Instructor" in [role.name for role in user.roles]:
            return redirect(url_for("pagina_instructor.inicioinstructor"))
        elif user is not None and "Aprendiz" in [role.name for role in user.roles]:
            return redirect(url_for("pagina_aprendiz.inicioaprendiz"))
        elif user is not None and "Administrador" in [role.name for role in user.roles]:
            return redirect(url_for("consultar_ficha.consultarficha"))
        elif user is not None and "Coordinador" in [role.name for role in user.roles]:
            return redirect(url_for("pagina_coordinador.iniciocoordinador"))

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



