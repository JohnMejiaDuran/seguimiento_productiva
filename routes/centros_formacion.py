from flask import Blueprint, render_template

centro_formacion = Blueprint("centro_formacion",__name__)

@centro_formacion.route("/centros_formacion")
def centros():
    title = "Centros de formacion"
    return render_template("centros_formacion.html", title=title)

