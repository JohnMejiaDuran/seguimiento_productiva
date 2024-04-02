from flask import Blueprint, render_template, url_for, redirect, request
from models.seguimientos import Asignacion, Seguimiento, Asociacion
from utils.db import db
from routes.consultar_fichas import admin_required
from flask_login import login_required
from sqlalchemy import desc
asignaciones = Blueprint("asignaciones", __name__)


@asignaciones.route("/seguimientos")
def asignacion():
    # Obtener todas las asignaciones y asociaciones, ordenadas por fecha de inicio de contrato descendente
    asignaciones = Asignacion.query.all()
    asociaciones = Asociacion.query.order_by(desc(Asociacion.fecha_inicio_contrato)).all()

    # Crear un diccionario para almacenar la última asociación de cada aprendiz
    ultimas_asociaciones = {}
    for asociacion in asociaciones:
        if asociacion.id_aprendiz not in ultimas_asociaciones:
            ultimas_asociaciones[asociacion.id_aprendiz] = asociacion

    # Pasar las asignaciones y las últimas asociaciones a la plantilla
    return render_template("/seguimientos.html", asignaciones=asignaciones, ultimas_asociaciones=ultimas_asociaciones)