from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    jsonify,
)
from flask_login import current_user
from models.seguimientos import (
    Aprendiz,
    Asignacion,
    Regional,
    Asociacion,
    Empresa,
    Variable,
    Seguimiento,
    Actividades,
    Valoracion,
)
from flask_login import login_user, logout_user, login_required
from utils.db import db
from functools import wraps
from routes.consultar_fichas import admin_required
from sqlalchemy import or_
from sqlalchemy import desc
from datetime import datetime
import openpyxl
from openpyxl import Workbook, load_workbook
from openpyxl.utils import get_column_letter
from openpyxl.utils import range_boundaries
from openpyxl.styles import Font

pagina_instructor = Blueprint("pagina_instructor", __name__)


def instructor_required(fn):
    @wraps(fn)
    def decorated_view(*args, **kwargs):
        if current_user.is_authenticated and any(
            role.name == "Instructor" for role in current_user.roles
        ):
            return fn(*args, **kwargs)
        else:
            flash("No tienes acceso a esta página.")
            return redirect(url_for("pagina_inicio.index"))

    return decorated_view


@pagina_instructor.route("/inicioinstructor")
@login_required
@instructor_required
def inicioinstructor():
    title = current_user.nombre + " " + current_user.apellido
    new_password = session.pop("new_password", False)
    return render_template(
        "inicioinstructor.html", title=title, new_password=new_password
    )


@pagina_instructor.route("/aprendicesasignados")
@login_required
@instructor_required
def aprendizasignado():
    documento_usuario_actual = current_user.documento
    asignaciones = Asignacion.query.filter_by(
        documento_instructor=documento_usuario_actual
    ).all()
    for asignacion in asignaciones:
        if not asignacion.aprendiz.email:
            asignacion.aprendiz.email = "Sin actualizar"
        if not asignacion.aprendiz.telefono:
            asignacion.aprendiz.telefono = "Sin actualizar"
    title = "Aprendices"
    return render_template(
        "aprendicesasignados.html", title=title, asignaciones=asignaciones
    )


@pagina_instructor.route("/crearseguimiento3", methods=["GET", "POST"])
@login_required
@instructor_required
def crearseguimiento():
    variables = Variable.query.all()
    regionales = Regional.query.all()
    aprendiz = Aprendiz.query.all()
    return render_template(
        "crearseguimiento3.html",
        regionales=regionales,
        variables=variables,
        aprendiz=aprendiz,
    )


