from flask import Flask, jsonify, render_template, request
from componentes import MMU

app = Flask(__name__)

# Crear una instancia de la MMU
mmu = MMU(size_RAM=400, size_pagina=4, tipoAlgoritmo=0)

# Ruta para cargar la página inicial
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para ejecutar comandos en la MMU (new, delete, use, kill)
@app.route('/mmu-action', methods=['POST'])
def mmu_action():
    data = request.json
    action = data['action']
    pid = data.get('pid')
    ptr = data.get('ptr')
    size = data.get('size')

    if action == 'new':
        ptr = mmu.new(pid, size)
    elif action == 'use':
        mmu.use(ptr)
    elif action == 'delete':
        mmu.delete(ptr)
    elif action == 'kill':
        mmu.kill(pid)

    # Devolver el estado actualizado de la MMU
    return jsonify(get_mmu_data())

# Función auxiliar para obtener los datos actuales de la MMU
def get_mmu_data():
    return {
        'memoria_real': [[pagina.id if pagina else None for pagina in mmu.memoria_real]],
        'memoria_virtual': [[pagina.id if pagina else None for pagina in mmu.memoria_virtual]],
        'procesos': mmu.procesos,
        'punteros': mmu.punteros,
        'contador_paginas': mmu.contador_paginas,
        'used_pages': [pagina.id for pagina in mmu.used_pages],
        'total_time': mmu.total_time,
        'thrashing_time': mmu.thrashing_time,
        'used_RAM': mmu.used_RAM,
        'used_VRAM': mmu.used_VRAM
    }

if __name__ == '__main__':
    app.run(debug=True)
