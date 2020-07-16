import smtplib, ssl, urllib.request, json, time, traceback
from getpass import getpass
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def alert(service, status):
    port = 465  # For SSL
    body = "O servico {0} esta {1}.".format(service, status)

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = sender_email
    message["Subject"] = "Alerta {0} {1}".format(service, status)
    message["Bcc"] = sender_email

    message.attach(MIMEText(body, "plain"))

    print("O servico {0} esta {1}. Enviando email...".format(service, status))
    if cancel_email:
        return
    # Create a secure SSL context
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, sender_email, message.as_string())

cancel_email = False
json_url = input("Type the url where to find the json: ")
sender_email = input("Type your email and press enter: ")
password = getpass()


offline_services = []

# Tenta abrir o arquivo salvo
try:
    with open('info.json') as json_file:
        old_state = json.load(json_file)

    for service in old_state['service'].keys():
        if old_state['service'][service] == 'down':
            offline_services.append(service)
except:
    pass

while True:
    try:
        data = urllib.request.urlopen(json_url) # it's a file like object and works just like a file
        for line in data: # files are iterable
            d = json.loads(line)
        
        now_offilne = []
        for service in d['service'].keys():
            if d['service'][service] == 'down':
                now_offilne.append(service)

        # Verifica quais serviços antes estavam funcionando e agora pararam para alertar
        for off_service in now_offilne:
            if off_service not in offline_services:
                alert(off_service, 'offline')
        # Verfica quais serviços antes estavam offline e agora voltaram a funcionar
        for off_service in offline_services:
            if off_service not in now_offilne:
                alert(off_service, 'online')
        
        if offline_services != now_offilne:
            offline_services = now_offilne
            with open('info.json', 'w') as outfile:
                json.dump(d, outfile)
        time.sleep(15) # Checka a URL a cada 15 segundos
    except:
        print("Ocorreu um erro!")
        traceback.print_exc()
        break

print("Shutting down")