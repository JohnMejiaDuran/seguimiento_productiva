from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user

pagina_aprendiz = Blueprint("pagina_aprendiz", __name__)


@pagina_aprendiz.route("/inicioaprendiz")
def inicioaprendiz():
    title = current_user.nombre + " " + current_user.apellido
    return render_template("inicioaprendiz.html", title=title)
