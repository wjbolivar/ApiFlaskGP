ApiFlaskGP
==========
Api rest que permite el registro de usuarios y las ventas asociadas a éstos

Feactures
---------

+ Flask
+ Python
+ APIRequest User
+ MongoDB



Install - Linux
---------------

sudo apt-get install -y mongodb-org

mongo
use apirest

Run Server
------------

cd api
python run.py

POST
------------
+ add user
curl -XPOST -H "Content-type: application/json" \
    -d '{"email":"prueba@gmail.com", "nombre": "Deusna", "apellido":"Pereira","direccion":"Coro falcon","activo":False}' \
    'http://localIP:5000/users/add'

+ update user

curl -XPOST -H "Content-type: application/json" \
    -d '{"email":"prueba@gmail.com", "nombre": "Deusnalith"}' \
    'http://localIP:5000/users/update'

+ add venta

curl -XPOST -H "Content-type: application/json" \
    -d '{
"uuid": "889e068d-b098-4da2-82dd-4c712b0446b6",\
"user_email": "ejemplo@geopagos.com",\
"amount": 123.45,\
"date": "2017-10-15 11:35"\
}' \
    'http://localIP:5000/ventas/add'
    
+ disable user

curl -XPOST -H "Content-type: application/json" \
    -d '{"email":"prueba@gmail.com"}' \
    'http://localIP:5000/users/deshabilitar'
    
    
    
GET
------
+ Get user
http://localIP:5000/users/<email>
  
+ List users
http://localIP:5000/users

+ Enable user
http://localIP:5000users/aprobar/<email>
  
+ sales list - user
http://localIP:5000/user/ventas/<user_email>

+ Disable sale
http://localIP:5000/venta/anular/<uuid>
