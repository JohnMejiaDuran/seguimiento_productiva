from app import app
from utils.db import db
from routes.inicio import unauthorized, status_404
from app import csrf
from models.seguimientos import create_admin_user

with app.app_context():
    db.init_app(app)
    db.create_all()
    create_admin_user()

if __name__ == "__main__":
    csrf.init_app(app)
    app.register_error_handler(401, unauthorized)
    app.register_error_handler(404, status_404)
    app.run(debug=True)
