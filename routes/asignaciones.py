from flask import Blueprint, render_template, url_for, redirect, request
from models.seguimientos import Asignacion, Seguimiento
from utils.db import db
from routes.consultar_fichas import admin_required
from flask_login import login_required

asignaciones = Blueprint("asignaciones", __name__)


@asignaciones.route("/seguimientos")
def asignacion():
    asignaciones = Asignacion.query.all()
    for asignacion in asignaciones:
        if not asignacion.fecha_inicio_contrato:
            asignacion.fecha_inicio_contrato = "Sin actualizar"
        if not asignacion.fecha_fin_contrato:
            asignacion.fecha_fin_contrato = "Sin actualizar"
    return render_template("/seguimientos.html", asignaciones=asignaciones)