@pagina_instructor.route("/guardar_seguimiento", methods=["POST"])
@login_required
@instructor_required
def guardarseguimiento():
    id_instructor = current_user.documento
    print(id_instructor)
    tipo_reunion = request.form["tipo_reunion"]
    documento = request.form["documento"]
    observaciones = request.form["observaciones"]
    tipo = request.form["tipoInforme"]
    inicio_periodo = request.form["inicio_periodo"]
    final_periodo = request.form["final_periodo"]
    juicio_final = request.form.get("juicio_final")
    jefe_inmediato = request.form["jefe_inmediato"]
    cargo_jefe = request.form["cargo_jefe"]
    telefono_jefe = request.form["telefono_jefe"]
    email_jefe = request.form["email_jefe"]
    regional = request.form["regional"]
    desempeno = request.form.get("desempeno")
    print("DESEMPEÑO")
    print(desempeno)
    print(juicio_final)
    reconocimiento = request.form.get("observaciones_desempeno")
    print(reconocimiento)
    observaciones_finales = request.form["observaciones_finales"]
    observaciones_finales_aprendiz = request.form["observaciones_finales_aprendiz"]
    asociacion = Asociacion.query.filter_by(id_aprendiz=documento).first()
    id_asociacion = asociacion.id_asociacion
    nombre_instructor = current_user.nombre + " " + current_user.apellido
    print(id_asociacion)
    # Create a new Seguimiento instanc
    ficha_aprendiz = Aprendiz.query.filter(Aprendiz.documento == documento).first()

    print(ficha_aprendiz.ficha.centro.nombre_centro)
    if not juicio_final:
        juicio_final = None
    if reconocimiento is None or reconocimiento == "":
        reconocimiento = None
    if not observaciones_finales:
        observaciones_finales = None
    if not observaciones_finales_aprendiz:
        observaciones_finales_aprendiz = None
    nuevo_seguimiento = Seguimiento(
        tipo_seguimiento=tipo_reunion,
        observacion=observaciones,
        fecha_inicio=inicio_periodo,
        fecha_fin=final_periodo,
        tipo=tipo,
        documento_aprendiz=documento,
        documento_instructor=id_instructor,
        id_asociacion=id_asociacion,
        reconocimiento=reconocimiento,
        juicio=juicio_final,
        observaciones_finales=observaciones_finales,
        observaciones_finales_aprendiz=observaciones_finales_aprendiz,
        nombre_instructor=nombre_instructor,
    )

    db.session.add(nuevo_seguimiento)
    db.session.commit()

    actividades = request.form.getlist("actividades[]")
    evidencias = request.form.getlist("evidencias[]")
    fechas_inicio = request.form.getlist("fecha_inicio_actividad[]")
    fechas_fin = request.form.getlist("fecha_fin_actividad[]")
    lugares = request.form.getlist("lugar_actividad[]")

    # Iterar sobre las listas y crear instancias de Actividades
    for actividad, evidencia, fecha_inicio, fecha_fin, lugar in zip(
        actividades, evidencias, fechas_inicio, fechas_fin, lugares
    ):
        nueva_actividad = Actividades(
            id_seguimiento=nuevo_seguimiento.id_seguimiento,  # Id del seguimiento recién creado
            descripcion_actividad=actividad,  # Utilizando el nombre de la actividad como descripción
            evidencia=evidencia,
            fecha_inicio=datetime.strptime(fecha_inicio, "%Y-%m-%d").date(),
            fecha_fin=datetime.strptime(fecha_fin, "%Y-%m-%d").date(),
            lugar=lugar,
        )
        db.session.add(nueva_actividad)

    db.session.commit()

    for variable_id, valoracion in request.form.items():
        if variable_id.startswith("satisfactorio_"):
            variable_id = variable_id.split("_")[-1]
            # tipo_variable = request.form.get("tipo_" + variable_id, "")
            observacion = request.form.get("observacion_" + variable_id, "")
            # Aquí puedes guardar la valoración y observación en tu base de datos o hacer lo que necesites con ellas
            valoracion_aprendiz = Valoracion(
                id_variable=variable_id,
                id_seguimiento=nuevo_seguimiento.id_seguimiento,
                valoracion=valoracion,
                observacion=observacion,
            )
            db.session.add(valoracion_aprendiz)
        db.session.commit()
    asignacion = Asignacion.query.filter_by(documento_aprendiz=documento).first()
    asociacion = (
        Asociacion.query.filter_by(id_aprendiz=documento)
        .order_by(desc(Asociacion.id_asociacion))
        .first()
    )
    if asociacion:
        nit = asociacion.nit_empresa
        empresa = Empresa.query.filter_by(nit=nit).first()

        if empresa:
            # Si se encuentra la empresa, obtener sus datos
            razon_social = empresa.razon_social
            telefono = empresa.telefono
            direccion = empresa.direccion
            email = empresa.email
    book = openpyxl.load_workbook("formato.xlsx")

    # Seleccionar la hoja activa
    sheet = book.active

    # Modificar las celdas en la hoja activa
    sheet["C2"] = regional
    sheet["R2"] = ficha_aprendiz.ficha.centro.nombre_centro
    sheet["G3"] = ficha_aprendiz.ficha.programa
    sheet["T3"] = ficha_aprendiz.ficha_id
    sheet["J5"] = ficha_aprendiz.nombre + " " + ficha_aprendiz.apellido
    sheet["J6"] = documento
    sheet["J7"] = "Sin actualizar"
    sheet["J8"] = "Sin actualizar"
    sheet["J9"] = ficha_aprendiz.alternativa
    sheet["J10"] = razon_social
    sheet["J11"] = nit
    sheet["J12"] = direccion
    sheet["J13"] = jefe_inmediato
    sheet["J14"] = cargo_jefe
    sheet["J15"] = telefono_jefe
    sheet["J16"] = email_jefe
    # Suponiendo que 'columna' es la columna inicial en la que deseas escribir las actividades
    columna = "A"

    # Suponiendo que 'fila' es la fila inicial en la que deseas escribir las actividades
    fila = 23

    for actividad, evidencia, fecha_inicio, fecha_fin, lugar in zip(
        actividades, evidencias, fechas_inicio, fechas_fin, lugares
    ):
        print(actividad)
        print(actividades)
        celda = f"{columna}{fila}"
        sheet[celda] = actividad

        celda_evidencia = f"N{fila}"
        sheet[celda_evidencia] = evidencia

        # Escribir las fechas de inicio y fin en la misma celda con un salto de línea
        celda_fecha = f"S{fila}"
        contenido_fecha = f"{fecha_inicio}\n{fecha_fin}"
        sheet[celda_fecha] = contenido_fecha

        celda_lugar = f"V{fila}"
        sheet[celda_lugar] = lugar

        fila += 1
    sheet["A26"] = observaciones
    # Seleccionar la segunda hoja del libro

    # Marcar la casilla correspondiente según el tipo de informe
    if tipo == "parcial":
        sheet["F29"] = "PARCIAL   [X]"

    elif tipo == "final":
        sheet["F30"] = "FINAL    [X]"
    sheet["Q29"] = inicio_periodo
    sheet["Q30"] = final_periodo

    fila_actual = 34  # Fila inicial donde empezamos a escribir

    # Iterar sobre las valoraciones y observaciones y escribir en el libro de Excel
    for variable_id, valoracion in request.form.items():
        if variable_id.startswith("satisfactorio_"):
            variable_id = variable_id.split("_")[-1]
            observacion = request.form.get("observacion_" + variable_id, "")

            # Determinar las celdas dependiendo de la valoración y escribir los datos
            if valoracion == "satisfactorio":
                sheet.cell(row=fila_actual, column=16).value = "X"  # Columna P
                sheet.cell(row=fila_actual, column=21).value = observacion  # Columna U
            else:
                sheet.cell(row=fila_actual, column=19).value = "X"  # Columna S
                sheet.cell(row=fila_actual, column=21).value = observacion  # Columna U

            # Pasar a la siguiente fila
            if fila_actual == 38:
                fila_actual = 42
            elif fila_actual < 49:
                fila_actual += 1
    sheet["A52"] = observaciones_finales
    sheet["A54"] = observaciones_finales_aprendiz
    if juicio_final == "aprobado":
        sheet["A57"] = "JUICIO DE EVALUACIÓN:           APROBADO [X]        NO APROBADO"
    # Si el juicio_final es "no_aprobado"
    elif juicio_final == "no_aprobado":
        sheet["A57"] = (
            "JUICIO DE EVALUACIÓN:           APROBADO            NO APROBADO [X]"
        )
    else:
        sheet["A57"] = "JUICIO DE EVALUACIÓN:           APROBADO          NO APROBADO"

    if desempeno == "desempenoSi":
        sheet["A58"] = "RECONOCIMIENTOS ESPECIALES SOBRE EL DESEMPEÑO: SI[X]     NO"
    elif desempeno == "desempenoNo":
        sheet["A58"] = "RECONOCIMIENTOS ESPECIALES SOBRE EL DESEMPEÑO: SI     NO[X]"
    else:
        sheet["A58"] = "RECONOCIMIENTOS ESPECIALES SOBRE EL DESEMPEÑO: SI     NO"
    sheet["A60"] = reconocimiento
    # Guardar los cambios en el archivo Excel
    fecha_actual = datetime.now().strftime("%d-%m-%Y")  # Formato: Día-Mes-Año

    nombre_archivo = f"{documento}_{ficha_aprendiz.ficha_id}_{fecha_actual}.xlsx"
    book.save(nombre_archivo)
    return "Seguimiento guardado"


