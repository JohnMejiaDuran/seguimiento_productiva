from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import current_user
from models.seguimientos import Empresa, Asociacion
from utils.db import db

empresa = Blueprint("empresa", __name__)


@empresa.route("/empresas")
def empresas():
    empresa_data = Empresa.query.all()
    empresa_guardada = session.pop("empresa_guardada", False)
    return render_template("empresas.html", empresa_data=empresa_data, empresa_guardada=empresa_guardada)


@empresa.route("/registroempresa")
def registroempresa():
    ya_existe_empresa = session.pop("ya_existe_empresa", False)
    return render_template(
        "registroempresa.html", ya_existe_empresa=ya_existe_empresa
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
        return redirect(url_for("empresa.registroempresa", ya_existe_empresa=ya_existe_empresa))
        
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
    
