from flask import Flask, render_template, request, send_file
import os
import random
import io

app = Flask(__name__)

# Configurar una carpeta para almacenar archivos subidos
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

import random

import random

def generate_operations(processes, max_operations, seed):
    random.seed(seed)  # Establecer la semilla para la aleatoriedad
    operations_list = []
    total_operations = 0
    ptr_table = {}  # Tabla de símbolos para almacenar punteros y su estado
    created_processes = set()  # Conjunto para rastrear procesos creados
    used_kill = set()  # Conjunto para rastrear qué procesos han sido "kill"
    options = list(range(1, processes+1))
    operations = ['new', 'use', 'delete'] * 3 + ['kill']
    print(options)

    while total_operations < (max_operations - len(used_kill)):
        operation_type = random.choice(operations)
        print(operations_list)

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

    # Asegurarse de que se haga un "kill" a todos los procesos creados
    for process_id in created_processes:
        if process_id not in used_kill:
            operations_list.append(f"kill({process_id})")
            used_kill.add(process_id)

    return operations_list


@app.route('/simulate', methods=['POST'])
def simulate():
    # Obtener el método de entrada
    input_method = request.form['input-method']
    
    form_data = []
    file_path = None
    operations_list = []

    if input_method == 'manual':
        algorithm = request.form['algorithm']
        processes = int(request.form['processes'])
        seed = int(request.form['seed'])
        max_operations = int(request.form['operations'])
        random.seed(seed)
        
        operations_list = generate_operations(processes, max_operations, seed)
        
        # Crear el arreglo con los datos ingresados manualmente
        form_data = [algorithm, processes, max_operations]
    elif input_method == 'file':
        # Obtener el archivo subido
        file = request.files['file']
        
        if file:
            # Guardar el archivo subido
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            
            # Incluir el nombre del archivo en los datos de respuesta
            form_data = [file.filename]
    
    # Crear un archivo en memoria con las operaciones generadas
    if operations_list:
        file_content = "\n".join(operations_list)
        file_stream = io.BytesIO(file_content.encode('utf-8'))
        return send_file(file_stream, as_attachment=True, download_name="operations.txt", mimetype='text/plain')

    # Retornar los datos en la plantilla de resultados
    return render_template('result.html', form_data=form_data, file_path=file_path)

if __name__ == '__main__':
    # Crear la carpeta de uploads si no existe
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    
    app.run(debug=True)
