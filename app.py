from flask import Flask
from routes.consultar_fichas import consultar_ficha
from routes.formulario_aprendiz import formularioaprendiz
from routes.consultar_aprendiz import consultar_aprendiz
from routes.inicio import pagina_inicio
from routes.instructores import instructores
from routes.centros_formacion import centro_formacion
from routes.aprendices import ruta_aprendices
from routes.error import pagina_error
from flask_login import LoginManager, login_user, logout_user, login_required
from models.ModelUser import ModelUser

app = Flask(__name__)
login_manager_app = LoginManager(app)


@login_manager_app.user_loader
def load_user(id):
    return ModelUser.get_by_id(id)


app.secret_key = "your_secret_key_here"

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:@localhost/seguimientos"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.register_blueprint(consultar_ficha)
app.register_blueprint(formularioaprendiz)
app.register_blueprint(pagina_inicio)
app.register_blueprint(consultar_aprendiz)
app.register_blueprint(instructores)
app.register_blueprint(centro_formacion)
app.register_blueprint(ruta_aprendices)
app.register_blueprint(pagina_error)
