from models.seguimientos import User


class ModelUser:
    @classmethod
    def login(cls, documento, password):
        try:
            # Realiza la consulta utilizando SQLAlchemy
            user_from_db = User.query.filter_by(documento=documento).first()
            if user_from_db is not None:
                # Comprueba la contraseña utilizando el método de la clase User
                if User.check_password(user_from_db.password, password):
                    return user_from_db
            return None

        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def get_by_id(cls, id_usuario):
        try:
            # Realiza la consulta utilizando SQLAlchemy
            user_from_db = User.query.get(id_usuario)
            return user_from_db

        except Exception as ex:
            raise Exception(ex)