@pagina_instructor.route("/formato_seguimiento")
def formato_seguimiento():
    return render_template("/formato.html")


@pagina_instructor.route("/buscar_aprendiz", methods=["POST", "GET"])
def buscar_aprendiz():
    if request.method == "POST":
        searchbox = request.form.get("text")
    elif request.method == "GET":
        searchbox = request.args.get("text")

    # Obtener el documento del instructor actual
    documento_instructor_actual = current_user.documento

    # Filtrar las asignaciones solo para el instructor actual y con alternativa diferente a "Sin Alternativa"
    asignaciones = (
        Asignacion.query.join(Aprendiz)
        .join(Asociacion)  # Unimos con la tabla Asociacion
        .filter(
            Asignacion.documento_instructor == documento_instructor_actual,
            Aprendiz.alternativa != "Sin Alternativa",
            or_(
                Aprendiz.documento.ilike(f"%{searchbox}%"),
                Asignacion.documento_aprendiz.ilike(f"%{searchbox}%"),
                Asociacion.id_aprendiz.ilike(
                    f"%{searchbox}%"
                ),  # Validar documento en Asociacion
            ),
        )
        .all()
    )
    print("Resultados de la consulta SQL:", asignaciones)

    # Preparar los datos para enviarlos como respuesta
    resultados = [
        {"documento": asignacion.documento_aprendiz} for asignacion in asignaciones
    ]

    # Devolver los resultados en formato JSON
    return jsonify(resultados)


