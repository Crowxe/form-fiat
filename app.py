from flask import Flask, render_template, request
from flask_mail import Mail, Message
from flask_mysqldb import MySQL
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from datetime import datetime

# Inicialización
app = Flask(__name__)

# Configuraciones
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "fiat_form"
app.config["MAIL_SERVER"] = "smtp-relay.brevo.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = False
app.config["MAIL_USERNAME"] = "crowiejose@gmail.com"
app.config["MAIL_PASSWORD"] = "QvmUF9CJ8PnKTg4R"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:@localhost/fiat_form"
app.config["SECRET_KEY"] = "f123"


# Inicializar extensiones
mysql = MySQL(app)
mail = Mail(app)
db = SQLAlchemy(app)
admin = Admin(app, name="Administración", template_mode="bootstrap3")


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


# Vistas de Flask-Admin
admin.add_view(ModelView(VehicleModel, db.session, name="Modelos de Vehículos"))
admin.add_view(ModelView(AdvisorModel, db.session, name="Asesores"))


@app.route("/testdb")
def testdb():
    cur = mysql.connection.cursor()
    cur.execute("SHOW TABLES;")
    tables = cur.fetchall()
    return str(tables)


@app.route("/createtable")
def create_table():
    cur = mysql.connection.cursor()
    cur.execute(
        """
        CREATE TABLE test_table (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(50) NOT NULL
        );
    """
    )
    mysql.connection.commit()
    return "Tabla creada!"


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

        # Renderizar el template del correo con los datos
        email_content = render_template("email_template.html", **data)

        # Crear el mensaje de correo
        msg = Message(
            "Nuevo Formulario de Suscripción",
            sender="crowiejose@gmail.com",
            recipients=["crowiejose@gmail.com"],
        )
        msg.html = email_content  # Establece el contenido renderizado como el cuerpo del correo

        # Enviar el mensaje
        mail.send(msg)

        return "¡Gracias por tu suscripción! Hemos recibido tus datos."
    vehicles = VehicleModel.query.all()
    advisors = AdvisorModel.query.all()
    print(vehicles)
    print(advisors)

    return render_template('index.html', vehicles=vehicles, advisors=advisors)



if __name__ == "__main__":
    app.run(debug=True)
