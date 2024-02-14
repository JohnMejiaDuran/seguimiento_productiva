from flask import render_template, request, Blueprint, url_for, redirect, flash, session
import pandas as pd
from models.seguimientos import Instructor
from datetime import datetime, timedelta
import xlrd
from io import BytesIO
from xlrd import XLRDError
from models.seguimientos import Aprendiz
from utils.db import db
from flask_login import login_required

consultar_ficha = Blueprint("consultar_ficha", __name__)


@consultar_ficha.route("/consultar_fichas", methods=["GET", "POST"])
@login_required
def consultarficha():
    titulo = "Consultar por fichas"
    logo = "/static/icons/user-icon.png"
    title = "Consultar fichas"

    xls = session.pop("xls_data", True)
    not_data = session.pop("not_data", True)
    return render_template(
        "consultar_fichas.html",
        titulo=titulo,
        logo=logo,
        title=title,
        xls=xls,
        not_data=not_data,
    )


# debo hacer otra ruta donde este solo la tabla y esta extraiga los datos  de la ruta llamada table que deberia llamarse validacion datos para observarlos


@consultar_ficha.route("/table", methods=["GET", "POST"])
def table():
    rol = "Empresario"
    instructores = Instructor.query.all()
    if request.method == "POST":
        # Verifica si se ha enviado un archivo en la solicitud.

        if "archivo" in request.files:
            archivo = request.files["archivo"]
            try:
                if not archivo.filename.endswith((".xls")):
                    xls = False
                    flash("Error al procesar el archivo .xls:", "error")
                    session["xls_data"] = xls
                    return redirect(url_for("consultar_ficha.consultarficha", xls=xls))

                contenido_archivo = archivo.read()
                memoria_archivo = BytesIO(contenido_archivo)
                workbook_xls = xlrd.open_workbook(file_contents=memoria_archivo.read())

                sheet = workbook_xls.sheet_by_index(0)
                ficha = sheet.cell_value(2, 2)
                ficha_sin_decimal = str(int(ficha))

                programa = sheet.cell_value(5, 2)

                fecha_excel = sheet.cell_value(8, 2)
                if isinstance(fecha_excel, float):
                    fecha_python = xlrd.xldate_as_datetime(
                        fecha_excel, 0
                    )  # El segundo argumento es el modo de fecha en Excel
                    fecha_sin_hora = fecha_python.date()
                    fecha_actual = datetime.now().date()

                    ficha_en_vigencia = True
                    if fecha_sin_hora + timedelta(days=548) < fecha_actual:
                        ficha_en_vigencia = False

                    else:
                        print(
                            "No es un valor de fecha en Excel en la celda especificada."
                        )
            except (ValueError, KeyError) as e:
                flash(f"Error en los datos del archivo Excel: {str(e)}", "error")

            if archivo:
                try:
                    df = pd.read_excel(archivo, skiprows=12)

                    #########################################################################
                    # APRENDICES CON ETAPA ELECTIVA APROBADA

                    en_formacion = df[
                        (df["Estado"] == "EN FORMACION")
                        & (
                            df["Competencia"]
                            != "2 - RESULTADOS DE APRENDIZAJE ETAPA PRÁCTICA"
                        )
                    ]  # primero lista los aprendices con estado en formacion y no tiene en cuenta el resultado de la etapa practica

                    conteo_por_persona_aprobada = (
                        en_formacion[en_formacion["Juicio de Evaluación"] == "APROBADO"]
                        .groupby(
                            ["Nombre", "Número de Documento", "Estado", "Apellidos"]
                        )
                        .size()
                    )  # el aprendiz debe tener los jucios de evaluacion aprobados y los agrupa por nombre, documento, estado y apellidos

                    documentos = (
                        en_formacion.groupby("Nombre")["Número de Documento"].size() - 1
                    )  # Cuenta cuantos juicios tiene cada aprendiz mediante la cedula y le resta 1 que es la practica

                    aprendices_aprobados = conteo_por_persona_aprobada[
                        conteo_por_persona_aprobada.eq(documentos)
                    ].reset_index()  # conteo por persona aprobada debe ser igual al conteo de documentos -1 ya que no contamos el resultado de la etapa practica

                    # Cargar los números de documento de la base de datos SQLAlchemy
                    numeros_documento_bd = db.session.query(
                        Aprendiz.documento
                    ).all()  # Suponiendo que 'session' es tu sesión SQLAlchemy y 'Aprendiz' es tu tabla
                    
                    # Convertir los números de documento a una lista
                    numeros_documento_bd_str = [(num[0]) for num in numeros_documento_bd]
                    print(numeros_documento_bd)
                    # Filtrar los aprendices basados en si sus números de documento ya están en la base de datos SQLAlchemy
                    aprendices_no_en_bd = aprendices_aprobados[
                        ~aprendices_aprobados["Número de Documento"].isin(
                            numeros_documento_bd_str
                        )
                    ]
                
                    #########################################################################
                    # APRENDICES CON JUICIOS PENDIENTES

                    competencias_por_evaluar = df[
                        (df["Juicio de Evaluación"] == "POR EVALUAR")
                        & (df["Estado"] == "EN FORMACION")
                        & (
                            df["Competencia"]
                            != "2 - RESULTADOS DE APRENDIZAJE ETAPA PRACTICA"
                        )
                    ]

                    practicasporevaluar = df[
                        (
                            df["Competencia"]
                            == "2 - RESULTADOS DE APRENDIZAJE ETAPA PRACTICA"
                        )
                        & (df["Juicio de Evaluación"] == "POR EVALUAR")
                    ]

                    evaluar = competencias_por_evaluar[
                        ~(df["Número de Documento"].isin(practicasporevaluar))
                    ]

                    #########################################################################
                    # APRENDICES CON NOVEDADES
                    #
                    aprendices_novedades = df[df["Estado"] != "EN FORMACION"]

                    # Luego puedes aplicar drop_duplicates
                    novedades = aprendices_novedades.drop_duplicates(
                        subset=("Número de Documento")
                    ).reset_index()

                    # Extracción de datos, ficha, fechas y validar si la ficha aun es vigente

                    return render_template(
                        "table.html",
                        aprendices_no_en_bd=aprendices_no_en_bd,
                        evaluar=evaluar,
                        novedades=novedades,
                        rol=rol,
                        instructores=instructores,
                        ficha_sin_decimal=ficha_sin_decimal,
                        programa=programa,
                        ficha_en_vigencia=ficha_en_vigencia,
                    )
                except (ValueError, KeyError, TypeError):
                    not_data = False
                    flash("Error en los datos del archivo Excel", "error")
                    session["not_data"] = not_data
                    return redirect(
                        url_for("consultar_ficha.consultarficha", not_data=not_data)
                    )
    else:
        return redirect(url_for("consultar_ficha.consultarficha"))
