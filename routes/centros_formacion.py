from flask import Blueprint, render_template,url_for,redirect,request
from models.seguimientos import Regional, Centro
from utils.db import db
from routes.consultar_fichas import admin_required
from flask_login import login_required
centro_formacion = Blueprint("centro_formacion",__name__)

@centro_formacion.route("/centros_formacion")
@login_required
@admin_required
def centros():
    title = "Centros de formacion"
    logo = "/static/icons/user-icon.png"
    rol = "Instructor"
    regionales = Regional.query.all()
    return render_template("centros_formacion.html", title=title, regionales=regionales, logo=logo, rol=rol)

@centro_formacion.route("/guardar_centro", methods=['POST'])
def guardar_centros():
    codigo_centro = request.form['codigo_centro']
    nombre_centro = request.form['nombre_centro']
    codigo_regional = request.form['codigo_regional']

    nuevo_centro = Centro(codigo_centro, nombre_centro, codigo_regional)
    
    # Agrega el nuevo cliente a la sesión de la base de datos
    db.session.add(nuevo_centro)
    # Confirma los cambios en la base de datos
    db.session.commit()

    # flash("centro guardado satisfactoriamente", 'success')    

    # Redirige a la página de lista de clientes después de registrar uno nuevo
    return redirect(url_for('centro_formacion.centros'))