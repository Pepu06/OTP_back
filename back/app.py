from flask import Flask, request, jsonify
import pandas as pd
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app.config['UPLOAD_FOLDER'] = './uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    
    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No file selected for uploading"}), 400
    
    if file and file.filename.endswith('.xlsx'):
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        return jsonify({"message": "File uploaded successfully", "filename": file.filename}), 200
    
    return jsonify({"error": "Invalid file format. Please upload an Excel file (.xlsx)"}), 400

@app.route('/process', methods=['GET'])
def process_file():
    files = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], f))]
    if not files:
        return jsonify({"error": "No files found"}), 404

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], files[0])
    
    try:
        data = pd.read_excel(filepath, sheet_name=None)
        processed_data = {sheet_name: sheet_data.to_dict(orient='records') for sheet_name, sheet_data in data.items()}
        
        return jsonify({"message": "File processed successfully", "data": processed_data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/update', methods=['POST'])
def update_data():
    data = request.json
    table = data.get('table')
    updated_rows = data.get('rows')
    
    if table not in ['torneos', 'partidos', 'jugadores']:
        return jsonify({"error": "Invalid table name"}), 400

    # Suponiendo que solo hay un archivo en la carpeta
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'data.xlsx')
    
    try:
        df = pd.read_excel(filepath, sheet_name=table)
        updated_df = pd.DataFrame(updated_rows)
        
        # Actualizar los datos en el DataFrame original
        df.update(updated_df)

        # Guardar los cambios en el archivo
        with pd.ExcelWriter(filepath, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df.to_excel(writer, sheet_name=table, index=False)
        
        return jsonify({"message": "Data updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    data = request.json
    table = data.get('table')
    updated_rows = data.get('rows')
    
    if table not in ['torneos', 'partidos', 'jugadores']:
        return jsonify({"error": "Invalid table name"}), 400

    # Suponiendo que solo hay un archivo en la carpeta
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'data.xlsx')
    
    try:
        df = pd.read_excel(filepath, sheet_name=table)
        updated_df = pd.DataFrame(updated_rows)
        
        # Actualizar los datos en el DataFrame original
        df.update(updated_df)

        # Guardar los cambios en el archivo
        with pd.ExcelWriter(filepath, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df.to_excel(writer, sheet_name=table, index=False)
        
        return jsonify({"message": "Data updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/delete', methods=['POST'])
def delete_data():
    data = request.json
    table = data.get('table')
    index = data.get('index')
    
    if table not in ['torneos', 'partidos', 'jugadores']:
        return jsonify({"error": "Invalid table name"}), 400

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'data.xlsx')
    
    try:
        df = pd.read_excel(filepath, sheet_name=table)

        # Verificar que el índice está dentro del rango
        if index < 0 or index >= len(df):
            return jsonify({"error": "Index out of range"}), 400

        df = df.drop(index)
        
        with pd.ExcelWriter(filepath, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df.to_excel(writer, sheet_name=table, index=False)
        
        return jsonify({"message": "Data deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
# Ruta para obtener datos del jugador
@app.route('/jugador/<id>', methods=['GET'])
def get_jugador(id):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'data.xlsx')
    
    try:
        df = pd.read_excel(filepath, sheet_name='jugadores')
        jugador = df[df['ID'] == int(id)].to_dict(orient='records')
        if not jugador:
            return jsonify({"error": "Jugador not found"}), 404
        
        return jsonify({"message": "Jugador data retrieved successfully", "data": jugador[0]}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Ruta para obtener histórico de torneos
@app.route('/historico/<id>', methods=['GET'])
def get_historico(id):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'data.xlsx')
    
    try:
        df = pd.read_excel(filepath, sheet_name='historicoTorneos')
        historico = df[df['IDJugador'] == int(id)].to_dict(orient='records')
        if not historico:
            return jsonify({"error": "Historico not found"}), 404
        
        return jsonify({"message": "Historico data retrieved successfully", "data": historico}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/partidos/<id>', methods=['GET'])
def get_partidos(id):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'data.xlsx')

    try:
        # Leer la hoja 'torneos' del archivo Excel
        df = pd.read_excel(filepath, sheet_name='partidos')
        partidos = df[df['IDTorneo'] == int(id)].to_dict(orient='records')
        if not partidos:
            return jsonify({"error": "Partidos not found"}), 404

        return jsonify({"message": "Partidos data retrieved successfully", "data": partidos}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/jugadores', methods=['GET'])
def get_jugadores():
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'data.xlsx')
    if not os.path.isfile(filepath):
        return jsonify({"error": "Archivo de jugadores no encontrado"}), 404

    try:
        # Leer la hoja 'jugadores' del archivo Excel
        df = pd.read_excel(filepath, sheet_name='jugadores')
        data = df.to_dict(orient='records')
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/torneos', methods=['GET'])
def get_torneos():
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'data.xlsx')
    if not os.path.isfile(filepath):
        return jsonify({"error": "Archivo de torneos no encontrado"}), 404

    try:
        # Leer la hoja 'torneos' del archivo Excel
        df = pd.read_excel(filepath, sheet_name='torneos')
        data = df.to_dict(orient='records')
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