# @pagina_instructor.route("/get_centros/<regional_id>", methods=["GET"])
# @login_required
# @instructor_required
# def get_centros(regional_id):
#     centros = Centro.query.filter_by(codigo_regional=regional_id).all()
#     centros_data = [
#         {"codigo_centro": centro.codigo_centro, "nombre_centro": centro.nombre_centro}
#         for centro in centros
#     ]
#     return jsonify({"centros": centros_data})


@pagina_instructor.route("/get_aprendiz/<documento>", methods=["GET"])
@login_required
@instructor_required
def aprendiz(documento):
    # Buscar la asignación del aprendiz basada en el número de documento
    asignacion = Asignacion.query.filter_by(documento_aprendiz=documento).first()
    asociacion = (
        Asociacion.query.filter_by(id_aprendiz=documento)
        .order_by(desc(Asociacion.id_asociacion))
        .first()
    )

    if asignacion:
        # Si se encuentra la asignación, obtener los datos del aprendiz
        nit = None
        razon_social = None
        telefono = None
        direccion = None
        email = None

        if asociacion:
            nit = asociacion.nit_empresa
            empresa = Empresa.query.filter_by(nit=nit).first()

            if empresa:
                # Si se encuentra la empresa, obtener sus datos
                razon_social = empresa.razon_social
                telefono = empresa.telefono
                direccion = empresa.direccion
                email = empresa.email

        aprendiz = asignacion.aprendiz
        nombre_aprendiz = aprendiz.nombre
        apellido_aprendiz = aprendiz.apellido

        # Obtener la información adicional del aprendiz (ficha, centro y regional)
        ficha = aprendiz.ficha
        codigo_ficha = ficha.id_ficha
        programa = ficha.programa

        centro = ficha.centro
        nombre_centro = centro.nombre_centro

        regional = centro.regional
        nombre_regional = regional.nombre_regional

        # Establecer los valores predeterminados si no se encuentra una empresa asociada
        if nit is None:
            nit = "No disponible"
            razon_social = "No disponible"
            telefono = "No disponible"
            direccion = "No disponible"
            email = "No disponible"

        # Construir el diccionario con la información del aprendiz
        aprendiz_data = {
            "nombre_aprendiz": nombre_aprendiz,
            "apellido_aprendiz": apellido_aprendiz,
            "nombre_centro": nombre_centro,
            "nombre_regional": nombre_regional,
            "programa": programa,
            "codigo_ficha": codigo_ficha,
            "nit": nit,
            "razon_social": razon_social,
            "direccion": direccion,
            "email": email,
            "telefono": telefono,
        }

        return jsonify(aprendiz_data)
    else:
        # Si no se encuentra la asignación, devolver un mensaje de error
        flash("No se encontró ningún aprendiz con ese número de documento.", "error")
        return (
            jsonify(
                {"error": "No se encontró ningún aprendiz con ese número de documento"}
            ),
            404,
        )


@pagina_instructor.route(
    "/cambio_contrasena",
)
@login_required
@instructor_required
def cambiocontrasena():
    diferentes = session.pop("diferentes", False)

    return render_template(
        "auth/cambiocontrasena.html",
        diferentes=diferentes,
    )


@pagina_instructor.route("/confirmar_contrasena", methods=["POST"])
@login_required
@instructor_required
def confirmarcontrasena():
    if request.method == "POST":
        new_password = request.form["new_password"]
        confirm_new_password = request.form["confirm_new_password"]

        # Verificar si las contraseñas coinciden
        if new_password != confirm_new_password:
            session["diferentes"] = True
            return redirect(url_for("pagina_instructor.cambiocontrasena"))

        usuario_actual = current_user

        usuario_actual.change_password(new_password)

        db.session.commit()
        session["new_password"] = True
        return redirect(url_for("pagina_instructor.inicioinstructor"))
    session.pop("diferentes", None)
    session.pop("new_password", None)
