from flask import Flask, request
from flask.json import jsonify
import b_backend


app = Flask(__name__)

@app.route('/bienvenido', methods=['GET'])
def  bienvenido():
    return 'Hola, este es un bot creado para responder preguntas desde un docx, desde Flask'


    
@app.route('/pregunta', methods=['POST'])
def recibir_mensajes():
    try:
        body = request.get_json()
        user_name = body.get('user_name')
        question = body.get('question')

        if not user_name or not question:
            return jsonify({'error': 'Campos user_name y question son requeridos'}), 400


        respuesta = b_backend.consulta(question)

        return jsonify({'respuesta': respuesta}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run()