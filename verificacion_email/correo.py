
from email.message import EmailMessage
import smtplib


smtp_server = "smtp.gmail.com"
smtp_port = 587
smtp_username = "expeditec.uci@gmail.com"
smtp_password = "nmmwerzbvlbynsxn"


# Función para enviar correo electrónico
def enviar_correo(email, asunto, mensaje):
    # Aceptar tanto string como lista de correos
    if isinstance(email, list):
        destinatarios = email
    else:
        destinatarios = [email]

    msg = EmailMessage()
    msg['Subject'] = asunto
    msg['From'] = smtp_username
    msg['To'] = ", ".join(destinatarios)
    msg.set_content(mensaje)

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
    except Exception as e:
        print(f"Error al enviar correo: {e}")
