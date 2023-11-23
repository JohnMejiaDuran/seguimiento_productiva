from flask import render_template, request, Blueprint, url_for,redirect,flash
import pandas as pd
from models.seguimientos import Instructor
from datetime import datetime, timedelta
import xlrd
from werkzeug.utils import secure_filename
from openpyxl import load_workbook
import os
import tempfile
from io import BytesIO


consultar_ficha = Blueprint("consultar_ficha", __name__)


@consultar_ficha.route("/consultar_fichas", methods=["GET", "POST"])
def consultarficha():
    titulo = "Consultar por fichass"
    rol = "Empresario"
    logo = "/static/icons/icon.png"
    
    return render_template("consultar_fichas.html",titulo=titulo, rol=rol,logo=logo)


@consultar_ficha.route("/table", methods=["GET", "POST"])
def table():
    rol = "Empresario"
    instructores = Instructor.query.all()

    if request.method == "POST":
        # Verifica si se ha enviado un archivo en la solicitud.

        if "archivo" in request.files:
            archivo = request.files["archivo"]
            
            contenido_archivo = archivo.read()
            memoria_archivo = BytesIO(contenido_archivo)
            workbook_xls = xlrd.open_workbook(file_contents=memoria_archivo.read())

            sheet = workbook_xls.sheet_by_index(0)
            ficha = sheet.cell_value(2, 2)
            ficha_sin_decimal = str(int(ficha))
            
            programa = sheet.cell_value(5, 2)

            fecha_excel = sheet.cell_value(8,2)
            if isinstance(fecha_excel, float):
                fecha_python = xlrd.xldate_as_datetime(fecha_excel, 0)# El segundo argumento es el modo de fecha en Excel
                fecha_sin_hora = fecha_python.date()
                fecha_actual = datetime.now().date()
                
                ficha_en_vigencia = True
                if fecha_sin_hora + timedelta(days=548) < fecha_actual:
                    ficha_en_vigencia = False
                
            else:
                print("No es un valor de fecha en Excel en la celda especificada.")

            if archivo:
                if not archivo.filename.endswith(('.xls', '.xlsx')):
                    flash('El archivo debe ser de tipo .xls o .xlsx', 'error')
                    return redirect(url_for('consultar_ficha.consultarficha'))

                df = pd.read_excel(archivo, skiprows=12)

            #########################################################################
        #APRENDICES CON ETAPA ELECTIVA APROBADA


                en_formacion = df[(df["Estado"] == "EN FORMACION") & (df["Competencia"] != "2 - RESULTADOS DE APRENDIZAJE ETAPA PRÁCTICA")] #primero lista los aprendices con estado en formacion y no tiene en cuenta el resultado de la etapa practica

                conteo_por_persona_aprobada = en_formacion[en_formacion['Juicio de Evaluación'] == 'APROBADO'].groupby(['Nombre', 'Número de Documento','Estado','Apellidos']).size() # el aprendiz debe tener los jucios de evaluacion aprobados y los agrupa por nombre, documento, estado y apellidos
                
                documentos = en_formacion.groupby('Nombre')['Número de Documento'].size()-1 # Cuenta cuantos juicios tiene cada aprendiz mediante la cedula y le resta 1 que es la practica

                aprendices_aprobados = conteo_por_persona_aprobada[conteo_por_persona_aprobada.eq(documentos)].reset_index() # conteo por persona aprobada debe ser igual al conteo de documentos -1 ya que no contamos el resultado de la etapa practica

           #########################################################################
        #APRENDICES CON JUICIOS PENDIENTES

                competencias_por_evaluar = df[(df["Juicio de Evaluación"] == "POR EVALUAR")&(df["Estado"]=="EN FORMACION")&(df["Competencia"] != "2 - RESULTADOS DE APRENDIZAJE ETAPA PRACTICA")]

                practicasporevaluar = df[
                        (
                            df["Competencia"]
                            == "2 - RESULTADOS DE APRENDIZAJE ETAPA PRACTICA"
                        )
                        & (df["Juicio de Evaluación"] == "POR EVALUAR")   
                ]

                evaluar = competencias_por_evaluar[~(
                        df["Número de Documento"].isin(
                            practicasporevaluar
                        )
                    )]
                
            #########################################################################
                #APRENDICES CON NOVEDADES
                # 
                aprendices_novedades = df[df["Estado"] != "EN FORMACION"]

                # Luego puedes aplicar drop_duplicates
                novedades = aprendices_novedades.drop_duplicates(subset=('Número de Documento')).reset_index()

                # Extracción de datos, ficha, fechas y validar si la ficha aun es vigente

                

                


                return render_template("table.html", aprendices_aprobados=aprendices_aprobados, evaluar=evaluar,
                                       novedades=novedades, rol=rol, instructores=instructores, ficha_sin_decimal=ficha_sin_decimal, programa=programa,ficha_en_vigencia=ficha_en_vigencia)
            
                

    flash('No se ha seleccionado ningún archivo.', 'error')
    return redirect(url_for('consultar_ficha.consultarficha'))



    


                    

