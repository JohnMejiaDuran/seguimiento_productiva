from flask import Flask, Blueprint, render_template

pagina_error = Blueprint("error",__name__)

@pagina_error.route("/error")
def handle_type_error(e):
    return render_template('error.html', error=str(e)), 400