# -*- coding: utf-8 -*-

from flask import request, jsonify, make_response
from flask import Flask, Response
from util.util import validate_email,es_float,mongodrv
import pymongo
from bson.son import SON
import datetime


class AppResponse(Response):
     default_mimetype = 'application/json'
  

try:
    app = Flask(__name__)
    app.config.from_pyfile('config.cfg')#carga de archivo de configuración
    app.response_class = AppResponse
    mongo = pymongo.MongoClient(host=mongodrv)#instancia Driver PyMongo - Mongodb 
     
except Exception as e:
    print "Exception: %s - %s"%(type(e), e)

#método listUsers
@app.route('/users',methods=['GET'])
def listUsers():
    """método para el despliegues del listado de todos los usuarios, se indica: email, nombre, apellido, dirección,
    estado activo (si fue aprobado y/o deshabilitado), la cantidad total de ventas asociadas a dicho usuario y el
    importe total operado (suma de los importes de todas las ventas no anuladas). """
    
    
    users = mongo.db.users.find({},{'_id':0})#busqueda de usuarios omitiendo cargar en el resultado el _id
    ventas = mongo.db.ventas

    if users.count():#si existen resgistros
        data = [ ]#tupla para guardar data de la consulta

        for user in users:
            """
                despliegue del método aggregate() para usar el marco de agregación. Se realiza una agregación
                simple para contar el número de ocurrencias para cada etiqueta en el conjunto de etiquetas,
                en toda la colección. Como los diccionarios de Python no mantienen el orden, se debe usar SON
                o collections.OrderedDict donde se requiere un orden explícito, por ejemplo, "$sort":

                https://api.mongodb.com/python/2.7.2/tutorial.html#querying-by-objectid
                https://api.mongodb.com/python/2.7.2/examples/aggregation.html#aggregation-framework
                """
            user_venta = ventas.aggregate([
                     { '$match': { 'user_email': user['email'],'anulada': {'$ne':True} } },
                     { '$group': {'_id':'user_email', 'count': {'$sum': 1}, 'total': { '$sum': '$amount' } } },
                     { '$sort': SON([('count', -1),('total', -1) ]) }
                   ])
            user_venta = user_venta['result']
            
            user["ventas"] = user_venta[0]['count'] if user_venta else 0 
            user["importe_total"] = user_venta[0]['total'] if user_venta else 0
  
            data.append(user)

        return jsonify({'response':"Lista de Usuarios",'data':data}) #retorno de json response

    else:
        return jsonify({'response': "no existen registros"})
#fin del método listUsers

#método get_one_user
@app.route('/users/<email>', methods=['GET'])
def get_one_user(email):
    """
        Éste método permite el despliegue de los datos asociados a un registro de usuario previo conocimiento de su email
    """
    users = mongo.db.users#conección db

    if validate_email(email):#método para validar email, si éste es valido seguimos con la operación, se encuentra en el paquete util
        try:
            user = users.find_one({'email' : email},{'_id': 0})

            if user:
                response = {'response' : 'detalles del usuario','data':user}
            else:
                response = {'response' :'usuario no encontrado'}

        except Exception as e:#si ocurre alguna eventualidad disparmos Exception
            response = {"response": "%s - %s"%(type(e), e)}
        
    else:
        response = {"response": "el dato email es requerido"}
    
    return jsonify(response)
#fin del método get_one_user

#método add_users
@app.route('/users', methods=['POST'])
def add_users():
    """
        Método para Crear usuarios indicando email, el cual es validado; nombre; apellido y dirección
        internamente se incorpora un campo valido para controlar si un usuario fue aprobado/deshabilitado
    """
    users = mongo.db.users
    data = request.get_json()#data jason de entrada
    
    if not data:
        response = {"response": "ERROR, no se ha suministrado un conjunto de datos (json)"}
        
    else:
        email = data.get('email')
            
        if validate_email(email):#validamos email
                
            if users.find_one({'email' : email}):#validamos que no exista el usuario

                response = {'response': "ya existe un registro con este email"}

            else:
                
                    users.insert(data)#insertamos data suministrada

                    response = {'response' : "registro exitoso"}

        else:
            response = {'response': "el dato email es requerido"}  

    return jsonify(response)
#fin de método add_users

#Método aprobar_user
@app.route('/users/aprobar/<email>',methods=['GET'])
def aprobar_user(email):
    """
       Método para aprobar un usuario anteriormente creado mediante su email
    """
    users = mongo.db.users

    if validate_email(email):

        try:
            #aprobación del usuaio mediante la actualización del item activo
            resultado = users.update({'email': email}, {'$set': {
                                                    'activo': True
                                                }})

            if resultado['updatedExisting']:#consultamos que se efectuó la actualización del registro
                response = {'response': "usuario activado"}

            else:
                response = {'response': "no se pudo activar, verifique los datos de entrada"}

        except Exception as e:
            response = {"response": "%s - %s"%(type(e), e)}

    else:
        response = {'response': "El dato email es requerido"}

    return jsonify(response)
 #fin del Método aprobar_user  
    
