from models.seguimientos import Aprendiz, Instructor, BaseUser, Administrador, Coordinador


class ModelUser:
    @classmethod
    def login(cls, documento, password, rol):
        try:
            # Realiza la consulta utilizando SQLAlchemy
            user_from_db = None
            if rol == "Aprendiz":
                user_from_db = Aprendiz.query.filter_by(documento=documento).first()
            elif rol == "Instructor":
                user_from_db = Instructor.query.filter_by(documento=documento).first()
            elif rol == "Administrador":
                user_from_db = Administrador.query.filter_by(documento=documento).first()
            elif rol == "Coordinador":
                user_from_db = Coordinador.query.filter_by(documento=documento).first()   

            if user_from_db is not None:
                # Comprueba la contraseña utilizando el método de la clase User
                if BaseUser.check_password(user_from_db.password, password):
                    return user_from_db
            return None

        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def get_by_id(cls, id_usuario):
        try:
            # Realiza la consulta utilizando SQLAlchemy
            user_from_db = BaseUser.query.get(id_usuario)
            return user_from_db

        except Exception as ex:
            raise Exception(ex)
