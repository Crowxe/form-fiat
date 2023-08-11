from flask import Flask, render_template, request
from flask_mail import Mail, Message

app = Flask(__name__)

# Configuración de Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'gautamaprods@gmail.com'  # Cambia esto por tu email
app.config['MAIL_PASSWORD'] = 'bren0333'       # Cambia esto por tu contraseña

# Inicializar Flask-Mail con la configuración anterior
mail = Mail(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Recoger los datos del formulario
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        # ... (recoge todos los otros campos del formulario de la misma manera)

        # Crear el mensaje de correo
        msg = Message('Nuevo Formulario de Suscripción', sender='gautamaprods@gmail.com', recipients=['crowiejose@gmail.com'])
        msg.body = f"Nombre completo: {first_name} {last_name}"  # Puedes añadir más campos aquí

        # Enviar el mensaje
        mail.send(msg)

        return "¡Gracias por tu suscripción! Hemos recibido tus datos."

    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
