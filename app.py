from datetime import datetime
from flask import Flask, render_template, request
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_babel import Babel, lazy_gettext as _
from flask_mail import Mail, Message
from flask_mysqldb import MySQL
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configuraciones agrupadas
CONFIG = {
    "MYSQL_HOST": "localhost",
    "MYSQL_USER": "root",
    "MYSQL_PASSWORD": "",
    "MYSQL_DB": "fiat_form",
    "MAIL_SERVER": "smtp-relay.brevo.com",
    "MAIL_PORT": 587,
    "MAIL_USE_TLS": True,
    "MAIL_USE_SSL": False,
    "MAIL_USERNAME": "crowiejose@gmail.com",
    "MAIL_PASSWORD": "QvmUF9CJ8PnKTg4R",
    "SQLALCHEMY_DATABASE_URI": "mysql://root:@localhost/fiat_form",
    "SECRET_KEY": "f123"
}
app.config.update(CONFIG)

mysql, mail, db, admin, babel = MySQL(app), Mail(app), SQLAlchemy(app), Admin(app, name=_("Administración"), template_mode="bootstrap3"), Babel(app)

# Modelos de base de datos
class BaseModel(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)


# Modelos de base de datos
class SubscriptionModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    dni_cuit = db.Column(db.String(20), nullable=False)
    birthday = db.Column(db.Date, nullable=False)
    cellphone = db.Column(db.String(20), nullable=False)
    alt_phone = db.Column(db.String(20), nullable=True)
    street = db.Column(db.String(100), nullable=False)
    door_number = db.Column(db.String(10), nullable=False)
    floor = db.Column(db.String(10), nullable=True)
    apartment = db.Column(db.String(10), nullable=True)
    city = db.Column(db.String(50), nullable=False)
    province = db.Column(db.String(50), nullable=False)
    postal_code = db.Column(db.String(10), nullable=False)
    cuil = db.Column(db.String(20), nullable=True)
    marital_status = db.Column(db.String(20), nullable=False)
    subscription_number = db.Column(db.String(20), nullable=False)
    subscription_model = db.Column(db.String(50), nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    customer_advisor = db.Column(db.String(50), nullable=False)
    payment = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class VehicleModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)


class AdvisorModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)


class SubscriptionModelView(ModelView):
    column_list = [
        "first_name",
        "last_name",
        "email",
        "birthday",
        "dni_cuit",
        "cellphone",
        "street",
        "door_number",
        "subscription_number",
        "subscription_model",
        "customer_advisor",
        "formatted_created_at",  # Usamos esta columna personalizada
    ]
    
    @staticmethod
    def _format_date(view, context, model, name):
        if model.created_at:
            return model.created_at.strftime("%Y-%m-%d")
        return ""

    column_formatters = {
        'formatted_created_at': _format_date
    }

    column_labels = {
        "first_name": "Nombre",
        "last_name": "Apellido",
        "email": "Correo Electrónico",
        "birthday": "Fecha de Nacimiento",
        "dni_cuit": "DNI/CUIT",
        "cellphone": "Teléfono Móvil",
        "street": "Calle",
        "door_number": "Número de Puerta",
        "subscription_number": "Número de Suscripción",
        "subscription_model": "Modelo de Suscripción",
        "customer_advisor": "Asesor de Cliente",
        "formatted_created_at": "Fecha de Creación",
    }


# Vistas de Flask-Admin
admin.add_view(ModelView(VehicleModel, db.session, name="Modelos de Vehículos"))
admin.add_view(ModelView(AdvisorModel, db.session, name="Asesores"))
admin.add_view(
    SubscriptionModelView(SubscriptionModel, db.session, name="Suscriptores")
)


def get_locale():
    return "es"


babel.init_app(app, locale_selector=get_locale)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Recoger los datos del formulario
        data = {
            "first_name": request.form.get("first_name"),
            "last_name": request.form.get("last_name"),
            "email": request.form.get("email"),
            "dni_cuit": request.form.get("dni_cuit"),
            "birthday": request.form.get("birthday"),
            "cellphone": request.form.get("cellphone"),
            "alt_phone": request.form.get("alt_phone"),
            "street": request.form.get("street"),
            "door_number": request.form.get("door_number"),
            "floor": request.form.get("floor"),
            "apartment": request.form.get("apartment"),
            "city": request.form.get("city"),
            "province": request.form.get("province"),
            "postal_code": request.form.get("postal_code"),
            "cuil": request.form.get("cuil"),
            "marital_status": request.form.get("marital_status"),
            "subscription_number": request.form.get("subscription_number"),
            "subscription_model": request.form.get("subscription_model"),
            "payment_method": request.form.get("payment_method"),
            "customer_advisor": request.form.get("customer_advisor"),
            "payment": request.form.get("payment"),
        }

        subscription = SubscriptionModel(**data)

        # Agregar la instancia a la sesión de la base de datos
        db.session.add(subscription)

        # Confirmar la sesión para guardar los cambios en la base de datos
        db.session.commit()

        # Renderizar el template del correo con los datos
        email_content = render_template("email_template.html", **data)

        # Crear el mensaje de correo
        msg = Message(
            "Nueva Suscripción",
            sender="crowiejose@gmail.com",
            recipients=["crowiejose@gmail.com"],
        )
        msg.html = email_content  # Establece el contenido renderizado como el cuerpo del correo

        # Enviar el mensaje
        mail.send(msg)

        return "¡Gracias por tu suscripción! Hemos recibido tus datos."
    vehicles = VehicleModel.query.all()
    advisors = AdvisorModel.query.all()

    return render_template("index.html", vehicles=vehicles, advisors=advisors)


if __name__ == "__main__":
    app.run(debug=True)
