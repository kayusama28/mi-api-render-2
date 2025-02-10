from flask import Flask, jsonify, request
import json

app = Flask(__name__)

DATA_FILE = "productos.json"

def leer_productos():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def guardar_productos(productos):
    with open(DATA_FILE, "w") as f:
        json.dump(productos, f, indent=4)

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
