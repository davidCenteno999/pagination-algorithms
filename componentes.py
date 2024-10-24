import random
class MMU:
    def __init__(self, size_RAM, size_pagina, tipoAlgoritmo):
        self.size_RAM = size_RAM # 400KB -> 100 paginas
        self.size_pagina = size_pagina # 4KB 
        self.cantidadMaximaPaginas = self.size_RAM//self.size_pagina
        self.memoria_real = []
        self.memoria_virtual = []
        self.contador_paginas = 0
        self.map_memoria = {} #ptr asociado a sus paginas {ptr:[page1,pg2,pg3]}
        self.procesos = {} #Parecido a objeto de procesos {pid:[ptr,ptr2,ptr3]}
        self.punteros = {} #tabla de simbolos  {ptr:pid}
        self.total_punteros = 1
        self.total_paginas = 0
        self.total_procesos = 0
        self.simTime = 0
        self.paginas_real = 0
        self.tipoAlgoritmo = tipoAlgoritmo
        self.total_time = 0
        self.thrashing_time =0
        self.used_RAM = 0
        self.used_VRAM = 0
        self.used_pages = []
        self.cant_used_pages = 0
        self.future_pages = []
        self.fifoList = []
        self.fragmentacion = 0
        self.future_pages_aux = []


    

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
        ptr = self.total_punteros
        self.total_punteros+=1
        paginas = []
        for i in range(numero_paginas):
            pagina = Pagina(self.obtener_id_pagina(),None,-1,0,pid,ptr,self.simTime,(round((numero_paginas*4096)-size)))
            if self.paginas_real < (self.cantidadMaximaPaginas):
                self.used_RAM+=4
                dir = self.paginas_real
                pagina.bandera = True
                pagina.direccion = dir
                self.memoria_real.append(pagina)
                self.fifoList.append(pagina)
                self.paginas_real+=1
                self.total_paginas+=1
                self.fragmentacion += pagina.fragmentacion
                
            else:
                self.used_VRAM+=round(size/4096)
                pagina.bandera = False
                self.memoria_virtual.append(pagina)
                self.total_paginas+=1
            paginas.append(pagina)
            
        self.map_memoria[ptr] = paginas
        
        if pid not in self.procesos:
            self.procesos[pid] = [ptr] #Crear proceso
            self.total_procesos+=1
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
                if(self.tipoAlgoritmo==4):
                    del self.future_pages[0]
                self.cant_used_pages+=1
                pagina.mark = 1
                if not pagina.bandera:
                    self.intercambio_paginas(pagina)
                    self.simTime+=5
                    self.thrashing_time+=5
                else:
                    self.simTime+=1
                self.used_pages.append(pagina)
                self.future_pages_aux.append(pagina.id)
                
                
        else:
            return

    #delete(ptr)
    def delete(self,ptr):
        if ptr in self.map_memoria:
            paginas = self.map_memoria.pop(ptr)
            for pagina in paginas:
                if pagina.bandera:
                    if(pagina in self.memoria_real):
                        self.memoria_real.remove(pagina)
                        self.paginas_real-=1
                        self.total_paginas-=1
                        self.used_RAM-=4
                        self.fifoList.remove(pagina)
                        self.fragmentacion-=pagina.fragmentacion
                else:
                    if(pagina in self.memoria_virtual):
                        self.memoria_virtual.remove(pagina)
                        self.total_paginas-=1
                        self.used_VRAM-=4

        pid = self.punteros[ptr] # Encontrar el proceso asociado al ptr
        if pid in self.procesos:
            self.procesos[pid].remove(ptr) #Eliminar ptr del proceso
    
    def kill (self, pid): 
        for ptr in self.procesos[pid]:
            self.delete(ptr)
        self.procesos.pop(pid)

    def intercambio_paginas(self,pagina):

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
        pagina_remplazo = self.fifoList.pop(0)
        self.memoria_real.remove(pagina_remplazo)

        pagina.direccion = pagina_remplazo.direccion
        pagina.bandera = True
        pagina_remplazo.direccion = None
        pagina_remplazo.bandera = False

        self.memoria_real.append(pagina)
        self.memoria_virtual.append(pagina_remplazo)
        self.fifoList.append(pagina)

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
            if pagina_remplazo in self.memoria_real:
                self.memoria_real.remove(pagina_remplazo)
        else:
            pagina_remplazo = self.memoria_real.pop(0)
        
        pagina.direccion = pagina_remplazo.direccion
        pagina.bandera = True
        pagina_remplazo.direccion = None
        pagina_remplazo.bandera = False

        self.memoria_real.append(pagina)
        self.memoria_virtual.append(pagina_remplazo)
        self.fifoList.append(pagina)

    def rnd(self,pagina):
        self.memoria_virtual.remove(pagina)
        indice_remplazo = random.randint(0,self.paginas_ocupadas_memoria_real() - 1)
        pagina_remplazo = self.memoria_real.pop(indice_remplazo)
        
        pagina.direccion = pagina_remplazo.direccion
        pagina.bandera = True
        pagina_remplazo.direccion = None
        pagina_remplazo.bandera = False

        self.memoria_real.append(pagina)
        self.memoria_virtual.append(pagina_remplazo)
        self.fifoList.append(pagina)

    def fifo(self,pagina):
        self.memoria_virtual.remove(pagina)
        pagina_remplazo = self.fifoList.pop(0)
        self.memoria_real.remove(pagina_remplazo)

        pagina.direccion = pagina_remplazo.direccion
        pagina.bandera = True
        pagina_remplazo.direccion = None
        pagina_remplazo.bandera = False

        self.memoria_real.append(pagina)
        self.memoria_virtual.append(pagina_remplazo)
        self.fifoList.append(pagina)

    def opt(self, pagina):
        self.memoria_virtual.remove(pagina)
        pagina_remplazo = self.opt_out_page()
        self.memoria_real.remove(pagina_remplazo)

        pagina.direccion = pagina_remplazo.direccion
        pagina.bandera = True
        pagina_remplazo.direccion = None
        pagina_remplazo.bandera = False

        self.memoria_virtual.append(pagina_remplazo)
        self.memoria_real.append(pagina)
        self.fifoList.append(pagina)


    def opt_out_page(self): #Falta optimizar, mientras se usa un pagina quitarla del array de futuras paginas a usar
        out_page = None
        out_index = -1
        for pagina in self.memoria_real:
            if pagina.id not in self.future_pages:
                out_page = pagina
                break
            i = self.future_pages.index(pagina.id)
            if(out_index < i):
                out_index = i
                out_page = pagina
                    
        #print("PAGINA SALIDA:")
        #print(out_page)
        
        return out_page

    #-------------------------------------------------------------
    #           Funciones Auxiliares
    #------------------------------------------------------------

    def set_future_pages(self,future_pages):
        self.future_pages = future_pages

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
        for i in range(0,len(paginas)):
            if paginas[i]:
                print(f"  Posición {i}: {paginas[i]}")
            #else:
            #    print(f"  Posición {i}: Vacía")

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
        #print("\nPunteros (ptr -> pid):")
        #for ptr, pid in self.punteros.items():
        #    print(f"  Puntero {ptr}: Proceso {pid}")
            

    
    def get_pages_state(self):
        # Retorna el estado actual de las páginas cargadas para el algoritmo OPT
        #print(self.memoria_real)
        pages = []
        for page in self.memoria_real:
            if page != None:
                pages.append({'page_id': page.id, 'pid': page.pid, 'loaded': page.bandera,
                'l_addr': page.ptr, 'm_addr': page.direccion, 'd_addr': 0,
                'loaded_t': page.loadTime, 'mark': page.mark})
        return pages
    
    
    def get_summary_1(self):
        # Resumen personalizado
        algoritmo = ""
        if (self.tipoAlgoritmo == 0):
            algoritmo = "FIFO"
        elif (self.tipoAlgoritmo == 1):
            algoritmo = "SC"
        elif (self.tipoAlgoritmo == 2):
            algoritmo = "MRU"
        elif (self.tipoAlgoritmo == 3):
            algoritmo = "RND"
        else:
            algoritmo = "Optimo"
        
        thrashingP = 0
        if (self.simTime != 0):
            thrashingP = (self.thrashing_time / self.simTime) * 100

        
        return {
            'total_pages': self.total_paginas,
            'unloaded_pages': len(self.memoria_virtual),
            'free_frames': 0,
            'loaded_pages': self.paginas_real,
            'processes': self.total_procesos,
            'simTime': self.simTime,
            'thrashing': self.thrashing_time,
            'thrashingP': thrashingP,
            'usedRam': self.used_RAM,
            'usedRamPer': (self.used_RAM/self.size_RAM)*100,
            'usedVRam': self.used_VRAM,
            'algorithm': algoritmo,
            'paginas_usadas': self.cant_used_pages,
            'fragmentacion': self.fragmentacion//4096

        }
        
    def get_summary_2(self):
        # Otro resumen personalizado
        return {
            
        }

class Pagina:
    def __init__(self, id, direccion, bandera, mark, pid, ptr, loadTime, fragmentacion):
        self.id = id
        self.direccion = direccion
        self.bandera = bandera
        self.mark = mark
        self.pid = pid
        self.ptr = ptr
        self.loadTime = loadTime
        self.fragmentacion = fragmentacion
    
    
    def __str__(self):
        # Imprime los atributos del objeto Pagina de manera estructurada
        return f"Pagina(id={self.id}, direccion={self.direccion}, bandera={self.bandera})"
