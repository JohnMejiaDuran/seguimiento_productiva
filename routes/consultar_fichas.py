from flask import render_template, request, Blueprint, url_for,redirect,flash
import pandas as pd


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
    if request.method == "POST":
        # Verifica si se ha enviado un archivo en la solicitud.

        if "archivo" in request.files:
            archivo = request.files["archivo"]
            if archivo:
                if not archivo.filename.endswith(('.xls', '.xlsx')):
                    flash('El archivo debe ser de tipo .xls o .xlsx', 'error')
                    return redirect(url_for('consultar_ficha.consultarficha'))

                df = pd.read_excel(archivo, skiprows=12)

            #########################################################################
        #APRENDICES CON ETAPA ELECTIVA APROBADA


                en_formacion = df[(df["Estado"] == "EN FORMACION") & (df["Competencia"] != "2 - RESULTADOS DE APRENDIZAJE ETAPA PRÁCTICA")]

                conteo_por_persona_aprobada = en_formacion[en_formacion['Juicio de Evaluación'] == 'APROBADO'].groupby(['Nombre', 'Número de Documento','Estado','Apellidos']).size()
                
                documentos = en_formacion.groupby('Nombre')['Número de Documento'].size()-1

                aprendices_aprobados = conteo_por_persona_aprobada[conteo_por_persona_aprobada.eq(documentos)].reset_index()

                
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
                    )].reset_index()
                
            #########################################################################
                #APRENDICES CON NOVEDADES
                # 
                aprendices_novedades = df[df["Estado"] != "EN FORMACION"]

                # Luego puedes aplicar drop_duplicates
                novedades = aprendices_novedades.drop_duplicates(subset=('Número de Documento')).reset_index()
                return render_template("table.html", aprendices_aprobados=aprendices_aprobados,evaluar=evaluar, novedades=novedades, rol=rol)
    flash('No se ha seleccionado ningún archivo.', 'error')
    return redirect(url_for('consultar_ficha.consultarficha'))



    


                    

