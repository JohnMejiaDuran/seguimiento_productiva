from flask import Flask, Blueprint, render_template,request,redirect,url_for

pagina_inicio = Blueprint("pagina_inicio",__name__)

@pagina_inicio.route("/")
def index():
    return redirect(url_for('pagina_inicio.inicio'))


@pagina_inicio.route("/login", methods=['GET','POST'])
def inicio():
    title = "Página de inicio"
    
    if request.method=='POST':
        print(request.form['username'])
        print(request.form['password'])
        return render_template("auth/paginainicio.html", title=title)
    else:
        return render_template("auth/paginainicio.html", title=title)

