from flask import Flask, render_template, request, send_file, jsonify
import os
import random
import io
import re

app = Flask(__name__)

# Configurar una carpeta para almacenar archivos subidos
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

def generate_operations(processes, max_operations, seed):
    random.seed(seed)  # Establecer la semilla para la aleatoriedad
    operations_list = []
    total_operations = 0
    ptr_table = {}  # Tabla de símbolos para almacenar punteros y su estado
    created_processes = set()  # Conjunto para rastrear procesos creados
    used_kill = set()  # Conjunto para rastrear qué procesos han sido "kill"
    options = list(range(1, processes + 1))
    operations = ['new', 'use', 'delete'] * 3 + ['kill']

    while total_operations < max_operations :
        operation_type = random.choice(operations)

        if operation_type == 'new':
            if not options:
                operations.remove('new')
                continue

            process_id = random.choice(options)
            options.remove(process_id)
            
            # Generar un tamaño aleatorio
            size = random.randint(1, 1000)  
            operations_list.append(f"new({process_id}, {size})")
            total_operations += 1

            ptr = len(operations_list)  # Suponiendo que el puntero es el índice
            ptr_table[ptr] = {'process_id': process_id, 'used': False}
            created_processes.add(process_id)  # Marcar el proceso como creado

        elif operation_type == 'use':
            # Solo se puede usar si hay al menos un puntero en la tabla de símbolos
            available_ptrs = [ptr for ptr, val in ptr_table.items() if not val['used']]
            if available_ptrs:
                ptr_to_use = random.choice(available_ptrs)
                operations_list.append(f"use({ptr_to_use})")
                ptr_table[ptr_to_use]['used'] = True
                total_operations += 1

        elif operation_type == 'delete':
            # Solo se puede eliminar si hay un puntero en la tabla de símbolos
            available_ptrs = [ptr for ptr in ptr_table.keys() if ptr_table[ptr]['used']]
            if available_ptrs:
                ptr_to_delete = random.choice(available_ptrs)
                operations_list.append(f"delete({ptr_to_delete})")
                total_operations += 1
                del ptr_table[ptr_to_delete]  # Eliminar puntero de la tabla

        elif operation_type == 'kill':
            # Solo se puede ejecutar "kill" si el proceso fue creado con "new"
            if 'new' not in operations:
                break  
            available_processes = [pid for pid in created_processes if pid not in used_kill]
            if available_processes:
                process_id_to_kill = random.choice(available_processes)
                operations_list.append(f"kill({process_id_to_kill})")
                total_operations += 1
                used_kill.add(process_id_to_kill)  # Marcar este proceso como "kill"

                ptrs_to_remove = [ptr for ptr in ptr_table if ptr_table[ptr]['process_id'] == process_id_to_kill]
                for ptr in ptrs_to_remove:
                    if ptr in ptr_table:
                        del ptr_table[ptr]  

    return operations_list

def validate_operations(operations_list):
    valid_operations = {'new', 'use', 'delete', 'kill'}
    errors = []

    for operation in operations_list:
        match = re.match(r'(\w+)\((\d+)(?:, (\d+))?\)', operation)
        if match:
            op_type = match.group(1)
            if op_type not in valid_operations:
                errors.append(f"Invalid operation type: {operation}")
        else:
            errors.append(f"Invalid operation format: {operation}")

    return errors

@app.route('/simulate', methods=['POST'])
def simulate():
    # Obtener el método de entrada
    input_method = request.form['input-method']
    
    form_data = []
    file_path = None
    operations_list = []
    errors = []

    if input_method == 'manual':
        algorithm = request.form['algorithm']
        processes = int(request.form['processes'])
        seed = int(request.form['seed'])
        max_operations = int(request.form['operations'])
        random.seed(seed)
        
        operations_list = generate_operations(processes, max_operations, seed)
        
        # Crear el arreglo con los datos ingresados manualmente
        form_data = [algorithm, processes, max_operations]
        
        # Guardar las operaciones generadas en un archivo
        if operations_list:
            file_content = "\n".join(operations_list)
            file_name = "operations.txt"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
            
            # Guardar el archivo en el servidor
            with open(file_path, 'w') as f:
                f.write(file_content)

    elif input_method == 'file':
        # Obtener el archivo subido
        file = request.files['file']
        
        if file:
            # Guardar el archivo subido
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            
            # Leer el contenido del archivo y validar operaciones
            with open(file_path, 'r') as f:
                operations_list = f.read().strip().splitlines()
            
            # Validar las operaciones del archivo
            errors = validate_operations(operations_list)
            if errors:
                return render_template('result.html', form_data=form_data, file_path=file_path, errors=errors, operations=operations_list)

    # Validar las operaciones generadas
    validation_errors = validate_operations(operations_list)
    if validation_errors:
        return render_template('result.html', form_data=form_data, file_path=file_path, errors=validation_errors, operations=operations_list)

    # Retornar los datos en la plantilla de resultados
    return render_template('result.html', form_data=form_data, file_path=file_path, errors=errors, operations=operations_list)

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), as_attachment=True)


if __name__ == '__main__':
    # Crear la carpeta de uploads si no existe
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    
    app.run(debug=True)
