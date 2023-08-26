from datetime import datetime
from flask import Flask, render_template, request
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_babel import Babel, lazy_gettext as _
from flask_mail import Mail, Message
from flask_mysqldb import MySQL
from flask_sqlalchemy import SQLAlchemy
from PIL import Image
from PIL import ImageDraw, ImageFont
import base64
import io
import os


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
    signature = db.Column(db.Text, nullable=False)


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


def save_signature_image(signature_base64, filename):
    signature_base64 = signature_base64.split(",")[1]
    # Decodifica la cadena base64
    signature_data = io.BytesIO(base64.b64decode(signature_base64))
    # Abre la imagen usando PIL
    image = Image.open(signature_data)
    # Define la ruta donde se guardará la imagen
    path = os.path.join("signatures", filename)
    # Guarda la imagen en la ruta especificada
    image.save(path)
    # Retorna la ruta donde se guardó la imagen
    return path

def add_text_to_image(image, text, position, font_path="arial.ttf", font_size=55):
    """
    Añade texto a una imagen en una posición específica.

    :param image: Objeto Image de PIL.
    :param text: Texto que se quiere añadir.
    :param position: Una tupla (x, y) que indica dónde se debe añadir el texto.
    :param font_path: Ruta de la fuente que se quiere usar. Por defecto es Arial.
    :param font_size: Tamaño de la fuente.
    :return: Objeto Image con el texto añadido.
    """
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(font_path, font_size)
    draw.text(position, text, font=font, fill="black")
    return image


def embed_data_on_form(signature_path, data, base_image_path="solicitud/solicitud-adhesion1.png"):
    base_image = Image.open(base_image_path)
    signature_image = Image.open(signature_path)

    # Coordenadas donde quieres incrustar la firma
    position_signature = (1900, 3270)
    base_image.paste(signature_image, position_signature, signature_image)  # El último argumento es para manejar la transparencia

    full_name = (data["first_name"] + " " + data["last_name"]).upper()
    address_text = f"{data['street']} {data['door_number']} {data['floor']}° {data['apartment']}".upper()

    base_image = add_text_to_image(base_image, full_name, (300, 2097))
    base_image = add_text_to_image(base_image, address_text, (300, 2220))
    base_image = add_text_to_image(base_image, data["postal_code"], (300, 2335))
    base_image = add_text_to_image(base_image, data["city"].upper(), (865, 2335))
    base_image = add_text_to_image(base_image, data["province"].upper(), (1780, 2335))
    base_image = add_text_to_image(base_image, data["dni_cuit"], (1080, 2575))
    base_image = add_text_to_image(base_image, data["birthday"], (1585, 2740))
    base_image = add_text_to_image(base_image, data["marital_status"].upper(), (290, 2740))
    base_image = add_text_to_image(base_image, data["cellphone"], (2060, 2740))

    # Guarda la imagen resultante
    output_path = f"solicitudes-autocompletadas/solicitud_{data['first_name']}_{data['last_name']}.png"
    base_image.save(output_path)

    return output_path

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
            "signature": request.form.get("signature_base64"),
        }

        subscription = SubscriptionModel(**data)
        # Convertimos la firma base64 en una imagen y obtenemos la ruta donde se guardó
        signature_path = save_signature_image(data["signature"], f"signature_{subscription.first_name}_{subscription.last_name}.png")
        # Actualizamos el campo 'signature' con la ruta de la imagen en lugar de la cadena base64
        data["signature"] = signature_path
        subscription.signature = signature_path
        # Llama a la función para incrustar la firma en la imagen de la solicitud
        embed_data_on_form(signature_path, data)

         # Buscar al asesor en la base de datos
        advisor = AdvisorModel.query.filter_by(name=data["customer_advisor"]).first()

        # Si el asesor existe, obtener su email
        advisor_email = advisor.email if advisor else None

        # Verificar si se encontró el email del asesor
        if not advisor_email:
            return "Error: No se encontró el email del asesor."

        # Preparar el contenido de los correos
        subscriber_email_content = render_template("subscriber_email_template.html", **data)
        admin_email_content = render_template("email_template.html", **data)

        # Crear el mensaje de correo para el suscriptor
        subscriber_msg = Message(
            "Confirmación de Suscripción",
            sender="crowiejose@gmail.com",
            recipients=[data["email"]],
        )
        subscriber_msg.html = subscriber_email_content

        # Crear el mensaje de correo para la administración (1er correo)
        admin_msg1 = Message(
            "Nueva Suscripción",
            sender="crowiejose@gmail.com",
            recipients=["crowiejose@gmail.com"],
        )
        admin_msg1.html = admin_email_content

        # Crear el mensaje de correo para el asesor
        admin_msg2 = Message(
            "Nueva Suscripción",
            sender="crowiejose@gmail.com",
            recipients=[advisor_email],
        )
        admin_msg2.html = admin_email_content

        # Enviar los correos
        # mail.send(subscriber_msg)
        # mail.send(admin_msg1)
        # mail.send(admin_msg2)

        # Guardar la suscripción en la base de datos
        db.session.add(subscription)
        db.session.commit()

        return "¡Gracias por tu suscripción! Hemos recibido tus datos."

    # Si es un GET, mostrar el formulario
    vehicles = VehicleModel.query.all()
    advisors = AdvisorModel.query.all()
    return render_template("index.html", vehicles=vehicles, advisors=advisors)

if __name__ == "__main__":
    app.run(debug=True)