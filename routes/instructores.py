from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.seguimientos import Instructor, Role, UserRole
from utils.db import db
from flask_login import login_required
from routes.consultar_fichas import admin_required
from werkzeug.security import generate_password_hash

instructores = Blueprint("instructores", __name__)


@instructores.route("/instructores")
@login_required
@admin_required
def instructor():
    rol = "Administrador"
    title = "Registro de instructores"
    logo = "/static/icons/user-icon.png"

    instructores = Instructor.query.all()
    return render_template(
        "instructores.html", title=title, rol=rol, logo=logo, instructores=instructores
    )


@instructores.route("/registro_instructor")
@login_required
def registro_instructor():
    rol = "Administrador"

    logo = "/static/icons/user-icon.png"
    title = "Registro de instructores"
    return render_template("registro_instructor.html", title=title, rol=rol, logo=logo)


@instructores.route("/nuevo_instructor", methods=["POST"])
@login_required
def nuevo_instructor():
    documento = request.form["documento"]
    vinculacion = request.form["vinculacion"]
    nombres = request.form["nombre"]
    apellidos = request.form["apellido"]
    email = request.form.get("email")
    telefono = request.form.get("telefono")

    password = documento
    hashed_password = generate_password_hash(password)

    # Crea una nueva instancia de Instructor
    instructor_nuevo = Instructor(
        documento=documento,
        nombre=nombres,
        apellido=apellidos,
        email=email,
        password=hashed_password,
        telefono=telefono,
        vinculacion=vinculacion,
    )

    # Agrega el nuevo instructor a la sesión y realiza la confirmación
    db.session.add(instructor_nuevo)
    db.session.commit()

    instructor_role = Role.query.filter_by(name="Instructor").first()

    # Obtener el ID del nuevo instructor insertado en la tabla BaseUser
    new_user_id = instructor_nuevo.id

    # Crear una instancia de UserRole para asignar el rol de Instructor al nuevo usuario
    user_role = UserRole(user_id=new_user_id, role_id=instructor_role.id)

    # Agregar la asignación de rol a la sesión y realizar la confirmación
    db.session.add(user_role)
    db.session.commit()

    flash("Instructor guardado satisfactoriamente", "success")

    # Redirige a la página de lista de clientes después de registrar uno nuevo
    return redirect(url_for("instructores.instructor"))
