#ñ
class MMU:
    def _init_(self, tamaño_RAM, tamaño_pagina):
        self.tamaño_RAM = tamaño_RAM # 400KB -> 100 paginas
        self.tamaño_pagina = tamaño_pagina # 4KB 
        self.memoria_real = [None] * 100 
        self.memoria_virtual = []
        self.map_memoria = {}
        self.contador_paginas = 1

    def obtener_id_pagina(self):
        self.contador_paginas += 1
        return self.contador_paginas
    
    def asignacion_memoria(self, pid, tamaño):
        #Pasar de KB a bytes
        # 1KB = 1024 
        # 4KB = 4096
        #Numero de paginas
        numero_paginas = (tamaño * 1024//4096) + 1
        #Generar puntero
        ptr = f"len(self.map_memoria) + 1"
        paginas = []
        for i in range(numero_paginas):
            pagina = Pagina(identificador = self.obtener_id_pagina())
            if len(self.memoria_real) < 100:
                pagina.direccion = self.contador_paginas - 1
                pagina.bandera = True
            else:
                pagina.bandera = False
                self.memoria_virtual.append(pagina)
            paginas.append(pagina)
        self.map_memoria[ptr] = paginas
        return ptr





        

class Pagina:
    def _init_(self, id, direccion, bandera):
        self.id = id
        self.direccion = direccion
        self.bandera = bandera