#Método deshabilitar_user
@app.route('/users/deshabilitar',methods=['POST'])
def deshabilitar_user():
    """
        Método para deshabilitar un usuario indicando su email (nunca se eliminan, pero pueden
        deshabilitarse)
    """
    users = mongo.db.users
    data = request.get_json()

    if validate_email(data.get('email')):

        try:
             #se procede a deshabilitar el usuaio mediante la actualización del item activo
            resultado = users.update({'email': data.get('email'),'activo':True}, {'$set': {
                                                    'activo': False
                                                }})
            if resultado['updatedExisting']:#consultamos que se efectuó la actualización del registro
                response = {'response': "usuario deshabilitado"}

            else:
                response = {'response': "no se pudo deshabilitar, verifique los datos de entrada"}

        except Exception as e:
            response = {"response": "%s - %s"%(type(e), e)}

    else:
        response = {"response": "El dato email es requerido"}

    return jsonify(response)
#fin del método deshabilitar_user

#Método update_user
@app.route('/users/update', methods=['POST'])
def update_user():
    """
        Método para modifica un usuario indicando su email y los campos a modificar mediante un jason 
    """
    users = mongo.db.users
    data = request.get_json()#lectuda de datos de entrada POST 
    
    if not data:
        response = {"response": "ERROR, no hay datos"}
        
    else:
            
        if validate_email(data.get('email')):#método para validar email, si éste es valido seguimos con la operación, se encuentra en el paquete util
            
            try:
                resultado = users.update({'email': data.get('email')}, {'$set': data })
                
                #retornamos los detalles de la actualización
                response = {"response": "registros actualizados %d"%resultado['n'], "data":[resultado]}

            except Exception as e:

                response = {"response": "%s - %s"%(type(e), e)}

        else:
            response = {"response": "El dato email es requerido"}

    return jsonify(response)
#fin del método update_user


#Método add_ventas
@app.route('/ventas/add', methods=['POST'])
def add_ventas():
    """
        Método para crear una venta asociada a un usuario, mediante una llamada tipo POST. 
        Si un usuario no se encuentra habilitado, se retorna un error.

        procedimiento: https://docs.mongodb.com/manual/reference/database-references/index.html#process
    """
    users = mongo.db.users
    ventas = mongo.db.ventas

    data = request.get_json()##lectuda de datos de entrada POST 

    if validate_email(data.get('user_email')):#validación del email

        user = users.find_one({'email':data.get('user_email'),'activo':True})#el usuario debe existir y estar habilitado

        if user:
            if es_float(data.get('amount')):#se verifica que el dato umount sea un float valido
                try:
                    
                    if ventas.find_one({'uuid': data.get('uuid')}):#Si existe el identificador uuid, se cancela el registro
                        response = {'response' : "ya existe un resgistro de venta con el uuid:%s"%data.get('uuid')}

                    else:
                        ventas.insert(data)#registro de la venta

                        #se añade el item de control anulada para conocer el estatus del registro
                        ventas.update({'uuid': data.get('uuid')}, {'$set': {
                                                        'anulada': False
                                                    } })

                        response = {'response' : "registro de venta exitoso"}

                except Exception as e:
                    response = {'response': "%s - %s"%(type(e), e)}

            else:
                response = {'response':"el monto asociado no es valido"}
                    

        else:
            response = {'response':"el usuario no se encuentra disponible"}
    else:
        response = {'response': "el dato email es requerido"}
    
    return jsonify(response)
#fin del método add_ventas

#Método user_ventas
@app.route('/users/ventas/<user_email>', methods=['GET'])
def user_ventas(user_email):
    """
        Método para consultar la lista de ventas de un usuario indicando su email
    """

    if validate_email(user_email):#validación del email
        ventas = mongo.db.ventas.find({'user_email':user_email},{'_id':0})

        if ventas.count():
            data = []#tupla para el modelado del resultado

            for venta in ventas:
                data.append(venta)

            response = {'response' : "ventas asociadas al usuario %s"%user_email,'data':data}
        else:
            response = {'response': "no existen ventas asociadas al usuario %s"%user_email }

    else:
       response = {'response': "el dato email es requerido"}

    return jsonify(response)
#fin del método user_ventas

#Método anular_venta
@app.route('/venta/anular/<uuid>', methods = ['GET'])
def anular_venta(uuid):
    """
        Método para anular una venta indicando su identificador único(uuid), la venta queda, pero anulada.
    """
    
    try:
        resultado = mongo.db.ventas.update({'uuid': uuid}, {'$set': {
                                                    'anulada': True
                                                } })
        if resultado['updatedExisting']:#se verifica que se ha efectuado la actualización
            response = {'response': "venta anulada"}

        else:
            response = {'response': "no se pudo realizar el proceso, verificar datos"}

    except Exception as e:
        response = {'response': "%s - %s"%(type(e), e)}
    
    return jsonify(response)
                
#fin del método anular_venta

#Error Handler 404
@app.errorhandler(404)
def not_found(error):
    app.logger.error('Server Error: %s', (error))
    return make_response(jsonify({'error': 'not found'}), 404)

#Error Handler 405
@app.errorhandler(405)
def not_found(error):
    app.logger.error('Server Error: %s', (error))
    return make_response(jsonify({'error': 'method is not allowed'}), 405)

#Error Handler 500
@app.errorhandler(500)
def internal_server_error(error):
    app.logger.error('Server Error: %s', (error))
    return make_response(jsonify({'error': 'internal Error'}), 500)

#Exception
@app.errorhandler(Exception)
def unhandled_exception(error):
    app.logger.error('Unhandled Exception: %s', (error))
    return make_response(jsonify({'error': 'unhandled exception'}), 500)
