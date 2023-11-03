from flask import Blueprint, render_template,request,redirect, url_for, flash
from models.seguimientos import Instructor
from utils.db import db

instructores = Blueprint("instructores",__name__)

@instructores.route("/instructores")
def instructor():
    rol = "Administrador"
    title = "Registro de instructores"
    logo = "/static/icons/user-icon.png"

    instructores = Instructor.query.all()
    return render_template("instructores.html", title=title, rol=rol,logo=logo, instructores=instructores)


@instructores.route("/registro_instructor")
def registro_instructor():
    rol = "Administrador"
    
    logo = "/static/icons/user-icon.png"
    title = "Registro de instructores"
    return render_template("registro_instructor.html", title=title,rol=rol,logo=logo)

@instructores.route("/nuevo_instructor", methods=["POST"])
def nuevo_instructor():
    documento = request.form['documento']
    estado = request.form['estado']
    nombres = request.form['nombre']
    email = request.form['email']
    telefono = request.form['telefono']
   
  
    nuevo_instructor = Instructor(documento, estado, nombres, email, telefono)

    db.session.add(nuevo_instructor)
    
    db.session.commit()

    flash("Instructor guardado satisfactoriamente", 'success')    

    # Redirige a la página de lista de clientes después de registrar uno nuevo
    return redirect(url_for('instructores.instructor'))