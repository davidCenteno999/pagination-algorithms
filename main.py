from flask import Flask, render_template, request



tipoAlgoritmo = 0


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')  # Aquí cargarías el frontend con botones y campos para la simulación

@app.route('/simulate', methods=['POST'])
def simulate():
    # Aquí procesarías la entrada del usuario para la simulación
    algorithm = request.form['algorithm']
    processes = int(request.form['processes'])
    operations = int(request.form['operations'])
    # Ejecuta la simulación
    result = 2#run_simulation(algorithm, processes, operations)  # Función que debes definir
    return render_template('result.html', result=result)  # Retorna el resultado de la simulación


if __name__ == '__main__':
    app.run(debug=True)