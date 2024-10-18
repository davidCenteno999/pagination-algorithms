import random
class MMU:
    def __init__(self, size_RAM, size_pagina, tipoAlgoritmo):
        self.size_RAM = size_RAM # 400KB -> 100 paginas
        self.size_pagina = size_pagina # 4KB 
        self.cantidadMaximaPaginas = self.size_RAM//self.size_pagina
        self.memoria_real = [None] * (self.cantidadMaximaPaginas) 
        self.memoria_virtual = []
        self.contador_paginas = 0
        self.map_memoria = {} #ptr asociado a sus paginas {ptr:[page1,pg2,pg3]}
        self.procesos = {} #Parecido a objeto de procesos {pid:[ptr,ptr2,ptr3]}
        self.punteros = {} #tabla de simbolos  {ptr:pid}
        self.tipoAlgoritmo = tipoAlgoritmo
        self.total_time = 0
        self.thrashing_time =0
        self.used_RAM = 0
        self.used_VRAM = 0
        self.used_pages = []
        self.future_pages = []


    

    #-------------------------------------------------------------
    #           Funciones Principales
    #------------------------------------------------------------
    #new (pid, size) : ptr 
    def new(self, pid, size):
        #Pasar de KB a bytes
        # 1KB = 1024 
        # 4KB = 4096
        #Numero de paginas
        numero_paginas = (size//4096) + (1 if size%4096!=0 else 0)
        #Generar puntero
        ptr = len(self.map_memoria) + 1
        paginas = []
        for i in range(numero_paginas):
            pagina = Pagina(self.obtener_id_pagina(),None,-1,0)
            if self.paginas_ocupadas_memoria_real() < (self.cantidadMaximaPaginas):
                dir = self.direccion_espacio_libre_memoria_real()
                pagina.bandera = True
                pagina.direccion = dir
                self.memoria_real[dir] = pagina
                
            else:
                pagina.bandera = False
                self.memoria_virtual.append(pagina)
            paginas.append(pagina)
            
        self.map_memoria[ptr] = paginas
        
        if pid not in self.procesos:
            self.procesos[pid] = [ptr] #Crear proceso
        else:
            self.procesos[pid].append(ptr) #Agregar ptr a proceso si ya existe

        if ptr not in self.punteros:
            self.punteros[ptr] = pid #Agregar ptr a tabla de simbolos

        return ptr
    
    #use(ptr) : void
    def use(self, ptr):
        if ptr in self.map_memoria:
            paginas = self.map_memoria[ptr]
            for pagina in paginas:
                pagina.mark = 1
                if not pagina.bandera:
                    self.intercambio_paginas(pagina,self.tipoAlgoritmo)

                self.used_pages.append(pagina)
        else:
            print("Punetero no encontrado.")

    #delete(ptr)
    def delete(self,ptr):
        if ptr in self.map_memoria:
            paginas = self.map_memoria.pop(ptr)
            for pagina in paginas:
                if pagina.bandera:
                    #self.memoria_real[pagina.direccion] = None
                    self.memoria_real.remove(pagina)
                else:
                    self.memoria_virtual.remove(pagina)

        pid = self.punteros[ptr] # Encontrar el proceso asociado al ptr
        self.procesos[pid].remove(ptr) #Eliminar ptr del proceso
    
    def kill (self, pid): 
        for ptr in self.procesos[pid]:
            self.delete(ptr)
        self.procesos.pop(pid)

    def intercambio_paginas(self,pagina,tipo):

        if(self.tipoAlgoritmo == 0): #FIFO
            self.fifo(pagina)
        if(self.tipoAlgoritmo == 1): #SC
            self.sc(pagina)
        if(self.tipoAlgoritmo == 2): #MRU
            self.MRU(pagina)
        if(self.tipoAlgoritmo == 3): #RND
            self.rnd(pagina)
        if(self.tipoAlgoritmo == 4): #OPT
            self.opt(pagina)

    #-------------------------------------------------------------
    #           Algoritmos
    #------------------------------------------------------------
    def fifo(self,pagina):
        self.memoria_virtual.remove(pagina)
        pagina_remplazo = self.memoria_real.pop(0)

        pagina.direccion = pagina_remplazo.direccion
        pagina.bandera = True
        pagina_remplazo.direccion = None
        pagina_remplazo.bandera = False

        self.memoria_real.append(pagina)
        self.memoria_virtual.append(pagina_remplazo)


        #self.actualizar_memoria_virtual(pagina_remplazo, pagina_remplazo.id)
        #self.actualizar_map(pagina,ptr)
        #self.actualizar_map(pagina_remplazo,None)

    def sc(self, pagina):
        # Recorre las páginas en memoria real para encontrar una que reemplazar
        while True:
            pagina_actual = self.memoria_real[0] 

            if pagina_actual.mark == 1:  
                ele = self.memoria_real.pop(0)
                ele.mark = 0 
                self.memoria_real.append(ele)  
            else:  
                self.fifo(pagina)
                break  
    
    def MRU(self, pagina):
        self.memoria_virtual.remove(pagina)
        if self.used_pages != []:
            pagina_remplazo = self.used_pages.pop()
            self.memoria_real.remove(pagina_remplazo)
        else:
            pagina_remplazo = self.memoria_real.pop(0)
        
        pagina.direccion = pagina_remplazo.direccion
        pagina.bandera = True
        pagina_remplazo.direccion = None
        pagina_remplazo.bandera = False

        self.memoria_real.insert(pagina_remplazo.direccion,pagina)
        self.memoria_virtual.append(pagina_remplazo)

    def rnd(self,pagina):
        self.memoria_virtual.remove(pagina)
        indice_remplazo = random.randint(0,self.paginas_ocupadas_memoria_real() - 1)
        pagina_remplazo = self.memoria_real.pop(indice_remplazo)
        
        pagina.direccion = pagina_remplazo.direccion
        pagina.bandera = True
        pagina_remplazo.direccion = None
        pagina_remplazo.bandera = False

        self.memoria_real.insert(indice_remplazo,pagina)
        self.memoria_virtual.append(pagina_remplazo)


    def opt(self, pagina):
        self.memoria_virtual.remove(pagina)
        pagina_remplazo = self.opt_out_page()
        self.memoria_real.remove(pagina_remplazo)
        pagina.direccion = pagina_remplazo.direccion
        pagina.bandera = True
        pagina_remplazo.direccion = None
        pagina_remplazo.bandera = False

    def opt_out_page(self): #Falta optimizar, mientras se usa un pagina quitarla del array de futuras paginas a usar
        out_page = None
        out_index = -1
        for pagina in self.memoria_real:
            page_found=0
            for i in range(0,len(self.future_pages)):

                if(self.future_pages[i].id == pagina.id):
                    page_found=1
                    if(out_index < i):
                        out_index = i
                        out_page = pagina
            if(page_found==0):
                out_index = -1
                out_page = pagina
                break
        return out_page

    #-------------------------------------------------------------
    #           Funciones Auxiliares
    #------------------------------------------------------------
    def obtener_id_pagina(self):
        self.contador_paginas += 1
        return self.contador_paginas
    
    def paginas_ocupadas_memoria_real(self):
        return sum(1 for page in self.memoria_real if page is not None)

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

        
    def imprimir_paginas(self, paginas):
        """Imprime las páginas en una lista, manejando si es None."""
        for i, pagina in enumerate(paginas):
            if pagina:
                print(f"  Posición {i}: {pagina}")
            else:
                print(f"  Posición {i}: Vacía")

    def imprimir_atributos(self):
        # Imprime los atributos básicos
        print(f"Tamaño de RAM: {self.size_RAM} KB")
        print(f"Tamaño de página: {self.size_pagina} KB")
        print(f"Contador de páginas: {self.contador_paginas}")
        print(f"Tipo de algoritmo: {self.tipoAlgoritmo}")
        
        # Imprime memoria real
        print("\nMemoria real:")
        self.imprimir_paginas(self.memoria_real)  # Pasa la lista de páginas a imprimir
        
        # Imprime memoria virtual
        print("\nMemoria virtual:")
        self.imprimir_paginas(self.memoria_virtual)  # Pasa la lista de páginas a imprimir

        print("\nPaginas Utilizadas:")
        self.imprimir_paginas(self.used_pages) 
        
        # Imprime map_memoria
        print("\nMapa de memoria (ptr -> páginas):")
        for ptr, paginas in self.map_memoria.items():
            print(f"  Puntero {ptr}:")
            self.imprimir_paginas(paginas)  # Pasa la lista de páginas a imprimir

        # Imprime procesos
        print("\nProcesos (pid -> ptrs):")
        for pid, ptrs in self.procesos.items():
            print(f"  Proceso {pid}:")
            for ptr in ptrs:
                print(f"    Puntero: {ptr}")

        # Imprime punteros
        print("\nPunteros (ptr -> pid):")
        for ptr, pid in self.punteros.items():
            print(f"  Puntero {ptr}: Proceso {pid}")

    
    def get_opt_state(self):
        # Retorna el estado actual de las páginas cargadas para el algoritmo OPT
        print(self.memoria_real)
        pages = []
        for page in self.memoria_real:
            if page != None:
                pages.append({'page_id': page.id, 'pid': 0, 'loaded': 0,
                'l_addr': 0, 'm_addr': page.direccion, 'd_addr': 0,
                'loaded_t': 0, 'mark': page.mark})
        return pages
    
    def get_alg_state(self):
        # Retorna el estado para otro algoritmo de reemplazo
        print(self.memoria_real)
        pages = []
        for page in self.memoria_real:
            if page != None:
                pages.append({'page_id': page.id, 'pid': 0, 'loaded': 0,
                'l_addr': 0, 'm_addr': page.direccion, 'd_addr': 0,
                'loaded_t': 0, 'mark': page.mark})
        return pages
    
    def get_summary_1(self):
        # Resumen personalizado
        return {
            'total_pages': len(self.memoria_real),
            'free_frames': 0
        }
        
    def get_summary_2(self):
        # Otro resumen personalizado
        return {
            'used_frames': len(self.memoria_real),
            'algorithm': self.tipoAlgoritmo
        }

class Pagina:
    def __init__(self, id, direccion, bandera, mark):
        self.id = id
        self.direccion = direccion
        self.bandera = bandera
        self.mark = mark
    
    
    def __str__(self):
        # Imprime los atributos del objeto Pagina de manera estructurada
        return f"Pagina(id={self.id}, direccion={self.direccion}, bandera={self.bandera})"
