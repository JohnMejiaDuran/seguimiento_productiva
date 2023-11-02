from flask import Blueprint,render_template,request,redirect,url_for,flash
import pandas as pd
consultar_aprendiz = Blueprint("consultar_aprendiz",__name__)

@consultar_aprendiz.route("/consultaraprendiz",methods=["GET", "POST"])
def consultaraprendiz():
    titulo = "Consultar por aprendiz"
    rol = "Administrador"
    logo_redirect = "/consultaraprendiz"
    logo = "/static/icons/icon.png"
    return render_template("consultaraprendiz.html",titulo=titulo, rol=rol,logo_redirect=logo_redirect ,logo=logo)

@consultar_aprendiz.route("/table2", methods=["GET", "POST"])
def table2():
    rol = "Administrador"
    
    if request.method == "POST":
        # Verifica si se ha enviado un archivo en la solicitud.

        if "archivo2" in request.files:
            archivo = request.files["archivo2"]
            if archivo:
                if not archivo.filename.endswith(('.xls', '.xlsx')):
                    flash('El archivo debe ser de tipo .xls o .xlsx', 'error')
                    return redirect(url_for('consultar_ficha.consultarficha'))

                df = pd.read_excel(archivo, skiprows=12)


                
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
                

        
                return render_template("table2.html",evaluar=evaluar, rol=rol)
    flash('No se ha seleccionado ningún archivo.', 'error')
    return redirect(url_for('consultar_aprendiz.consultaraprendiz'))