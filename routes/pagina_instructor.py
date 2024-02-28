from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user

pagina_instructor = Blueprint("pagina_instructor", __name__)


@pagina_instructor.route("/inicioinstructor")
def inicioinstructor():
    title = current_user.nombre + " " + current_user.apellido
    return render_template("inicioinstructor.html", title=title)
