# -*- coding: utf-8 -*-
import re
import os

#Constantes de validación
EMAIL_VALIDATE = '^[(a-z0-9\_\-\.)]+@[(a-z0-9\_\-\.)]+\.[(a-z)]{2,15}$'
FLOAT = '^[0-9]*\.?[0-9]*$'

mongodrv = os.environ['DB_PORT_27017_TCP_ADDR']

#Método validate_email
def validate_email(email):
    """
        Método que permite la validación del campo email segun la expresión regular de la constante EMAIL_VALIDATE
    """
    validate = False # en principio se asume que el dato no es valido

    if not email:# si no se optien un email
        validate = False

    
    elif re.match(EMAIL_VALIDATE,email.lower()):
        validate = True

    else:
        validate =False

    return validate
#fin del Método validate_email

#Método es_float
def es_float(num):
    """
        Método para verificar si un campo posee el formáto valido de un dato float
    """
    return True if re.match(FLOAT,str(num).lower()) else False

