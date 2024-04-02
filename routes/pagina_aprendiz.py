from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import current_user
from models.seguimientos import Empresa, Asociacion
from utils.db import db

pagina_aprendiz = Blueprint("pagina_aprendiz", __name__)


@pagina_aprendiz.route("/inicioaprendiz")
def inicioaprendiz():
    logo = "/static/icons/user-icon.png"
    title = current_user.nombre + " " + current_user.apellido
    return render_template("inicioaprendiz.html", title=title, logo=logo)


@pagina_aprendiz.route("/empresas")
def empresas():
    empresas = Empresa.query.all()
    return render_template("empresas.html", empresas=empresas)


@pagina_aprendiz.route("/registroempresa")
def registroempresa():
    asociacion_exitosa = session.pop("asociacion", False)
    return render_template(
        "registroempresa.html", asociacion_exitosa=asociacion_exitosa
    )


@pagina_aprendiz.route("/guardar_empresa", methods=["POST"])
def guardarempresas():
    id_empresa = request.form["nit"]
    razon_social = request.form["razonsocial"]
    direccion = request.form["direccion"]
    telefono = request.form["telefono"]
    email = request.form["email"]

    id_aprendiz = current_user.documento
    print(id_aprendiz)
    print(type(id_aprendiz))
    empresa_existente = Empresa.query.filter_by(nit=id_empresa).first()

    if not empresa_existente:
        nueva_empresa = Empresa(
            nit=id_empresa,
            razon_social=razon_social,
            direccion=direccion,
            telefono=telefono,
            email=email,
        )
        db.session.add(nueva_empresa)
        db.session.commit()
    else:
        # Si la empresa ya existe, se obtiene su ID
        id_empresa = empresa_existente.nit

    # Guardar la asociación
    # Suponiendo que obtienes el ID del aprendiz de alguna manera
    nueva_asociacion = Asociacion(nit_empresa=id_empresa, id_aprendiz=id_aprendiz)
    db.session.add(nueva_asociacion)
    db.session.commit()
    asociacion_exitosa = True
    session["asociacion"] = asociacion_exitosa
    return redirect(
        url_for(
            "pagina_aprendiz.registroempresa", asociacion_exitosa=asociacion_exitosa
        )
    )
