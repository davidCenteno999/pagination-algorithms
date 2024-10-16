import componentes
from componentes import MMU, Pagina
#4096 -1
#8192 -2
#12288 -3

MMU1 = MMU(16, 4, 3) #memoria total 3 paginas





MMU1.new(1,8192) #2 ptr-1
MMU1.new(1,4096) #1 ptr-2
MMU1.new(1,4096) #1 ptr-3

MMU1.use(2)
MMU1.new(1,4096) #1 ptr-4
MMU1.imprimir_atributos()

print("--------------------------------------------------")
MMU1.use(4)
MMU1.imprimir_atributos()
