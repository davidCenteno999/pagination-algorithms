from flask import Flask, render_template, request, send_file, jsonify, Response
import os
import random
import re
import time  # Para simular el progreso de las operaciones
from componentes import MMU, Pagina
import json
import traceback

app = Flask(__name__)

# Inicialmente declaramos la variable global sin valor
MMU1 = None
MMU2 = None
MMU3 = None

# Configurar una carpeta para almacenar archivos subidos
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


paused = False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/continue')
def continue_simulation():
    global paused
    paused = False  # Se reanuda la simulación
    return jsonify({"status": "continue"})

def initialize_MMU(algorithm):
    global MMU1
    global MMU2
    global MMU3
    algo = 0
    if algorithm == "FIFO":
        algo = 0
    elif algorithm == "SC":
        algo = 1
    elif algorithm == "MRU":
        algo = 2
    else:
        algo = 3
    # Aquí la MMU con el algoritmo seleccionado
    MMU1 = MMU(400, 4, algo)
    MMU2 = MMU(400, 4, 4)
    MMU3 = MMU(400, 4, 0)

def generate_operations(processes, max_operations, seed):
    random.seed(seed)  # Establecer la semilla para la aleatoriedad
    operations_list = []
    total_operations = 0
    total_processes = 0
    total_ptr = 1
    total_pages = 1
    operations_per_process = (max_operations // processes) - 1
    ptr_table = {}  # Tabla de símbolos para almacenar punteros y su estado {ptr:[1,2,3,4,5,6],ptr:[]}
    ptr_table_2 = {}
    created_processes = {}  # Conjunto para rastrear procesos creados
    used_pages = []

    used_kill = set()  # Conjunto para rastrear qué procesos han sido "kill"
    options = []
    operations = ['new', 'use'] * 2 + ['delete'] + ['kill']
    last_operation = ''
    operations_last_new_process = 0

    while total_processes < processes:

        if((operations_last_new_process >= operations_per_process) and last_operation != 'kill'):
            operation_type = 'new'
        elif(operations_last_new_process >= operations_per_process):
            operation_type = 'use'
        else:
            operation_type = random.choice(operations)
            
        
        if operation_type == 'new' and last_operation != 'kill':

            size = random.randint(1, 40960)
            numero_paginas = (size//4096) + (1 if size%4096!=0 else 0)
            ptr = total_ptr
            total_ptr +=1
            ptr_table[ptr] = list(range(total_pages, total_pages + numero_paginas))
            ptr_table_2[ptr] = list(range(total_pages, total_pages + numero_paginas))
            total_pages += numero_paginas

            if(operations_last_new_process >= operations_per_process): #new process forced
                operations_last_new_process = 0
                total_processes+=1
                process_id = total_processes
                created_processes[process_id] = [ptr]
                options.append(process_id)
                    
            elif(len(created_processes)!=0):    #existing process
                process_id = random.choice(list(created_processes.keys()))
                created_processes[process_id].append(ptr)
                operations_last_new_process+=1

            else:                                #new process
                operations_last_new_process = 0
                total_processes+=1
                process_id = total_processes
                created_processes[process_id] = [ptr]
                options.append(process_id)
                


            operations_list.append(f"new({process_id}, {size})")
            total_operations += 1
            last_operation ='new'

        elif operation_type == 'use' and len(ptr_table)!=0:
            ptr_to_use = random.choice(list(ptr_table.keys()))
            operations_list.append(f"use({ptr_to_use})")
            used_pages += ptr_table[ptr_to_use]
            total_operations += 1
            operations_last_new_process +=1
            last_operation ='use'

        elif operation_type == 'delete' and len(ptr_table)>5:
            ptr_to_delete = random.choice(list(ptr_table.keys()))
            operations_list.append(f"delete({ptr_to_delete})")
            total_operations += 1
            operations_last_new_process +=1
            del ptr_table[ptr_to_delete]
            last_operation ='delete'

        elif operation_type == 'kill' and len(created_processes)>3 and len(ptr_table)>5:
            process_id_to_kill = random.choice(list(created_processes.keys()))
            operations_list.append(f"kill({process_id_to_kill})")
            used_kill.add(process_id_to_kill)
    
            for ptr in created_processes[process_id_to_kill]:
                if ptr in ptr_table:
                    del ptr_table[ptr]  

            del created_processes[process_id_to_kill]
            total_operations += 1
            operations_last_new_process +=1
            last_operation ='kill'

    #print(list(ptr_table.keys()))
    #print(operations_list)
    #print(len(ptr_table))
    #print("Operations")
    #print(total_operations)
    #print("Processes")
    #print(total_processes)
    #print(operations_last_new_process)
    #print(operations_per_process)
    #print(total_pages)
    #print(used_pages)
    with open('operations_generate.txt', 'w') as file:
        for operation in operations_list:
            file.write(f"{operation}\n")
    with open("paginasfuturas.txt", 'w') as file:
        for page in used_pages:
            file.write(f"{page}\n")
    with open("punteros.txt", 'w') as file:
        file.write("Puntero\tPáginas\n") 
        for ptr, pages in ptr_table_2.items():
            file.write(f"{ptr}\t{', '.join(map(str, pages))}\n")  # Escribe cada puntero y sus páginas

    return operations_list, used_pages

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

def populate_future_pages(operations_list):
    pattern = r'(\w+)\(([^,]*),?([^)]*)\)'  # Captura un primer argumento y un segundo opcional
    line_number = 1
    for operation in operations_list:
        #global paused
        #while paused:
        #    time.sleep(0.1)  # Esperar a que se reanude
        match = re.match(pattern, operation)
        
        if match:
            operation_type = match.group(1)
            first_arg = int(match.group(2))  # Primer argumento
            second_arg = int(match.group(3)) if match.group(3) else None  # Segundo argumento opcional

            #print(f'Operation: {operation_type}, First Arg: {first_arg}, Second Arg: {second_arg}')

            # Ejecutar la operación según el tipo
            if operation_type == "new":
                # Ejecutar la operación new en la MMU con pid y tamaño  
                MMU3.new(first_arg, second_arg)  # first_arg = pid, second_arg = size
            elif operation_type == "use":
                # Ejecutar la operación use en la MMU con el puntero
                MMU3.use(first_arg)  # first_arg = puntero (ptr)
            elif operation_type == "delete":
                # Ejecutar la operación delete en la MMU con el puntero
                MMU3.delete(first_arg)  # first_arg = puntero (ptr)
            elif operation_type == "kill":
                # Ejecutar la operación kill en la MMU con pid
                MMU3.kill(first_arg)

    return MMU3.future_pages_aux


@app.route('/simulate', methods=['POST'])
def simulate():
    global MMU1
    global MMU2
    global MMU3
    input_method = request.form['input-method']
    operations_list = []
    errors = []
    algorithm = request.form['algorithm']


    initialize_MMU(algorithm)

    if input_method == 'manual':
        processes = int(request.form['processes'])
        seed = int(request.form['seed'])
        max_operations = int(request.form['operations'])
        

        operations_list, future_pages = generate_operations(processes, max_operations, seed)
        MMU1.set_future_pages(future_pages)
        MMU2.set_future_pages(future_pages)

    elif input_method == 'file':
        file = request.files['file']
        if file:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)

            with open(file_path, 'r') as f:
                operations_list = f.read().strip().splitlines()

            errors = validate_operations(operations_list)

            future_pages = populate_future_pages(operations_list)

            MMU1.set_future_pages(future_pages)
            MMU2.set_future_pages(future_pages)
    validation_errors = validate_operations(operations_list)
    
    app.config['OPERATIONS_LIST'] = operations_list

    return render_template('result.html', operations=[])

count = 0

@app.route('/simulate_stream')  
def simulate_stream():
    global count
    operations_list = app.config.get('OPERATIONS_LIST', [])
    
    
    if (count < 1):
        def generate():
            pattern = r'(\w+)\(([^,]*),?([^)]*)\)'  # Captura un primer argumento y un segundo opcional
            line_number = 1
            for operation in operations_list:
                #global paused
                #while paused:
                #    time.sleep(0.1)  # Esperar a que se reanude
                match = re.match(pattern, operation)
                
                if match:
                    operation_type = match.group(1)
                    first_arg = int(match.group(2))  # Primer argumento
                    second_arg = int(match.group(3)) if match.group(3) else None  # Segundo argumento opcional

                    #print(f'Operation: {operation_type}, First Arg: {first_arg}, Second Arg: {second_arg}')

                    # Ejecutar la operación según el tipo
                    if operation_type == "new":
                        # Ejecutar la operación new en la MMU con pid y tamaño
                        
                        MMU1.new(first_arg, second_arg)  # first_arg = pid, second_arg = size
                        MMU2.new(first_arg, second_arg)
                    elif operation_type == "use":
                        # Ejecutar la operación use en la MMU con el puntero
                        MMU1.use(first_arg)  # first_arg = puntero (ptr)
                        MMU2.use(first_arg)
                    elif operation_type == "delete":
                        # Ejecutar la operación delete en la MMU con el puntero
                        MMU1.delete(first_arg)  # first_arg = puntero (ptr)
                        MMU2.delete(first_arg)
                    elif operation_type == "kill":
                        # Ejecutar la operación kill en la MMU con pid
                        MMU1.kill(first_arg)  # first_arg = pid
                        MMU2.kill(first_arg)

                    
                    #MMU1.imprimir_atributos()
                    mmu_state = {
                        'opt': MMU1.get_pages_state(),  # Obtener el estado del algoritmo OPT
                        'alg': MMU2.get_pages_state(),  # Obtener el estado de otro algoritmo
                        'summary_1': MMU1.get_summary_1(),  # Resumen 1
                        'summary_2': MMU2.get_summary_1(),   # Resumen 2
                        'current_operation': f"{line_number}: {operation}"
                    }
                    # Enviar los datos en formato SSE (Server-Sent Events) al cliente
                    #print(mmu_state)
                    # Simular el tiempo entre cada operación
                    line_number += 1
                    time.sleep(0.2)
                    paused = True
                    yield f"data:{json.dumps(mmu_state)}\n\n"
        
    count+=1;    
    return Response(generate(), mimetype='text/event-stream')


@app.route('/download/<filename>')
def download_file(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), as_attachment=True)

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    
    app.run(debug=True)
