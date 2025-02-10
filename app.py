from flask import Flask, jsonify, request, Response
import json
from spyne import Application, rpc, ServiceBase, Unicode
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication

app = Flask(__name__)

DATA_FILE = "productos.json"

# 📌 Funciones para manejar productos
def leer_productos():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def guardar_productos(productos):
    with open(DATA_FILE, "w") as f:
        json.dump(productos, f, indent=4)

# 📌 Rutas REST
@app.route("/api/productos", methods=["GET"])
def obtener_productos():
    return jsonify(leer_productos())

@app.route("/api/productos", methods=["POST"])
def agregar_producto():
    nuevo_producto = request.json
    productos = leer_productos()
    productos.append(nuevo_producto)
    guardar_productos(productos)
    return jsonify({"mensaje": "Producto agregado", "producto": nuevo_producto}), 201

# 📌 Servicio SOAP con spyne
class ProductoService(ServiceBase):
    @rpc(Unicode, _returns=Unicode)
    def obtener_producto(ctx, nombre):
        productos = leer_productos()
        for p in productos:
            if p["nombre"] == nombre:
                return json.dumps(p)  # Convertir a string JSON
        return "Producto no encontrado"

# 📌 Configurar la aplicación SOAP
soap_app = Application([ProductoService], 'mi.api.soap',
                       in_protocol=Soap11(), out_protocol=Soap11())

wsgi_app = WsgiApplication(soap_app)

# 📌 Rutas SOAP en Flask
@app.route("/soap", methods=["GET", "POST"])
def soap_service():
    if request.method == "GET":
        return "Servicio SOAP activo. Accede a /soap?wsdl para ver el WSDL."
    
    return Response(
        wsgi_app(request.environ, lambda status, headers: (status, headers)[1]),
        content_type="text/xml; charset=utf-8"
    )

# 📌 Agregar WSDL para visualizarlo en el navegador
@app.route("/soap?wsdl", methods=["GET"])
def soap_wsdl():
    return Response(
        soap_app.create_wsdl(),
        content_type="text/xml; charset=utf-8"
    )

# 📌 Ejecutar la app en modo desarrollo (para pruebas locales)
if __name__ == "__main__":
    app.run(debug=True)


