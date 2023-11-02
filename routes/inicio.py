from flask import Flask, Blueprint, render_template

pagina_inicio = Blueprint("pagina_inicio",__name__)

@pagina_inicio.route("/")
def inicio():
    title = "Página de inicio"
    return render_template("paginainicio.html", title=title)

