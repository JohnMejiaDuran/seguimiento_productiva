from flask import Flask
from routes.consultar_fichas import consultar_ficha
from routes.inicio import pagina_inicio
from routes.instructores import instructores
from routes.centros_formacion import centro_formacion
from routes.aprendices import ruta_aprendices
from routes.error import pagina_error
from flask_login import LoginManager
from models.ModelUser import ModelUser
from flask_wtf.csrf import CSRFProtect
from routes.pagina_instructor import pagina_instructor
from routes.pagina_aprendiz import pagina_aprendiz
from routes.asignaciones import asignaciones
app = Flask(__name__)

csrf = CSRFProtect()

login_manager_app = LoginManager(app)


@login_manager_app.user_loader
def load_user(id):
    return ModelUser.get_by_id(id)


app.secret_key = "your_secret_key_here"

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:@localhost/seguimientos"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.register_blueprint(asignaciones)
app.register_blueprint(consultar_ficha)
app.register_blueprint(pagina_inicio)
app.register_blueprint(instructores)
app.register_blueprint(centro_formacion)
app.register_blueprint(ruta_aprendices)
app.register_blueprint(pagina_error)
app.register_blueprint(pagina_instructor)
app.register_blueprint(pagina_aprendiz)