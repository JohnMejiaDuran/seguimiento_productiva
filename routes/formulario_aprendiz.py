from flask import Flask,Blueprint,render_template

formularioaprendiz = Blueprint("formularioaprendiz",__name__)

@formularioaprendiz.route("/formularioaprendiz")
def consultaraprendiz():
    return render_template("formularioaprendiz.html")