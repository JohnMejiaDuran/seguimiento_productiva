from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    jsonify,
)
from flask_login import current_user
from models.seguimientos import Empresa, Asociacion
from utils.db import db

empresa = Blueprint("empresa", __name__)


@empresa.route("/empresas")
def empresas():
    empresa_data = Empresa.query.all()
    empresa_guardada = session.pop("empresa_guardada", False)
    return render_template(
        "empresas.html", empresa_data=empresa_data, empresa_guardada=empresa_guardada
    )


@empresa.route("/registroempresa")
def registroempresa():
    ya_existe_empresa = session.pop("ya_existe_empresa", False)
    return render_template("registroempresa.html", ya_existe_empresa=ya_existe_empresa)


@empresa.route("/buscar_empresa", methods=["POST", "GET"])
def buscarempresa():
    if request.method == "POST":
        searchbox = request.form.get("text")
    elif request.method == "GET":
        searchbox = request.args.get("text")

    # Filtrar las asignaciones solo para el instructor actual
    empresas_encontradas = Empresa.query.filter(
        Empresa.nit.ilike(f"%{searchbox}%")
    ).all()

    # Preparar los datos para enviarlos como respuesta
    resultados_empresas = [{"nit": empresa.nit} for empresa in empresas_encontradas]
    # Devolver los resultados en formato JSON
    return jsonify(resultados_empresas)


@empresa.route("/get_empresa/<nit>", methods=["GET"])
def encontrar_empresa(nit):
    buscar_empresa = Empresa.query.filter_by(nit=nit).first()

    if buscar_empresa:
        razon_social = buscar_empresa.razon_social
        direccion = buscar_empresa.direccion
        telefono = buscar_empresa.telefono
        email = buscar_empresa.email

        empresa_data = {
            "razon_social": razon_social,
            "direccion": direccion,
            "telefono": telefono,
            "email": email,
        }

        return jsonify(empresa_data)
    else:
        # Si no se encuentra la asignación, devolver un mensaje de error
        return jsonify(
            {"error": "No se encontró ningún aprendiz con ese número de documento."}
        )


@empresa.route("/guardar_empresa", methods=["POST"])
def guardarempresas():
    id_empresa = request.form["nit"]
    razon_social = request.form["razonsocial"]
    direccion = request.form["direccion"]
    telefono = request.form["telefono"]
    email = request.form["email"]

    # id_aprendiz = current_user.documento
    # print(id_aprendiz)
    # print(type(id_aprendiz))
    empresa_existente = Empresa.query.filter_by(nit=id_empresa).first()

    if empresa_existente:
        ya_existe_empresa = True
        session["ya_existe_empresa"] = ya_existe_empresa
        return redirect(
            url_for("empresa.registroempresa", ya_existe_empresa=ya_existe_empresa)
        )

    else:
        nueva_empresa = Empresa(
            nit=id_empresa,
            razon_social=razon_social,
            direccion=direccion,
            telefono=telefono,
            email=email,
        )
        db.session.add(nueva_empresa)
        db.session.commit()
        empresa_guardada = True
        session["empresa_guardada"] = empresa_guardada
        return redirect(url_for("empresa.empresas", empresa_guardada=empresa_guardada))

    # # Guardar la asociación
    # # Suponiendo que obtienes el ID del aprendiz de alguna manera
    # nueva_asociacion = Asociacion(nit_empresa=id_empresa, id_aprendiz=id_aprendiz)
    # db.session.add(nueva_asociacion)
    # db.session.commit()
