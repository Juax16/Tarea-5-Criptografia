import imaplib
import email
import re
import sys


FILE_NAME = 'mail_re.csv' # Nombre del archivo a importar

# Datos del usuario (dirección de correo y contraseña)
USR_EMAIL = '' # Correo electrónico
USR_PW =  '' # Contraseña del correo electrónico

# Hostname del servicio de correo, Dirección IMAP
HOSTNAME = 'imap.gmail.com' # Si es Gmail, Outlook/Hotmail = 'imap-mail.outlook.com'


# Convierte la fecha leida del archivo de DD/MM/AA a DD-MM-AAAA
def date_formatter( date_to_format):
    months = {
    '01' : 'Jan', '02' : 'Feb',
    '03' : 'Mar', '04' : 'Apr',
    '05' : 'May', '06' : 'Jun',
    '07' : 'Jul', '08' : 'Aug',
    '09' : 'Sep', '10' : 'Oct',
    '11' : 'Nov', '12' : 'Dec'
}
    split = date_to_format.split('/')
    if int(split[0]) > 31 or int(split[1]) > 12 or int(split[0]) < 1 or int(split[1]) < 1:
        print("Fecha inválida! (Mes menor a 1, mayor a 12, día menor a 1 o dia mayor a 31)")
        return
    date = "-".join((split[0], months[split[1]], str(20)+split[2]))
    return date


# Arreglo de 2 dimensiones para guardar los datos del .csv

lista = [[]] 


with open(FILE_NAME, newline='') as file:
    data = file.readlines()
    number = 1
    print("Elija una de las siguientes direcciones: ")
    for row in data:
        parse = row.split(";", 2)
        if parse[0] == '':
            break
        parse[2] = parse[2].strip("\r\n")
        print(str(number)+ ') ' + parse[0])
        lista[number-1].append(parse[0])  
        lista[number-1].append(parse[1])  
        lista[number-1].append(parse[2])
        number += 1
        lista.append([])

print('Escriba el numero correspondiente a la dirección de correo elegida: ')
num = input()

while True:
    if num.isnumeric():
        if int(num) < 1 or int(num) > number:
            print("Entrada inválida, por favor ingrese un numero válido.")
            num = input()
        else:
            break
    else:
        print("Entrada inválida, por favor ingrese un numero válido.")
        num = input()


        

mail = lista[int(num)-1][0]
regex = lista[int(num)-1][1]
date = lista[int(num)-1][2]

date = date_formatter(date)

print("\nDirección elegida: " + mail)
print("Expresión regular: " + regex)
print("Fecha del correo mas antiguo válido para la ER: " + date)


# Conexión con el servicio
conn = imaplib.IMAP4_SSL(HOSTNAME)

# Inicio de sesión
try:
    conn.login(USR_EMAIL, USR_PW)
    print("Se inició sesión correctamente!")
except:
    print("Error al iniciar sesión, se recomienda revisar los datos de ingreso.")
    sys.exit()

# Se selecciona la bandeja de entrada
response, data = conn.select('INBOX')
if response:
    print("Se seleccionó la bandeja de entrada.\n")


# Se busca en el buzón elegido (INBOX)
# FROM: remitente
# SINCE: desde que fecha se empieza a recolectar 
# Retorna una tupla con el estado 
response_2, msg_ids = conn.search(None, '(FROM %s SINCE %s)' %(mail,date))
# FECHAS NO COINCIDEN


msg_list = msg_ids[0].split()


if msg_list == []:
    print("No se encontró ningún correo con los criterios de búsqueda seleccionados.")
    sys.exit()


print("Numero de correos recuperados: " + str(len(msg_list)))

count = 0
print("______________________________________________________________________\n")
print("Empieza la recuperación y comparación de message-id\n")

# Se recorre cada elemento de la lista ID's, no condundir con el 'message-id'
for id in msg_list:
    # Se deodifica de bytes a utf-8
    id_raw = id.decode()
    # Se recupera el encabezado del correo
    # Retorna un mensaje del estado de la petición y la información solicitada
    typ2, msg_data = conn.fetch(id, 'BODY.PEEK[HEADER]')
    # Se decodifica
    raw_email = msg_data[0][1].decode('utf-8')
    # Se convierte en un objeto 'Message'
    email_obj = email.message_from_string(raw_email)
    # Se selecciona el 'message-id' y se le quitan los '<' y '>' del principio y final
    msg_id = email_obj['message-id'].strip('<>')
    # Se compara la expresión regular con el ID recién guardado
    matched = re.fullmatch(regex, msg_id)
    if not matched:
        count = count + 1
        print("______________________________________________________________________________________________________________________")
        print("Un mensaje no cumple con la expresión regular!!!")
        print("Fecha: " + email_obj['date'].strip('<>'))
        print("Message-ID: " + email_obj['message-id'].strip('<>'))
        print("Recuerda revisar si cumple con alguna expresión regular anterior o si la fecha es cercana a la validez de la actual ER!")
        print("______________________________________________________________________________________________________________________ \n")

print("Total de mensajes irregulares: " + str(count))

print("\n\nFin del código!")


