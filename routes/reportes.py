from flask import Blueprint, render_template, url_for, redirect, request
from models.seguimientos import Asignacion, Seguimiento, Asociacion
from utils.db import db
from routes.consultar_fichas import admin_required
from flask_login import login_required
from sqlalchemy import desc
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
from flask import send_file

reportes = Blueprint("reportes", __name__)


@reportes.route("/reportes")
def reporte():
    seguimientos_por_instructor = Seguimiento.query.all()
    
    seguimientos_por_instructor_dic = {}
    for seguimiento in seguimientos_por_instructor:
        if seguimiento.documento_instructor and seguimiento.nombre_instructor in seguimientos_por_instructor_dic:
            seguimientos_por_instructor_dic[seguimiento.nombre_instructor] += 1
        else:
            seguimientos_por_instructor_dic[seguimiento.nombre_instructor] = 1

    instructores = list(seguimientos_por_instructor_dic.keys())
    cantidad_seguimientos = list(seguimientos_por_instructor_dic.values())

    # Graficar
    plt.bar(instructores, cantidad_seguimientos)
    plt.xlabel("Instructor")
    plt.ylabel("Cantidad de Seguimientos")
    plt.title("Cantidad de Seguimientos por Instructor")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    # Convertir el gráfico a una representación HTML
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format="png")
    img_buffer.seek(0)
    img_str = base64.b64encode(img_buffer.getvalue()).decode()

    plt.close()  # Cerrar la figura para liberar memoria

    # Pasar el gráfico como una cadena de base64 a la plantilla HTML
    return render_template("/reportes.html", img_data=img_str)
