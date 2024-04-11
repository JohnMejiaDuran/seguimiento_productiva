from flask import Blueprint, render_template, url_for, redirect, request
from models.seguimientos import Asignacion, Seguimiento, Asociacion
from utils.db import db
from routes.consultar_fichas import admin_required
from flask_login import login_required
from sqlalchemy import desc
import matplotlib
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import io
import base64
from flask import send_file

reportes = Blueprint("reportes", __name__)


@reportes.route("/reportes")
def reporte():
    seguimientos_por_instructor = Seguimiento.query.all()
    data = {
        "ID": [
            seguimiento.id_seguimiento for seguimiento in seguimientos_por_instructor
        ],
        "Instructor": [
            seguimiento.nombre_instructor for seguimiento in seguimientos_por_instructor
        ],
        "Tipo": [
            seguimiento.tipo_seguimiento for seguimiento in seguimientos_por_instructor
        ],
        # Agrega más columnas según tus necesidades
    }
    df_seguimientos = pd.DataFrame(data)
    conteo_seguimientos = (
        df_seguimientos.groupby(["Instructor", "Tipo"])
        .size()
        .unstack(
            fill_value=0
        )  # Esto crea las columnas 'Presencial' y 'Virtual' y rellena los valores faltantes con 0
    )

    # Convertir el DataFrame en una lista de tuplas para facilitar la iteración
    conteo_seguimientos_list = conteo_seguimientos.reset_index().values.tolist()

    # Preparar datos para las barras
    instructors = [item[0] for item in conteo_seguimientos_list]
    presencial = [item[1] for item in conteo_seguimientos_list]
    virtual = [item[2] for item in conteo_seguimientos_list]

    # Configurar el ancho de las barras
    bar_width = 0.35
    index = range(len(instructors))

    fig, ax = plt.subplots()
    ax.bar(index, presencial, bar_width, label="Presencial")
    ax.bar([i + bar_width for i in index], virtual, bar_width, label="Virtual")

    # Agregar etiquetas con los números correspondientes a cada barra
    for i, v in enumerate(presencial):
        ax.text(i, v, str(v), ha="center", va="bottom")

    for i, v in enumerate(virtual):
        ax.text(i + bar_width, v, str(v), ha="center", va="bottom")

    # Agregar etiquetas, títulos, etc.
    ax.set_xlabel("Instructor")
    ax.set_ylabel("Cantidad de Seguimientos")
    ax.set_title("Cantidad de Seguimientos por Instructor")
    ax.set_xticks([i + bar_width / 2 for i in index])
    ax.set_xticklabels(instructors, rotation=45, ha="right")
    ax.legend()

    plt.tight_layout()

    # Convertir el gráfico a una representación HTML
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format="png")
    img_buffer.seek(0)
    img_str = base64.b64encode(img_buffer.getvalue()).decode()
    plt.close()  # Cerrar la figura para liberar memoria

    print(df_seguimientos)

    return render_template("/reportes.html", img_data=img_str)
    # img_data=img_str
