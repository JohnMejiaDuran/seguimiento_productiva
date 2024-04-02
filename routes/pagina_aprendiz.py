from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import current_user
from models.seguimientos import Empresa, Asociacion
from utils.db import db

pagina_aprendiz = Blueprint("pagina_aprendiz", __name__)


@pagina_aprendiz.route("/inicioaprendiz")
def inicioaprendiz():
    logo = "/static/icons/user-icon.png"
    title = current_user.nombre + " " + current_user.apellido
    return render_template("inicioaprendiz.html", title=title, logo=logo)

