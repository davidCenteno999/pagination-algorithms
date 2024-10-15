#ñ
class MMU:
    def _init_(self, tamaño_RAM, tamaño_pagina):
        self.tamaño_RAM = tamaño_RAM # 400KB -> 100 paginas
        self.tamaño_pagina = tamaño_pagina # 4KB 
        self.memoria_real = [None] * 100 
        self.memoria_virtual = []
        self.map_memoria = {}
        self.contador_paginas = 0
        self.proceos = {}

    
    
    #-------------------------------------------------------------
    #           Funciones Principales
    #------------------------------------------------------------
    #new (pid, size) : ptr 
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
                pagina.bandera = True
                pagina.direccion = self.direccion_memoria_real(pagina)
                
            else:
                pagina.bandera = False
                self.memoria_virtual.append(pagina)
            paginas.append(pagina)
        self.map_memoria[ptr] = paginas
        self.asignar_puntero_lista_procesos(pid,ptr)

        return ptr
    
    #use(ptr) : void
    def usar_memoria(self, ptr):
        if ptr in self.map_memoria:
            paginas = self.map_memoria[ptr]
            for pagina in paginas:
                if not pagina.bandera:
                    self.intercambio_paginas(pagina)
        else:
            print("Punetero no encontrado.")

    #delete(ptr)
    def eliminar_memoria(self,ptr):
        if ptr in self.map_memoria:
            lista_paginas = self.map_memoria.pop(ptr)
            for pagina in lista_paginas:
                if pagina.bandera:
                    self.memoria_real[pagina.direccion] = None
                else:
                    self.memoria_virtual.remove(pagina)

    #-------------------------------------------------------------
    #           Algoritmos
    #------------------------------------------------------------
    def fifo(self,pagina,ptr):
        primer_ele = self.memoria_real[0]
        pagina.direccion = primer_ele.direccion
        pagina.bandera = True

        self.memoria_real[0] = pagina
    
    #def actualizar_memoria_virtual(self,pagina_remplazo,id):
        
                

    def actualizar_map(self,pagina,ptr):
        nueva_lista_paginas = []
        for llave,valor in self.map_memoria.items():
            if llave == ptr:
                for ele in valor:
                    if pagina.id == ele.id:
                        nueva_lista_paginas.append(pagina)
                    else:
                        nueva_lista_paginas.append(ele)
        self.map_memoria[ptr] = nueva_lista_paginas




    #-------------------------------------------------------------
    #           Funciones Auxiliares
    #------------------------------------------------------------
    def obtener_id_pagina(self):
        self.contador_paginas += 1
        return self.contador_paginas
    
    def direccion_memoria_real(self,pagina):
        dir =  self.contador_paginas - 1
        pagina.direccion = dir
        self.memoria_real[dir] = pagina
        return dir
    
    def direccion_espacio_libre_memoria_real(self):
        count = 0
        for ele in self.memoria_real:
            if ele == None:
                return count
            count += 1

    def intercambio_paginas(self,pagina):
        if len(self.memoria_real) < 100:
            dir = self.direccion_espacio_libre_memoria_real()
            self.memoria_real[dir] = pagina
            pagina.direccion = dir
            pagina.bandera = True
                
        else:
            #Llamar a algoritmos de remplazo de paginas
            return None
    
    def asignar_puntero_lista_procesos(self, pid, ptr):
        if pid not in self.proceos:
            self.proceos[pid] = [ptr]
        else:
            self.proceos[pid].append(ptr)


class Pagina:
    def _init_(self, id, direccion, bandera):
        self.id = id
        self.direccion = direccion
        self.bandera = bandera


class Proceso:
    def __init__(self,pid,MMU):
        self.pid = pid
        self.tabla_simbolos = []
        self.MMU = MMU
    
    def new (self, pid, size): 
        ptr = self.MMU.asignacion_memoria(pid,size)
        self.tabla_simbolos.append(ptr)

    def use (self, ptr): 
        if ptr in self.tabla_simbolos:
            self.MMU.use_memory(ptr) 
        else:
            print(f"Puntero {ptr} no encontrado en el proceso {self.pid}")
    def delete (self, ptr):
        if ptr in self.tabla_simbolos:
            self.MMMU.eliminar_memoria(ptr)
        else:
            print(f"Puntero {ptr} no encontrado en el proceso {self.pid}")

    def kill (self, pid): 
        for ptr in self.tabla_simbolos:
            self.MMU.eliminar_memoria(ptr)  
        self.tabla_simbolos.clear()
