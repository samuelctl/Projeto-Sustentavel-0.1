import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

EMAIL_REMETENTE = "samuel11souza09@gmail.com"
SENHA_APP = "arwv ecpr ploj vwyb"


def enviar_email(destinatario: str, assunto: str, mensagem_html: str):
    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL_REMETENTE
        msg["To"] = destinatario
        msg["Subject"] = assunto

        msg.attach(MIMEText(mensagem_html, "html"))

        servidor = smtplib.SMTP("smtp.gmail.com", 587)
        servidor.starttls()
        servidor.login(EMAIL_REMETENTE, SENHA_APP)

        servidor.sendmail(EMAIL_REMETENTE, destinatario, msg.as_string())
        servidor.quit()

        print("Email enviado com sucesso!")

    except Exception as e:
        print("Erro ao enviar email:", e)