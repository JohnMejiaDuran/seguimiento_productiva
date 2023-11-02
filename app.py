from flask import Flask
from routes.consultar_fichas import consultar_ficha
from routes.formulario_aprendiz import formularioaprendiz
from routes.consultar_aprendiz import consultar_aprendiz
from routes.inicio import pagina_inicio
app = Flask(__name__)

app.secret_key = 'your_secret_key_here'
app.register_blueprint(consultar_ficha)
app.register_blueprint(formularioaprendiz)
app.register_blueprint(pagina_inicio)
app.register_blueprint(consultar_aprendiz)