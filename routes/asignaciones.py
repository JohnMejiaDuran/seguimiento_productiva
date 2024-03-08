from flask import Blueprint, render_template, url_for, redirect, request
from models.seguimientos import Asignacion
from utils.db import db
from routes.consultar_fichas import admin_required
from flask_login import login_required

asignaciones = Blueprint("asignaciones", __name__)


@asignaciones.route("/asignaciones")
def asignacion():
    asignaciones = Asignacion.query.all()
    return render_template("/asignaciones.html", asignaciones=asignaciones)
