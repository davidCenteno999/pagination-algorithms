from flask import Flask, render_template, request
import os

app = Flask(__name__)

# Configurar una carpeta para almacenar archivos subidos
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')  # Cargar el frontend con el formulario

@app.route('/simulate', methods=['POST'])
def simulate():
    # Obtener los datos del formulario
    algorithm = request.form['algorithm']
    processes = int(request.form['processes'])
    operations = int(request.form['operations'])
    
    # Obtener el archivo subido
    file = request.files['file']
    file_path = None
    
    if file:
        # Guardar el archivo subido en la carpeta de uploads
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
    
    # Crear un arreglo con los datos del formulario y el archivo subido
    form_data = [algorithm, processes, operations, file.filename if file else "No file uploaded"]
    
    # Retornar los datos y el archivo subido en la plantilla de resultados
    return render_template('result.html', form_data=form_data, file_path=file_path)

if __name__ == '__main__':
    # Crear la carpeta de uploads si no existe
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    
    app.run(debug=True)
