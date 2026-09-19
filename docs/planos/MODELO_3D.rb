# encoding: UTF-8
#----------------------------------------------------------------------------
#  LOCAL DE HOSTELERIA — MODELO 3D PARA SKETCHUP
#
#  Generado por docs/planos/export_sketchup.py desde estructura.py,
#  mobiliario.py y equipamiento.py, que son las mismas fuentes que
#  dibujan las cuatro laminas. Ninguna coordenada esta escrita a mano.
#
#  USO — consola Ruby de SketchUp:
#      load "C:/ruta/MODELO_3D.rb"
#  o pegar el archivo entero. Se construye al cargarlo. Para rehacerlo:
#      Local3D.build
#  Para borrar lo construido:
#      Local3D.clear
#
#  UNIDADES: metros. Cada numero se convierte con .m, asi que el modelo
#  sale a milimetro exacto sobre las cotas del plano.
#
#  ORIGEN: esquina interior Suroeste del local (0,0,0), X al Este,
#  Y al Norte, Z hacia arriba. Es el mismo origen de obra del plano.
#
#  ALTURAS (en planta todo esta medido; en altura, solo el suelo a suelo)
#      Suelo a suelo                           2.560 m   medido en obra
#      Canto del forjado                       0.250 m   SUPUESTO — COMPROBAR
#      Intrados del forjado                    2.310 m   derivado
#      Altura libre del altillo                2.500 m   sin medir
#      Techo del altillo                       5.060 m   derivado
#      Coronacion del acristalamiento          4.700 m   aproximada — COMPROBAR
#      Travesano del ventanal Sur              2.300 m   sin medir — COMPROBAR
#      Zocalo de piedra de la carpinteria      0.130 m   medido
#      Alto del zocalo del ventanal            0.130 m   SUPUESTO — COMPROBAR
#      Intrados de la viga P1b                 2.100 m   SUPUESTO — COMPROBAR
#      Pared en L                              1.220 m   medida
#      Vidrio sobre la pared en L              1.350 m   medido
#      Huecos de paso                          2.100 m   estandar
#      Antepechos de vidrio                    1.000 m   estandar
#      Encimeras                               0.900 m   estandar
#      Borde inferior de la campana            2.000 m   estandar
#      Estante mural de la trasbarra           1.600 m   SUPUESTO — sobre el aparato más alto
#      Sillon corrido: asiento / respaldo      0.420 m   SUPUESTO — fondo sin medir
#      Cara vista del cassette de aire         2.280 m   empotrado, panel a haces con el techo
#      Cuerpo del cassette (en el forjado)     2.310 m   sube hasta 2,560
#      Revestimiento del frente de la barra    0.900 m   hasta la encimera
#
#  CADENA DE OBRA DEL LADO OESTE (la que fijo el cliente)
#      Cara interior del zocalo del ventanal          1,968
#      + barra 2,79  -> cara Sur de P1                4,759
#      + paso 0,598  -> cara NORTE de P1 = base de la L 5,357
#      + pared en L 3,600  -> muro Norte              8,957
#      + hundimiento 0,051  -> pared hundida de la cocina 9,008
#      + espesor del muro  -> borde del solar         9,156
#      De la pared hundida a la cara Norte de P1      3,651  (los 3,65 del cliente)
#
#  PASOS LIBRES MEDIDOS SOBRE EL MODELO
#      Entre las mesas del ventanal                   0,600 y 0,600
#      Libre delante del mostrador                    1,000
#      Entre las dos filas de sillas (pasillo del ventanal) 1,202
#      Entre la silla de M2 y la nevera A7            0,450
#      Puerta -> barra, por el Norte de la fila central 0,700
#      Salida del personal de la barra a la sala      1,310
#      Pasillo de la cocina                           0,840 a 0,980
#
#  CONFLICTOS QUE EL MODELO DEJA A LA VISTA (son del proyecto, no del 3D)
#      El vidrio de la pared en L corona en 2,570 y el forjado arranca en 2,310:
#        no pasa por debajo del altillo. Ya estaba anotado en COMPROBAR.
#      La viga P1b (y 4,933-5,183) muere en x=2,380, en el aire: con la pared en L
#        arrancando ahora en y=5,357, su extremo Este se quedo sin apoyo.
#      El lavavajillas K6 es 0,013 mas alto y 0,051 mas hondo que el fregadero K7
#        bajo el que va: asoma por encima de la encimera y por delante.
#      El lavavasos B1 mide 0,670 de alto y el hueco bajo la vitrina V2 es de 0,600:
#        no cabe debajo.
#      Las vitrinas son de 0,70 de fondo sobre un mostrador de 0,63: vuelan 0,07
#        sobre el paso de personal. En el 3D se dibujan al fondo del mostrador.
#      El machon P4 se mete 0,201 en el ancho de la escalera: al pasarlo quedan
#        0,878 libres, no los 1,079 del tramo.
#      Cuatro empotrados del proyecto original (x=1,10) caen en la cocina, que es
#        doble altura: no hay techo donde empotrarlos.
#      El empotrado de (1,10 / 8,50) cae dentro de la campana.
#      Los dos apliques del proyecto original caen sobre los armarios K8 y K9; en
#        el 3D se suben a 1,95 para que se vean.
#      El horno K5 se dibuja en el suelo: el plano no dice sobre que apoya.
#      El aire AC1 va empotrado en el forjado, como pide el cliente: el cuerpo de
#        la maquina (0,250) ocupa el canto entero del suelo del altillo. Hay que
#        dejar el hueco al hormigonar o resolverlo por encima del forjado.
#----------------------------------------------------------------------------

# recargar el fichero no debe llenar la consola de avisos de constante
Object.send(:remove_const, :Local3D) if defined?(Local3D)

module Local3D

  NOMBRE_MODELO = "Local de hosteleria"

  # --- materiales: [clave, nombre, r, g, b]
  MATERIALES = [
    ["muro", "Muro", 196, 192, 186],
    ["pilar", "Pilar", 120, 118, 114],
    ["tabique", "Tabique", 214, 210, 202],
    ["forjado", "Forjado", 176, 172, 165],
    ["solera", "Solera", 150, 148, 145],
    ["vidrio", "Vidrio", 150, 190, 205],
    ["carp", "Carpinteria", 70, 90, 100],
    ["madera", "Madera", 168, 124, 78],
    ["mesa", "Mesa", 206, 190, 166],
    ["silla", "Silla", 138, 111, 78],
    ["sillon", "Sillon", 128, 96, 78],
    ["inox", "Inox", 198, 202, 206],
    ["aparato", "Aparato", 120, 138, 150],
    ["frio", "Equipo de frio", 168, 198, 212],
    ["encimera", "Encimera", 222, 214, 198],
    ["piedra", "Piedra", 186, 182, 176],
    ["escalera", "Escalera", 162, 158, 152],
    ["luz", "Luminaria", 246, 232, 180],
    ["aire", "Aire acondicionado", 238, 238, 235],
    ["rejilla", "Rejilla", 176, 178, 178],
    ["falso", "Falso techo", 240, 238, 234],
  ]

  # --- capas
  CAPAS = [
    "01 Solera",
    "02 Muros",
    "03 Pilares",
    "04 Carpinteria",
    "05 Pared en L",
    "06 Zocalo",
    "07 Bano",
    "08 Escalera",
    "09 Forjado",
    "10 Cocina",
    "11 Barra",
    "12 Sala",
    "13 Instalaciones",
    "14 Planta alta",
    "15 Techo",
  ]
  CAPAS_OCULTAS = ["15 Techo"]

  # --- cajas: [capa, material, nombre, x0, y0, x1, y1, z0, z1]
  CAJAS = [
    ["02 Muros", "muro", "Medianera Norte", 2.4300, 8.9570, 10.0400, 9.1560, 0.0000, 5.0600],
    ["02 Muros", "muro", "Medianera Norte - cocina", 0.0000, 9.0080, 2.4300, 9.1560, 0.0000, 5.0600],
    ["02 Muros", "muro", "Muro Oeste", 0.0000, 2.0090, 0.2500, 9.0080, 0.0000, 5.0600],
    ["02 Muros", "muro", "Muro Oeste - esquina SO", 0.0000, 1.5610, 0.5100, 2.0090, 0.0000, 5.0600],
    ["02 Muros", "muro", "Muro Oeste del cuello", 5.7310, 0.9600, 5.9800, 1.5610, 0.0000, 5.0600],
    ["02 Muros", "muro", "Medianera Este", 9.8900, 1.4290, 10.0400, 8.9570, 0.0000, 5.0600],
    ["02 Muros", "muro", "Medianera Este - cuello", 9.7100, 0.3300, 10.0400, 1.4290, 0.0000, 5.0600],
    ["03 Pilares", "pilar", "P1 · Machón del muro Oeste", 0.2500, 4.7590, 0.5500, 5.3570, 0.0000, 5.0600],
    ["03 Pilares", "pilar", "P2 · Pilastra del muro Sur", 1.2900, 1.5610, 1.8700, 2.0110, 0.0000, 5.0600],
    ["03 Pilares", "pilar", "P3 · Pilar central", 5.6700, 4.6880, 6.3200, 5.7580, 0.0000, 5.0600],
    ["03 Pilares", "pilar", "P4 · Machón de la medianera Este", 9.6890, 4.7080, 9.8900, 5.3090, 0.0000, 5.0600],
    ["03 Pilares", "pilar", "P5 · Pilar de fachada", 5.7310, 0.0000, 6.3310, 1.0000, 0.0000, 5.0600],
    ["03 Pilares", "pilar", "Viga P1b", 0.5500, 4.9330, 2.3800, 5.1830, 2.1000, 2.3100],
    ["04 Carpinteria", "vidrio", "Ventanal Sur · paño 1", 0.5100, 1.5730, 1.2900, 1.6090, 0.1300, 4.7000],
    ["04 Carpinteria", "carp", "Ventanal Sur · travesaño 1", 0.5100, 1.5610, 1.2900, 1.6210, 2.2700, 2.3300],
    ["04 Carpinteria", "piedra", "Ventanal Sur · zócalo de piedra 1", 0.5100, 1.5610, 1.2900, 1.6210, 0.0000, 0.1300],
    ["04 Carpinteria", "vidrio", "Ventanal Sur · paño 2", 1.8700, 1.5730, 5.8700, 1.6090, 0.1300, 4.7000],
    ["04 Carpinteria", "carp", "Ventanal Sur · travesaño 2", 1.8700, 1.5610, 5.8700, 1.6210, 2.2700, 2.3300],
    ["04 Carpinteria", "piedra", "Ventanal Sur · zócalo de piedra 2", 1.8700, 1.5610, 5.8700, 1.6210, 0.0000, 0.1300],
    ["02 Muros", "muro", "Dintel de fachada Sur 1 (SUPUESTO)", 0.5100, 1.5610, 1.2900, 1.6210, 4.7000, 5.0600],
    ["02 Muros", "muro", "Dintel de fachada Sur 2 (SUPUESTO)", 1.8700, 1.5610, 5.8700, 1.6210, 4.7000, 5.0600],
    ["02 Muros", "muro", "Ventanal Sur · jamba", 5.8700, 1.5610, 5.9800, 1.8100, 0.0000, 5.0600],
    ["04 Carpinteria", "vidrio", "Escaparate · vidrio", 6.3310, 0.3800, 7.6410, 0.4090, 0.1300, 4.7000],
    ["02 Muros", "muro", "Dintel de fachada Este (SUPUESTO)", 6.3310, 0.3700, 9.7100, 0.4190, 4.7000, 5.0600],
    ["04 Carpinteria", "piedra", "Escaparate · zócalo de piedra", 6.3310, 0.3700, 9.7100, 0.4190, 0.0000, 0.1300],
    ["04 Carpinteria", "vidrio", "Puerta de acceso · hoja 1", 7.6410, 0.3700, 8.6710, 0.4190, 0.1300, 2.1000],
    ["04 Carpinteria", "vidrio", "Puerta de acceso · hoja 2", 8.6710, 0.3700, 9.7010, 0.4190, 0.1300, 2.1000],
    ["04 Carpinteria", "vidrio", "Puerta de acceso · montante superior", 7.6410, 0.3800, 9.7010, 0.4090, 2.1000, 4.7000],
    ["05 Pared en L", "tabique", "Tramo largo 3,60", 2.4300, 5.3570, 2.5300, 8.9570, 0.0000, 1.2200],
    ["05 Pared en L", "tabique", "Doblez 0,74", 1.7900, 5.3570, 2.5300, 5.4570, 0.0000, 1.2200],
    ["05 Pared en L", "vidrio", "Tramo largo 3,60 · vidrio", 2.4600, 5.4570, 2.5000, 8.9270, 1.2200, 2.5700],
    ["06 Zocalo", "piedra", "Zócalo del ventanal", 0.5100, 1.6210, 1.2900, 1.9680, 0.0000, 0.1300],
    ["06 Zocalo", "piedra", "Zócalo del ventanal", 1.8700, 1.6210, 5.8700, 1.9680, 0.0000, 0.1300],
    ["07 Bano", "tabique", "Tabique Oeste del baño", 7.4000, 7.7300, 7.5000, 8.9570, 0.0000, 2.3100],
    ["07 Bano", "tabique", "Tabique Sur - tramo Oeste", 7.4000, 7.7300, 7.7700, 7.8300, 0.0000, 2.3100],
    ["07 Bano", "tabique", "Tabique Sur - tramo Este", 8.4700, 7.7300, 9.8900, 7.8300, 0.0000, 2.3100],
    ["07 Bano", "tabique", "Baño · dintel de la puerta", 7.7700, 7.7300, 8.4700, 7.8300, 2.1000, 2.3100],
    ["07 Bano", "madera", "Baño · hoja de la puerta", 7.7700, 7.7500, 8.4700, 7.7900, 0.0000, 2.1000],
    ["08 Escalera", "escalera", "Peldaño 1", 8.8110, 3.5790, 9.8900, 3.8389, 0.0000, 0.1506],
    ["08 Escalera", "escalera", "Peldaño 2", 8.8110, 3.8389, 9.8900, 4.0989, 0.0000, 0.3012],
    ["08 Escalera", "escalera", "Peldaño 3", 8.8110, 4.0989, 9.8900, 4.3588, 0.0000, 0.4518],
    ["08 Escalera", "escalera", "Peldaño 4", 8.8110, 4.3588, 9.8900, 4.6188, 0.0000, 0.6024],
    ["08 Escalera", "escalera", "Peldaño 5", 8.8110, 4.6188, 9.8900, 4.7080, 0.0000, 0.7529],
    ["08 Escalera", "escalera", "Peldaño 5", 8.8110, 4.7080, 9.6890, 4.8787, 0.0000, 0.7529],
    ["08 Escalera", "escalera", "Peldaño 6", 8.8110, 4.8787, 9.6890, 5.1386, 0.0000, 0.9035],
    ["08 Escalera", "escalera", "Peldaño 7", 8.8110, 5.1386, 9.6890, 5.3090, 0.0000, 1.0541],
    ["08 Escalera", "escalera", "Peldaño 7", 8.8110, 5.3090, 9.8900, 5.3986, 0.0000, 1.0541],
    ["08 Escalera", "escalera", "Peldaño 8", 8.8110, 5.3986, 9.8900, 5.6585, 0.0000, 1.2047],
    ["08 Escalera", "escalera", "Peldaño 9", 8.8110, 5.6585, 9.8900, 5.9184, 0.0000, 1.3553],
    ["08 Escalera", "escalera", "Peldaño 10", 8.8110, 5.9184, 9.8900, 6.1784, 0.0000, 1.5059],
    ["08 Escalera", "escalera", "Peldaño 11", 8.8110, 6.1784, 9.8900, 6.4383, 0.0000, 1.6565],
    ["08 Escalera", "escalera", "Peldaño 12", 8.8110, 6.4383, 9.8900, 6.6983, 0.0000, 1.8071],
    ["08 Escalera", "escalera", "Peldaño 13", 8.8110, 6.6983, 9.8900, 6.9582, 0.0000, 1.9576],
    ["08 Escalera", "escalera", "Peldaño 14", 8.8110, 6.9582, 9.8900, 7.2181, 0.0000, 2.1082],
    ["08 Escalera", "escalera", "Peldaño 15", 8.8110, 7.2181, 9.8900, 7.4781, 0.0000, 2.2588],
    ["08 Escalera", "escalera", "Peldaño 16", 8.8110, 7.4781, 9.8900, 7.7380, 0.0000, 2.4094],
    ["10 Cocina", "inox", "Bancada de cocción a medida", 0.2500, 8.4080, 2.4300, 9.0080, 0.0000, 0.9000],
    ["10 Cocina", "aparato", "K1 · Placa de inducción Bartscher, 2 zonas Ø230, 6 kW, 400 V", 0.2500, 8.5530, 0.9500, 9.0080, 0.9000, 1.0200],
    ["10 Cocina", "aparato", "K2 · Cocedor de pasta eléctrico METRO Professional GNC1008, 8 L, 4 cestos", 0.9500, 8.4580, 1.4200, 9.0080, 0.9000, 1.2800],
    ["10 Cocina", "aparato", "K3 · Freidora profesional 1 cuba de 7 L, eléctrica", 1.4200, 8.5480, 1.6900, 9.0080, 0.9000, 1.2700],
    ["10 Cocina", "aparato", "K4 · Plancha eléctrica Cleiton 50 cm, placa de 8 mm, sobremesa", 1.6900, 8.5080, 2.2400, 9.0080, 0.9000, 1.2300],
    ["10 Cocina", "inox", "KC · Campana extractora industrial recta, sin turbina, AISI-304 satinado, 2 × 1,2 m", 0.3100, 7.8080, 2.3100, 9.0080, 2.0000, 2.5000],
    ["10 Cocina", "aparato", "K5 · Horno de convección eléctrico industrial, 4 bandejas 45 × 33", 0.2500, 7.8180, 0.8450, 8.4080, 0.0000, 0.5750],
    ["10 Cocina", "inox", "K7 · Fregadero con bastidor con hueco lavavajillas, cuba izquierda, 1200 × 600 · cuba", 0.2500, 6.6180, 0.8500, 7.2180, 0.0000, 0.8500],
    ["10 Cocina", "inox", "K7 · Fregadero con bastidor con hueco lavavajillas, cuba izquierda, 1200 × 600 · escurridor", 0.2500, 7.2180, 0.8500, 7.8180, 0.8100, 0.8500],
    ["10 Cocina", "aparato", "K6 · Lavavajillas industrial ST500, cesta 50 × 50, bajo el escurridor de K7", 0.2500, 7.2355, 0.9010, 7.8005, 0.0000, 0.8630],
    ["10 Cocina", "frio", "K8 · Armario refrigerado vertical Edenox APS-451 I, inox, 1 puerta, 395 L", 0.2500, 5.9920, 0.9900, 6.6180, 0.0000, 1.8650],
    ["10 Cocina", "frio", "K9 · Armario refrigerado vertical Edenox APS-451 I, inox, 1 puerta, 395 L", 0.2500, 5.3660, 0.9900, 5.9920, 0.0000, 1.8650],
    ["10 Cocina", "frio", "K10 · Mesa refrigerada Infrico 4 puertas, AISI-304, peto 100 mm, -2/+8 ºC, 530 L", 1.8300, 5.4570, 2.4300, 7.9990, 0.0000, 0.8500],
    ["11 Barra", "encimera", "Mesada de la trasbarra a medida", 0.2500, 2.6110, 0.8500, 4.7590, 0.8600, 0.9000],
    ["11 Barra", "inox", "A4 · Fregadero de pie 1 seno con estante y bastidor, 600 × 600 × 850", 0.2500, 2.0110, 0.8500, 2.6110, 0.0000, 0.8500],
    ["11 Barra", "aparato", "A1 · Cafetera (comprada), 2 grupos", 0.2500, 3.7590, 0.8500, 4.7590, 0.9000, 1.4000],
    ["11 Barra", "aparato", "A2 · Molinillo de café Cunil TRANQUILO de ABC, 275 W, tolva 0,5 kg", 0.2500, 3.5890, 0.5900, 3.7590, 0.9000, 1.3100],
    ["11 Barra", "aparato", "A3 · Máquina de helado y crema fría Bras B-CREAM1HD, 6 L, italiana", 0.2500, 3.3590, 0.7400, 3.5590, 0.9000, 1.5200],
    ["11 Barra", "frio", "A5 · Botellero frigorífico BTL1000, 2 puertas correderas, 240 L", 0.2500, 2.6110, 0.8300, 3.6510, 0.0000, 0.8500],
    ["11 Barra", "inox", "A6 · Estante mural cartelas compacto Fricosmos 011410, 1250 × 400 × 245 (1)", 0.2500, 3.5090, 0.6500, 4.7590, 1.6000, 1.8450],
    ["11 Barra", "inox", "A6 · Estante mural cartelas compacto Fricosmos 011410, 1250 × 400 × 245 (2)", 0.2500, 2.2590, 0.6500, 3.5090, 1.6000, 1.8450],
    ["11 Barra", "encimera", "Mostrador delantero a medida", 1.9000, 3.9680, 2.4800, 4.7590, 0.0000, 0.9000],
    ["11 Barra", "madera", "Frente de la barra · revestimiento de madera (logo y LED)", 2.5000, 1.9680, 2.5300, 4.7590, 0.0500, 0.9000],
    ["11 Barra", "madera", "Frente de la barra · retranqueo inferior para la tira de LED", 2.4800, 1.9680, 2.5000, 4.7590, 0.0000, 0.0500],
    ["11 Barra", "madera", "Mostrador · tabla de madera", 1.9000, 3.9680, 2.5300, 4.7590, 0.9000, 0.9400],
    ["11 Barra", "aparato", "V2 · motor", 2.1800, 1.9680, 2.4800, 2.2680, 0.0000, 0.3000],
    ["11 Barra", "vidrio", "V2 · Vitrina refrigerada (comprada), 1,00 × 0,70; debajo, lavavasos", 1.9000, 1.9680, 2.5000, 2.9680, 0.6000, 1.2500],
    ["11 Barra", "aparato", "V1 · motor", 2.1800, 2.9680, 2.4800, 3.2680, 0.0000, 0.3000],
    ["11 Barra", "vidrio", "V1 · Vitrina refrigerada (comprada), 1,00 × 0,70; hueco libre debajo", 1.9000, 2.9680, 2.5000, 3.9680, 0.6000, 1.2500],
    ["11 Barra", "aparato", "B1 · Lavavasos Elettrobar FAST 40, cesta 40 × 40 (bajo la vitrina V2)", 1.9400, 2.2980, 2.4800, 2.7380, 0.0000, 0.6700],
    ["11 Barra", "aparato", "B3 · Caja: tablet sobre soporte (lo único que queda en el mostrador)", 2.0500, 4.1680, 2.2500, 4.4180, 0.9400, 1.1900],
    ["11 Barra", "madera", "Tabla de P2", 0.5100, 1.6210, 1.2900, 2.0110, 0.9000, 0.9400],
    ["11 Barra", "inox", "B4 · Columna de cerveza en T de 3 grifos, bandeja 40 × 40, sobre la tabla de P2", 0.7900, 1.7010, 1.1900, 2.1010, 0.9400, 1.4900],
    ["12 Sala", "frio", "A7 · Armario expositor de bebidas Gasfrit, 1 puerta de cristal, 400 L", 5.7250, 4.1080, 6.2650, 4.6880, 0.0000, 1.9200],
    ["12 Sala", "mesa", "M1 · tablero", 3.5300, 2.4880, 4.2300, 3.1880, 0.7100, 0.7500],
    ["12 Sala", "silla", "M1 · pie 1", 3.8400, 2.7980, 3.9200, 2.8780, 0.0000, 0.7100],
    ["12 Sala", "silla", "M1 · base 1", 3.6800, 2.6380, 4.0800, 3.0380, 0.0000, 0.0200],
    ["12 Sala", "silla", "M1 · silla 1 · asiento", 3.6700, 3.2380, 4.0900, 3.6580, 0.4100, 0.4500],
    ["12 Sala", "silla", "M1 · silla 1 · pata", 3.6700, 3.2380, 3.7100, 3.2780, 0.0000, 0.4100],
    ["12 Sala", "silla", "M1 · silla 1 · pata", 4.0500, 3.2380, 4.0900, 3.2780, 0.0000, 0.4100],
    ["12 Sala", "silla", "M1 · silla 1 · pata", 3.6700, 3.6180, 3.7100, 3.6580, 0.0000, 0.4100],
    ["12 Sala", "silla", "M1 · silla 1 · pata", 4.0500, 3.6180, 4.0900, 3.6580, 0.0000, 0.4100],
    ["12 Sala", "silla", "M1 · silla 1 · respaldo", 3.6700, 3.6080, 4.0900, 3.6580, 0.4500, 0.8800],
    ["12 Sala", "silla", "M1 · silla 2 · asiento", 3.6700, 2.0180, 4.0900, 2.4380, 0.4100, 0.4500],
    ["12 Sala", "silla", "M1 · silla 2 · pata", 3.6700, 2.0180, 3.7100, 2.0580, 0.0000, 0.4100],
    ["12 Sala", "silla", "M1 · silla 2 · pata", 4.0500, 2.0180, 4.0900, 2.0580, 0.0000, 0.4100],
    ["12 Sala", "silla", "M1 · silla 2 · pata", 3.6700, 2.3980, 3.7100, 2.4380, 0.0000, 0.4100],
    ["12 Sala", "silla", "M1 · silla 2 · pata", 4.0500, 2.3980, 4.0900, 2.4380, 0.0000, 0.4100],
    ["12 Sala", "silla", "M1 · silla 2 · respaldo", 3.6700, 2.0180, 4.0900, 2.0680, 0.4500, 0.8800],
    ["12 Sala", "mesa", "M3 · tablero", 4.8300, 2.4880, 5.5300, 3.1880, 0.7100, 0.7500],
    ["12 Sala", "silla", "M3 · pie 1", 5.1400, 2.7980, 5.2200, 2.8780, 0.0000, 0.7100],
    ["12 Sala", "silla", "M3 · base 1", 4.9800, 2.6380, 5.3800, 3.0380, 0.0000, 0.0200],
    ["12 Sala", "silla", "M3 · silla 1 · asiento", 4.9700, 3.2380, 5.3900, 3.6580, 0.4100, 0.4500],
    ["12 Sala", "silla", "M3 · silla 1 · pata", 4.9700, 3.2380, 5.0100, 3.2780, 0.0000, 0.4100],
    ["12 Sala", "silla", "M3 · silla 1 · pata", 5.3500, 3.2380, 5.3900, 3.2780, 0.0000, 0.4100],
    ["12 Sala", "silla", "M3 · silla 1 · pata", 4.9700, 3.6180, 5.0100, 3.6580, 0.0000, 0.4100],
    ["12 Sala", "silla", "M3 · silla 1 · pata", 5.3500, 3.6180, 5.3900, 3.6580, 0.0000, 0.4100],
    ["12 Sala", "silla", "M3 · silla 1 · respaldo", 4.9700, 3.6080, 5.3900, 3.6580, 0.4500, 0.8800],
    ["12 Sala", "silla", "M3 · silla 2 · asiento", 4.9700, 2.0180, 5.3900, 2.4380, 0.4100, 0.4500],
    ["12 Sala", "silla", "M3 · silla 2 · pata", 4.9700, 2.0180, 5.0100, 2.0580, 0.0000, 0.4100],
    ["12 Sala", "silla", "M3 · silla 2 · pata", 5.3500, 2.0180, 5.3900, 2.0580, 0.0000, 0.4100],
    ["12 Sala", "silla", "M3 · silla 2 · pata", 4.9700, 2.3980, 5.0100, 2.4380, 0.0000, 0.4100],
    ["12 Sala", "silla", "M3 · silla 2 · pata", 5.3500, 2.3980, 5.3900, 2.4380, 0.0000, 0.4100],
    ["12 Sala", "silla", "M3 · silla 2 · respaldo", 4.9700, 2.0180, 5.3900, 2.0680, 0.4500, 0.8800],
    ["12 Sala", "mesa", "M2 · tablero", 6.1300, 2.4880, 6.8300, 3.1880, 0.7100, 0.7500],
    ["12 Sala", "silla", "M2 · pie 1", 6.4400, 2.7980, 6.5200, 2.8780, 0.0000, 0.7100],
    ["12 Sala", "silla", "M2 · base 1", 6.2800, 2.6380, 6.6800, 3.0380, 0.0000, 0.0200],
    ["12 Sala", "silla", "M2 · silla 1 · asiento", 6.2700, 3.2380, 6.6900, 3.6580, 0.4100, 0.4500],
    ["12 Sala", "silla", "M2 · silla 1 · pata", 6.2700, 3.2380, 6.3100, 3.2780, 0.0000, 0.4100],
    ["12 Sala", "silla", "M2 · silla 1 · pata", 6.6500, 3.2380, 6.6900, 3.2780, 0.0000, 0.4100],
    ["12 Sala", "silla", "M2 · silla 1 · pata", 6.2700, 3.6180, 6.3100, 3.6580, 0.0000, 0.4100],
    ["12 Sala", "silla", "M2 · silla 1 · pata", 6.6500, 3.6180, 6.6900, 3.6580, 0.0000, 0.4100],
    ["12 Sala", "silla", "M2 · silla 1 · respaldo", 6.2700, 3.6080, 6.6900, 3.6580, 0.4500, 0.8800],
    ["12 Sala", "silla", "M2 · silla 2 · asiento", 6.2700, 2.0180, 6.6900, 2.4380, 0.4100, 0.4500],
    ["12 Sala", "silla", "M2 · silla 2 · pata", 6.2700, 2.0180, 6.3100, 2.0580, 0.0000, 0.4100],
    ["12 Sala", "silla", "M2 · silla 2 · pata", 6.6500, 2.0180, 6.6900, 2.0580, 0.0000, 0.4100],
    ["12 Sala", "silla", "M2 · silla 2 · pata", 6.2700, 2.3980, 6.3100, 2.4380, 0.0000, 0.4100],
    ["12 Sala", "silla", "M2 · silla 2 · pata", 6.6500, 2.3980, 6.6900, 2.4380, 0.0000, 0.4100],
    ["12 Sala", "silla", "M2 · silla 2 · respaldo", 6.2700, 2.0180, 6.6900, 2.0680, 0.4500, 0.8800],
    ["12 Sala", "mesa", "M5 · tablero", 3.8400, 5.3300, 4.5400, 6.0300, 0.7100, 0.7500],
    ["12 Sala", "silla", "M5 · pie 1", 4.1500, 5.6400, 4.2300, 5.7200, 0.0000, 0.7100],
    ["12 Sala", "silla", "M5 · base 1", 3.9900, 5.4800, 4.3900, 5.8800, 0.0000, 0.0200],
    ["12 Sala", "silla", "M5 · silla 1 · asiento", 3.9800, 6.0800, 4.4000, 6.5000, 0.4100, 0.4500],
    ["12 Sala", "silla", "M5 · silla 1 · pata", 3.9800, 6.0800, 4.0200, 6.1200, 0.0000, 0.4100],
    ["12 Sala", "silla", "M5 · silla 1 · pata", 4.3600, 6.0800, 4.4000, 6.1200, 0.0000, 0.4100],
    ["12 Sala", "silla", "M5 · silla 1 · pata", 3.9800, 6.4600, 4.0200, 6.5000, 0.0000, 0.4100],
    ["12 Sala", "silla", "M5 · silla 1 · pata", 4.3600, 6.4600, 4.4000, 6.5000, 0.0000, 0.4100],
    ["12 Sala", "silla", "M5 · silla 1 · respaldo", 3.9800, 6.4500, 4.4000, 6.5000, 0.4500, 0.8800],
    ["12 Sala", "silla", "M5 · silla 2 · asiento", 3.9800, 4.8600, 4.4000, 5.2800, 0.4100, 0.4500],
    ["12 Sala", "silla", "M5 · silla 2 · pata", 3.9800, 4.8600, 4.0200, 4.9000, 0.0000, 0.4100],
    ["12 Sala", "silla", "M5 · silla 2 · pata", 4.3600, 4.8600, 4.4000, 4.9000, 0.0000, 0.4100],
    ["12 Sala", "silla", "M5 · silla 2 · pata", 3.9800, 5.2400, 4.0200, 5.2800, 0.0000, 0.4100],
    ["12 Sala", "silla", "M5 · silla 2 · pata", 4.3600, 5.2400, 4.4000, 5.2800, 0.0000, 0.4100],
    ["12 Sala", "silla", "M5 · silla 2 · respaldo", 3.9800, 4.8600, 4.4000, 4.9100, 0.4500, 0.8800],
    ["12 Sala", "mesa", "M4 · tablero", 4.9700, 5.3300, 5.6700, 6.0300, 0.7100, 0.7500],
    ["12 Sala", "silla", "M4 · pie 1", 5.2800, 5.6400, 5.3600, 5.7200, 0.0000, 0.7100],
    ["12 Sala", "silla", "M4 · base 1", 5.1200, 5.4800, 5.5200, 5.8800, 0.0000, 0.0200],
    ["12 Sala", "silla", "M4 · silla 1 · asiento", 5.1100, 6.0800, 5.5300, 6.5000, 0.4100, 0.4500],
    ["12 Sala", "silla", "M4 · silla 1 · pata", 5.1100, 6.0800, 5.1500, 6.1200, 0.0000, 0.4100],
    ["12 Sala", "silla", "M4 · silla 1 · pata", 5.4900, 6.0800, 5.5300, 6.1200, 0.0000, 0.4100],
    ["12 Sala", "silla", "M4 · silla 1 · pata", 5.1100, 6.4600, 5.1500, 6.5000, 0.0000, 0.4100],
    ["12 Sala", "silla", "M4 · silla 1 · pata", 5.4900, 6.4600, 5.5300, 6.5000, 0.0000, 0.4100],
    ["12 Sala", "silla", "M4 · silla 1 · respaldo", 5.1100, 6.4500, 5.5300, 6.5000, 0.4500, 0.8800],
    ["12 Sala", "silla", "M4 · silla 2 · asiento", 5.1100, 4.8600, 5.5300, 5.2800, 0.4100, 0.4500],
    ["12 Sala", "silla", "M4 · silla 2 · pata", 5.1100, 4.8600, 5.1500, 4.9000, 0.0000, 0.4100],
    ["12 Sala", "silla", "M4 · silla 2 · pata", 5.4900, 4.8600, 5.5300, 4.9000, 0.0000, 0.4100],
    ["12 Sala", "silla", "M4 · silla 2 · pata", 5.1100, 5.2400, 5.1500, 5.2800, 0.0000, 0.4100],
    ["12 Sala", "silla", "M4 · silla 2 · pata", 5.4900, 5.2400, 5.5300, 5.2800, 0.0000, 0.4100],
    ["12 Sala", "silla", "M4 · silla 2 · respaldo", 5.1100, 4.8600, 5.5300, 4.9100, 0.4500, 0.8800],
    ["12 Sala", "mesa", "M7 · tablero", 2.5500, 7.6570, 3.9500, 8.3570, 0.7100, 0.7500],
    ["12 Sala", "silla", "M7 · pie 1", 2.8600, 7.9670, 2.9400, 8.0470, 0.0000, 0.7100],
    ["12 Sala", "silla", "M7 · base 1", 2.7000, 7.8070, 3.1000, 8.2070, 0.0000, 0.0200],
    ["12 Sala", "silla", "M7 · pie 2", 3.5600, 7.9670, 3.6400, 8.0470, 0.0000, 0.7100],
    ["12 Sala", "silla", "M7 · base 2", 3.4000, 7.8070, 3.8000, 8.2070, 0.0000, 0.0200],
    ["12 Sala", "silla", "M7 · silla 1 · asiento", 2.6900, 7.1870, 3.1100, 7.6070, 0.4100, 0.4500],
    ["12 Sala", "silla", "M7 · silla 1 · pata", 2.6900, 7.1870, 2.7300, 7.2270, 0.0000, 0.4100],
    ["12 Sala", "silla", "M7 · silla 1 · pata", 3.0700, 7.1870, 3.1100, 7.2270, 0.0000, 0.4100],
    ["12 Sala", "silla", "M7 · silla 1 · pata", 2.6900, 7.5670, 2.7300, 7.6070, 0.0000, 0.4100],
    ["12 Sala", "silla", "M7 · silla 1 · pata", 3.0700, 7.5670, 3.1100, 7.6070, 0.0000, 0.4100],
    ["12 Sala", "silla", "M7 · silla 1 · respaldo", 2.6900, 7.1870, 3.1100, 7.2370, 0.4500, 0.8800],
    ["12 Sala", "silla", "M7 · silla 2 · asiento", 3.3900, 7.1870, 3.8100, 7.6070, 0.4100, 0.4500],
    ["12 Sala", "silla", "M7 · silla 2 · pata", 3.3900, 7.1870, 3.4300, 7.2270, 0.0000, 0.4100],
    ["12 Sala", "silla", "M7 · silla 2 · pata", 3.7700, 7.1870, 3.8100, 7.2270, 0.0000, 0.4100],
    ["12 Sala", "silla", "M7 · silla 2 · pata", 3.3900, 7.5670, 3.4300, 7.6070, 0.0000, 0.4100],
    ["12 Sala", "silla", "M7 · silla 2 · pata", 3.7700, 7.5670, 3.8100, 7.6070, 0.0000, 0.4100],
    ["12 Sala", "silla", "M7 · silla 2 · respaldo", 3.3900, 7.1870, 3.8100, 7.2370, 0.4500, 0.8800],
    ["12 Sala", "mesa", "M10 · tablero", 4.6150, 7.6570, 5.3150, 8.3570, 0.7100, 0.7500],
    ["12 Sala", "silla", "M10 · pie 1", 4.9250, 7.9670, 5.0050, 8.0470, 0.0000, 0.7100],
    ["12 Sala", "silla", "M10 · base 1", 4.7650, 7.8070, 5.1650, 8.2070, 0.0000, 0.0200],
    ["12 Sala", "silla", "M10 · silla 1 · asiento", 4.7550, 7.1870, 5.1750, 7.6070, 0.4100, 0.4500],
    ["12 Sala", "silla", "M10 · silla 1 · pata", 4.7550, 7.1870, 4.7950, 7.2270, 0.0000, 0.4100],
    ["12 Sala", "silla", "M10 · silla 1 · pata", 5.1350, 7.1870, 5.1750, 7.2270, 0.0000, 0.4100],
    ["12 Sala", "silla", "M10 · silla 1 · pata", 4.7550, 7.5670, 4.7950, 7.6070, 0.0000, 0.4100],
    ["12 Sala", "silla", "M10 · silla 1 · pata", 5.1350, 7.5670, 5.1750, 7.6070, 0.0000, 0.4100],
    ["12 Sala", "silla", "M10 · silla 1 · respaldo", 4.7550, 7.1870, 5.1750, 7.2370, 0.4500, 0.8800],
    ["12 Sala", "mesa", "M11 · tablero", 5.9800, 7.6570, 7.3800, 8.3570, 0.7100, 0.7500],
    ["12 Sala", "silla", "M11 · pie 1", 6.2900, 7.9670, 6.3700, 8.0470, 0.0000, 0.7100],
    ["12 Sala", "silla", "M11 · base 1", 6.1300, 7.8070, 6.5300, 8.2070, 0.0000, 0.0200],
    ["12 Sala", "silla", "M11 · pie 2", 6.9900, 7.9670, 7.0700, 8.0470, 0.0000, 0.7100],
    ["12 Sala", "silla", "M11 · base 2", 6.8300, 7.8070, 7.2300, 8.2070, 0.0000, 0.0200],
    ["12 Sala", "silla", "M11 · silla 1 · asiento", 6.1200, 7.1870, 6.5400, 7.6070, 0.4100, 0.4500],
    ["12 Sala", "silla", "M11 · silla 1 · pata", 6.1200, 7.1870, 6.1600, 7.2270, 0.0000, 0.4100],
    ["12 Sala", "silla", "M11 · silla 1 · pata", 6.5000, 7.1870, 6.5400, 7.2270, 0.0000, 0.4100],
    ["12 Sala", "silla", "M11 · silla 1 · pata", 6.1200, 7.5670, 6.1600, 7.6070, 0.0000, 0.4100],
    ["12 Sala", "silla", "M11 · silla 1 · pata", 6.5000, 7.5670, 6.5400, 7.6070, 0.0000, 0.4100],
    ["12 Sala", "silla", "M11 · silla 1 · respaldo", 6.1200, 7.1870, 6.5400, 7.2370, 0.4500, 0.8800],
    ["12 Sala", "silla", "M11 · silla 2 · asiento", 6.8200, 7.1870, 7.2400, 7.6070, 0.4100, 0.4500],
    ["12 Sala", "silla", "M11 · silla 2 · pata", 6.8200, 7.1870, 6.8600, 7.2270, 0.0000, 0.4100],
    ["12 Sala", "silla", "M11 · silla 2 · pata", 7.2000, 7.1870, 7.2400, 7.2270, 0.0000, 0.4100],
    ["12 Sala", "silla", "M11 · silla 2 · pata", 6.8200, 7.5670, 6.8600, 7.6070, 0.0000, 0.4100],
    ["12 Sala", "silla", "M11 · silla 2 · pata", 7.2000, 7.5670, 7.2400, 7.6070, 0.0000, 0.4100],
    ["12 Sala", "silla", "M11 · silla 2 · respaldo", 6.8200, 7.1870, 7.2400, 7.2370, 0.4500, 0.8800],
    ["12 Sala", "sillon", "Sillón corrido · asiento", 2.5300, 8.3570, 7.4000, 8.9570, 0.0000, 0.4200],
    ["12 Sala", "sillon", "Sillón corrido · respaldo", 2.5300, 8.8570, 7.4000, 8.9570, 0.4200, 1.0500],
    ["13 Instalaciones", "luz", "Aplique 1", 0.2500, 5.6500, 0.3700, 5.8500, 1.9500, 2.2500],
    ["13 Instalaciones", "luz", "Aplique 2", 0.2500, 6.3500, 0.3700, 6.5500, 1.9500, 2.2500],
    ["13 Instalaciones", "aire", "AC1 · cuerpo de la máquina (empotrado en el forjado)", 4.6300, 4.7830, 5.5100, 5.6630, 2.3100, 2.5600],
    ["13 Instalaciones", "aire", "AC1 · Cassette de 4 vías empotrado, al Oeste de P3 · panel de 4 vías", 4.5950, 4.7480, 5.5450, 5.6980, 2.2800, 2.3100],
    ["13 Instalaciones", "rejilla", "AC1 · rejilla de retorno central", 4.8450, 4.9980, 5.2950, 5.4480, 2.2650, 2.2800],
    ["13 Instalaciones", "rejilla", "AC1 · lama de impulsión Sur", 4.7200, 4.7830, 5.4200, 4.8730, 2.2650, 2.2800],
    ["13 Instalaciones", "rejilla", "AC1 · lama de impulsión Norte", 4.7200, 5.5730, 5.4200, 5.6630, 2.2650, 2.2800],
    ["13 Instalaciones", "rejilla", "AC1 · lama de impulsión Oeste", 4.6300, 4.8730, 4.7200, 5.5730, 2.2650, 2.2800],
    ["13 Instalaciones", "rejilla", "AC1 · lama de impulsión Este", 5.4200, 4.8730, 5.5100, 5.5730, 2.2650, 2.2800],
    ["14 Planta alta", "tabique", "Tabique Oeste del aseo", 2.4610, 7.5090, 2.5600, 8.9570, 2.5600, 5.0600],
    ["14 Planta alta", "tabique", "Tabique Sur - tramo Oeste", 2.5600, 7.5090, 3.0890, 7.6070, 2.5600, 5.0600],
    ["14 Planta alta", "tabique", "Tabique Sur - tramo Este", 3.8490, 7.5090, 7.5110, 7.6070, 2.5600, 5.0600],
    ["14 Planta alta", "tabique", "Tabique del inodoro", 4.4610, 7.6070, 4.5600, 8.2080, 2.5600, 5.0600],
    ["14 Planta alta", "tabique", "Tabique aseo / almacen", 5.4590, 7.6070, 5.5580, 8.9570, 2.5600, 5.0600],
    ["14 Planta alta", "tabique", "Tabique Este del almacen", 7.4080, 7.6070, 7.5110, 8.0720, 2.5600, 5.0600],
    ["14 Planta alta", "tabique", "Puerta aseo · dintel", 3.0890, 7.5090, 3.8490, 7.6070, 4.6600, 5.0600],
    ["14 Planta alta", "madera", "Puerta aseo · hoja", 3.0890, 7.5290, 3.8490, 7.5690, 2.5600, 4.6600],
    ["14 Planta alta", "tabique", "Puerta inodoro · dintel", 4.4610, 8.2080, 4.5600, 8.9570, 4.6600, 5.0600],
    ["14 Planta alta", "madera", "Puerta inodoro · hoja", 4.4810, 8.2080, 4.5210, 8.9570, 2.5600, 4.6600],
    ["14 Planta alta", "tabique", "Puerta almacen · dintel", 7.4080, 8.0720, 7.5110, 8.9570, 4.6600, 5.0600],
    ["14 Planta alta", "madera", "Puerta almacen · hoja", 7.4280, 8.0720, 7.4680, 8.9570, 2.5600, 4.6600],
    ["14 Planta alta", "vidrio", "Borde Oeste del vacio", 2.4110, 3.9880, 2.4610, 7.5090, 2.5600, 3.5600],
    ["14 Planta alta", "vidrio", "Borde Sur del vacio", 2.4110, 3.9390, 8.7590, 3.9880, 2.5600, 3.5600],
    ["14 Planta alta", "vidrio", "Caja de escalera", 8.7590, 3.9390, 8.8110, 7.7380, 2.5600, 3.5600],
    ["14 Planta alta", "mesa", "C1 · tablero", 3.3500, 4.1000, 4.3500, 6.5000, 3.2700, 3.3100],
    ["14 Planta alta", "silla", "C1 · pie 1", 3.8100, 5.2600, 3.8900, 5.3400, 2.5600, 3.2700],
    ["14 Planta alta", "silla", "C1 · base 1", 3.6500, 5.1000, 4.0500, 5.5000, 2.5600, 2.5800],
    ["14 Planta alta", "silla", "C1 · silla 1 · asiento", 4.4000, 4.1900, 4.8200, 4.6100, 2.9700, 3.0100],
    ["14 Planta alta", "silla", "C1 · silla 1 · pata", 4.4000, 4.1900, 4.4400, 4.2300, 2.5600, 2.9700],
    ["14 Planta alta", "silla", "C1 · silla 1 · pata", 4.7800, 4.1900, 4.8200, 4.2300, 2.5600, 2.9700],
    ["14 Planta alta", "silla", "C1 · silla 1 · pata", 4.4000, 4.5700, 4.4400, 4.6100, 2.5600, 2.9700],
    ["14 Planta alta", "silla", "C1 · silla 1 · pata", 4.7800, 4.5700, 4.8200, 4.6100, 2.5600, 2.9700],
    ["14 Planta alta", "silla", "C1 · silla 1 · respaldo", 4.4000, 4.1900, 4.8200, 4.2400, 3.0100, 3.4400],
    ["14 Planta alta", "silla", "C1 · silla 2 · asiento", 4.4000, 4.7900, 4.8200, 5.2100, 2.9700, 3.0100],
    ["14 Planta alta", "silla", "C1 · silla 2 · pata", 4.4000, 4.7900, 4.4400, 4.8300, 2.5600, 2.9700],
    ["14 Planta alta", "silla", "C1 · silla 2 · pata", 4.7800, 4.7900, 4.8200, 4.8300, 2.5600, 2.9700],
    ["14 Planta alta", "silla", "C1 · silla 2 · pata", 4.4000, 5.1700, 4.4400, 5.2100, 2.5600, 2.9700],
    ["14 Planta alta", "silla", "C1 · silla 2 · pata", 4.7800, 5.1700, 4.8200, 5.2100, 2.5600, 2.9700],
    ["14 Planta alta", "silla", "C1 · silla 2 · respaldo", 4.7700, 4.7900, 4.8200, 5.2100, 3.0100, 3.4400],
    ["14 Planta alta", "silla", "C1 · silla 3 · asiento", 4.4000, 5.3900, 4.8200, 5.8100, 2.9700, 3.0100],
    ["14 Planta alta", "silla", "C1 · silla 3 · pata", 4.4000, 5.3900, 4.4400, 5.4300, 2.5600, 2.9700],
    ["14 Planta alta", "silla", "C1 · silla 3 · pata", 4.7800, 5.3900, 4.8200, 5.4300, 2.5600, 2.9700],
    ["14 Planta alta", "silla", "C1 · silla 3 · pata", 4.4000, 5.7700, 4.4400, 5.8100, 2.5600, 2.9700],
    ["14 Planta alta", "silla", "C1 · silla 3 · pata", 4.7800, 5.7700, 4.8200, 5.8100, 2.5600, 2.9700],
    ["14 Planta alta", "silla", "C1 · silla 3 · respaldo", 4.7700, 5.3900, 4.8200, 5.8100, 3.0100, 3.4400],
    ["14 Planta alta", "silla", "C1 · silla 4 · asiento", 4.4000, 5.9900, 4.8200, 6.4100, 2.9700, 3.0100],
    ["14 Planta alta", "silla", "C1 · silla 4 · pata", 4.4000, 5.9900, 4.4400, 6.0300, 2.5600, 2.9700],
    ["14 Planta alta", "silla", "C1 · silla 4 · pata", 4.7800, 5.9900, 4.8200, 6.0300, 2.5600, 2.9700],
    ["14 Planta alta", "silla", "C1 · silla 4 · pata", 4.4000, 6.3700, 4.4400, 6.4100, 2.5600, 2.9700],
    ["14 Planta alta", "silla", "C1 · silla 4 · pata", 4.7800, 6.3700, 4.8200, 6.4100, 2.5600, 2.9700],
    ["14 Planta alta", "silla", "C1 · silla 4 · respaldo", 4.4000, 6.3600, 4.8200, 6.4100, 3.0100, 3.4400],
    ["14 Planta alta", "silla", "C1 · silla 5 · asiento", 2.8800, 4.1900, 3.3000, 4.6100, 2.9700, 3.0100],
    ["14 Planta alta", "silla", "C1 · silla 5 · pata", 2.8800, 4.1900, 2.9200, 4.2300, 2.5600, 2.9700],
    ["14 Planta alta", "silla", "C1 · silla 5 · pata", 3.2600, 4.1900, 3.3000, 4.2300, 2.5600, 2.9700],
    ["14 Planta alta", "silla", "C1 · silla 5 · pata", 2.8800, 4.5700, 2.9200, 4.6100, 2.5600, 2.9700],
    ["14 Planta alta", "silla", "C1 · silla 5 · pata", 3.2600, 4.5700, 3.3000, 4.6100, 2.5600, 2.9700],
    ["14 Planta alta", "silla", "C1 · silla 5 · respaldo", 2.8800, 4.1900, 3.3000, 4.2400, 3.0100, 3.4400],
    ["14 Planta alta", "silla", "C1 · silla 6 · asiento", 2.8800, 4.7900, 3.3000, 5.2100, 2.9700, 3.0100],
    ["14 Planta alta", "silla", "C1 · silla 6 · pata", 2.8800, 4.7900, 2.9200, 4.8300, 2.5600, 2.9700],
    ["14 Planta alta", "silla", "C1 · silla 6 · pata", 3.2600, 4.7900, 3.3000, 4.8300, 2.5600, 2.9700],
    ["14 Planta alta", "silla", "C1 · silla 6 · pata", 2.8800, 5.1700, 2.9200, 5.2100, 2.5600, 2.9700],
    ["14 Planta alta", "silla", "C1 · silla 6 · pata", 3.2600, 5.1700, 3.3000, 5.2100, 2.5600, 2.9700],
    ["14 Planta alta", "silla", "C1 · silla 6 · respaldo", 2.8800, 4.7900, 2.9300, 5.2100, 3.0100, 3.4400],
    ["14 Planta alta", "silla", "C1 · silla 7 · asiento", 2.8800, 5.3900, 3.3000, 5.8100, 2.9700, 3.0100],
    ["14 Planta alta", "silla", "C1 · silla 7 · pata", 2.8800, 5.3900, 2.9200, 5.4300, 2.5600, 2.9700],
    ["14 Planta alta", "silla", "C1 · silla 7 · pata", 3.2600, 5.3900, 3.3000, 5.4300, 2.5600, 2.9700],
    ["14 Planta alta", "silla", "C1 · silla 7 · pata", 2.8800, 5.7700, 2.9200, 5.8100, 2.5600, 2.9700],
    ["14 Planta alta", "silla", "C1 · silla 7 · pata", 3.2600, 5.7700, 3.3000, 5.8100, 2.5600, 2.9700],
    ["14 Planta alta", "silla", "C1 · silla 7 · respaldo", 2.8800, 5.3900, 2.9300, 5.8100, 3.0100, 3.4400],
    ["14 Planta alta", "silla", "C1 · silla 8 · asiento", 2.8800, 5.9900, 3.3000, 6.4100, 2.9700, 3.0100],
    ["14 Planta alta", "silla", "C1 · silla 8 · pata", 2.8800, 5.9900, 2.9200, 6.0300, 2.5600, 2.9700],
    ["14 Planta alta", "silla", "C1 · silla 8 · pata", 3.2600, 5.9900, 3.3000, 6.0300, 2.5600, 2.9700],
    ["14 Planta alta", "silla", "C1 · silla 8 · pata", 2.8800, 6.3700, 2.9200, 6.4100, 2.5600, 2.9700],
    ["14 Planta alta", "silla", "C1 · silla 8 · pata", 3.2600, 6.3700, 3.3000, 6.4100, 2.5600, 2.9700],
    ["14 Planta alta", "silla", "C1 · silla 8 · respaldo", 2.8800, 6.3600, 3.3000, 6.4100, 3.0100, 3.4400],
    ["14 Planta alta", "silla", "R1 · silla 1 · asiento", 7.3300, 6.0800, 7.7500, 6.5000, 2.9700, 3.0100],
    ["14 Planta alta", "silla", "R1 · silla 1 · pata", 7.3300, 6.0800, 7.3700, 6.1200, 2.5600, 2.9700],
    ["14 Planta alta", "silla", "R1 · silla 1 · pata", 7.7100, 6.0800, 7.7500, 6.1200, 2.5600, 2.9700],
    ["14 Planta alta", "silla", "R1 · silla 1 · pata", 7.3300, 6.4600, 7.3700, 6.5000, 2.5600, 2.9700],
    ["14 Planta alta", "silla", "R1 · silla 1 · pata", 7.7100, 6.4600, 7.7500, 6.5000, 2.5600, 2.9700],
    ["14 Planta alta", "silla", "R1 · silla 1 · respaldo", 7.3300, 6.4500, 7.7500, 6.5000, 3.0100, 3.4400],
    ["14 Planta alta", "silla", "R1 · silla 2 · asiento", 7.3300, 4.3600, 7.7500, 4.7800, 2.9700, 3.0100],
    ["14 Planta alta", "silla", "R1 · silla 2 · pata", 7.3300, 4.3600, 7.3700, 4.4000, 2.5600, 2.9700],
    ["14 Planta alta", "silla", "R1 · silla 2 · pata", 7.7100, 4.3600, 7.7500, 4.4000, 2.5600, 2.9700],
    ["14 Planta alta", "silla", "R1 · silla 2 · pata", 7.3300, 4.7400, 7.3700, 4.7800, 2.5600, 2.9700],
    ["14 Planta alta", "silla", "R1 · silla 2 · pata", 7.7100, 4.7400, 7.7500, 4.7800, 2.5600, 2.9700],
    ["14 Planta alta", "silla", "R1 · silla 2 · respaldo", 7.3300, 4.3600, 7.7500, 4.4100, 3.0100, 3.4400],
    ["14 Planta alta", "silla", "R1 · silla 3 · asiento", 8.0748, 5.6500, 8.4948, 6.0700, 2.9700, 3.0100],
    ["14 Planta alta", "silla", "R1 · silla 3 · pata", 8.0748, 5.6500, 8.1148, 5.6900, 2.5600, 2.9700],
    ["14 Planta alta", "silla", "R1 · silla 3 · pata", 8.4548, 5.6500, 8.4948, 5.6900, 2.5600, 2.9700],
    ["14 Planta alta", "silla", "R1 · silla 3 · pata", 8.0748, 6.0300, 8.1148, 6.0700, 2.5600, 2.9700],
    ["14 Planta alta", "silla", "R1 · silla 3 · pata", 8.4548, 6.0300, 8.4948, 6.0700, 2.5600, 2.9700],
    ["14 Planta alta", "silla", "R1 · silla 3 · respaldo", 8.4448, 5.6500, 8.4948, 6.0700, 3.0100, 3.4400],
    ["14 Planta alta", "silla", "R1 · silla 4 · asiento", 6.5852, 5.6500, 7.0052, 6.0700, 2.9700, 3.0100],
    ["14 Planta alta", "silla", "R1 · silla 4 · pata", 6.5852, 5.6500, 6.6252, 5.6900, 2.5600, 2.9700],
    ["14 Planta alta", "silla", "R1 · silla 4 · pata", 6.9652, 5.6500, 7.0052, 5.6900, 2.5600, 2.9700],
    ["14 Planta alta", "silla", "R1 · silla 4 · pata", 6.5852, 6.0300, 6.6252, 6.0700, 2.5600, 2.9700],
    ["14 Planta alta", "silla", "R1 · silla 4 · pata", 6.9652, 6.0300, 7.0052, 6.0700, 2.5600, 2.9700],
    ["14 Planta alta", "silla", "R1 · silla 4 · respaldo", 6.5852, 5.6500, 6.6352, 6.0700, 3.0100, 3.4400],
    ["14 Planta alta", "silla", "R1 · silla 5 · asiento", 6.5852, 4.7900, 7.0052, 5.2100, 2.9700, 3.0100],
    ["14 Planta alta", "silla", "R1 · silla 5 · pata", 6.5852, 4.7900, 6.6252, 4.8300, 2.5600, 2.9700],
    ["14 Planta alta", "silla", "R1 · silla 5 · pata", 6.9652, 4.7900, 7.0052, 4.8300, 2.5600, 2.9700],
    ["14 Planta alta", "silla", "R1 · silla 5 · pata", 6.5852, 5.1700, 6.6252, 5.2100, 2.5600, 2.9700],
    ["14 Planta alta", "silla", "R1 · silla 5 · pata", 6.9652, 5.1700, 7.0052, 5.2100, 2.5600, 2.9700],
    ["14 Planta alta", "silla", "R1 · silla 5 · respaldo", 6.5852, 4.7900, 6.6352, 5.2100, 3.0100, 3.4400],
    ["14 Planta alta", "silla", "R1 · silla 6 · asiento", 8.0748, 4.7900, 8.4948, 5.2100, 2.9700, 3.0100],
    ["14 Planta alta", "silla", "R1 · silla 6 · pata", 8.0748, 4.7900, 8.1148, 4.8300, 2.5600, 2.9700],
    ["14 Planta alta", "silla", "R1 · silla 6 · pata", 8.4548, 4.7900, 8.4948, 4.8300, 2.5600, 2.9700],
    ["14 Planta alta", "silla", "R1 · silla 6 · pata", 8.0748, 5.1700, 8.1148, 5.2100, 2.5600, 2.9700],
    ["14 Planta alta", "silla", "R1 · silla 6 · pata", 8.4548, 5.1700, 8.4948, 5.2100, 2.5600, 2.9700],
    ["14 Planta alta", "silla", "R1 · silla 6 · respaldo", 8.4448, 4.7900, 8.4948, 5.2100, 3.0100, 3.4400],
  ]

  # --- prismas: [capa, material, nombre, [[x, y], ...], z0, z1]
  PRISMAS = [
    ["01 Solera", "solera", "Solera de planta baja", [[0.2500, 9.0080], [2.4300, 9.0080], [2.4300, 8.9570], [9.8900, 8.9570], [9.8900, 1.4290], [9.7100, 1.4290], [9.7100, 0.3790], [6.2300, 0.3790], [6.2300, 0.9600], [5.9800, 0.9600], [5.9800, 1.6210], [0.5100, 1.6210], [0.5100, 2.0090], [0.2500, 2.0090]], -0.1500, 0.0000],
    ["09 Forjado", "forjado", "Forjado de planta alta", [[2.4610, 8.9570], [9.8900, 8.9570], [9.8900, 7.7380], [8.8110, 7.7380], [8.8110, 3.9390], [2.4110, 3.9390], [2.4110, 7.5090], [2.4610, 7.5090]], 2.3100, 2.5600],
    ["15 Techo", "forjado", "Techo del altillo", [[0.0000, 9.1560], [10.0400, 9.1560], [10.0400, 0.3300], [6.2300, 0.3300], [6.2300, 0.0000], [5.7310, 0.0000], [5.7310, 1.5610], [0.0000, 1.5610]], 5.0600, 5.2600],
  ]

  # --- paneles: [capa, material, nombre, [[y, z], ...], x0, x1]
  PANELES = [
    ["08 Escalera", "tabique", "Caja de escalera (planta baja)", [[3.9390, 0.0000], [7.7380, 0.0000], [7.7380, 2.3100], [5.8400, 2.3100], [3.9390, 1.2090]], 8.6500, 8.8110],
  ]

  # --- cilindros: [capa, material, nombre, cx, cy, r, z0, z1]
  CILINDROS = [
    ["11 Barra", "inox", "B2 · Barriles de cerveza de 30 L, Ø 0,32 (debajo de la tabla de P2)", 0.9100, 1.8160, 0.1600, 0.1300, 0.7300],
    ["13 Instalaciones", "luz", "Empotrado 1", 1.1000, 4.6000, 0.0450, 2.2900, 2.3100],
    ["13 Instalaciones", "luz", "Empotrado 2", 2.6000, 4.6000, 0.0450, 2.2900, 2.3100],
    ["13 Instalaciones", "luz", "Empotrado 3", 4.1000, 4.6000, 0.0450, 2.2900, 2.3100],
    ["13 Instalaciones", "luz", "Empotrado 4", 1.1000, 5.9000, 0.0450, 2.2900, 2.3100],
    ["13 Instalaciones", "luz", "Empotrado 5", 2.6000, 5.9000, 0.0450, 2.2900, 2.3100],
    ["13 Instalaciones", "luz", "Empotrado 6", 4.1000, 5.9000, 0.0450, 2.2900, 2.3100],
    ["13 Instalaciones", "luz", "Empotrado 7", 1.1000, 7.2000, 0.0450, 2.2900, 2.3100],
    ["13 Instalaciones", "luz", "Empotrado 8", 2.6000, 7.2000, 0.0450, 2.2900, 2.3100],
    ["13 Instalaciones", "luz", "Empotrado 9", 4.1000, 7.2000, 0.0450, 2.2900, 2.3100],
    ["13 Instalaciones", "luz", "Empotrado 10", 1.1000, 8.5000, 0.0450, 2.2900, 2.3100],
    ["13 Instalaciones", "luz", "Empotrado 11", 2.6000, 8.5000, 0.0450, 2.2900, 2.3100],
    ["13 Instalaciones", "luz", "Empotrado 12", 4.1000, 8.5000, 0.0450, 2.2900, 2.3100],
    ["13 Instalaciones", "luz", "Empotrado 13", 8.6000, 8.5000, 0.0450, 2.2900, 2.3100],
    ["13 Instalaciones", "luz", "Colgante 1", 2.0400, 2.2800, 0.1300, 1.7000, 1.9200],
    ["13 Instalaciones", "luz", "Colgante 2", 2.0400, 3.5800, 0.1300, 1.7000, 1.9200],
    ["13 Instalaciones", "luz", "Colgante 3", 4.6000, 3.2000, 0.1300, 1.7000, 1.9200],
    ["13 Instalaciones", "luz", "Colgante 4", 7.6000, 3.2000, 0.1300, 1.7000, 1.9200],
    ["13 Instalaciones", "luz", "Colgante 5", 7.3000, 0.9500, 0.1300, 1.7000, 1.9200],
    ["13 Instalaciones", "luz", "Colgante 6", 8.9000, 0.9500, 0.1300, 1.7000, 1.9200],
    ["14 Planta alta", "mesa", "R1 · tablero", 7.5400, 5.4300, 0.6000, 3.2700, 3.3100],
    ["14 Planta alta", "silla", "R1 · pie", 7.5400, 5.4300, 0.0600, 2.5600, 3.2700],
    ["14 Planta alta", "silla", "R1 · base", 7.5400, 5.4300, 0.2200, 2.5600, 2.5800],
  ]


  # ------------------------------------------------------------- utilidades
  def self.material(model, clave)
    @mats ||= {}
    return @mats[clave] if @mats[clave]
    fila = MATERIALES.find { |f| f[0] == clave }
    return nil unless fila
    nombre = fila[1]
    mat = model.materials[nombre] || model.materials.add(nombre)
    mat.color = Sketchup::Color.new(fila[2], fila[3], fila[4])
    @mats[clave] = mat
  end

  def self.capa(model, nombre)
    @capas ||= {}
    @capas[nombre] ||= (model.layers[nombre] || model.layers.add(nombre))
  end

  # Extruye una cara horizontal creada en z0 hasta z1. El sentido de giro NO
  # esta garantizado: las cajas vienen en antihorario pero los tres prismas
  # vienen en horario visto desde arriba. Por eso se fuerza la normal a +Z
  # antes del pushpull, y esa comprobacion NO se puede quitar.
  def self.extruir(grupo, puntos_xy, z0, z1)
    pts = puntos_xy.map { |x, y| Geom::Point3d.new(x.m, y.m, z0.m) }
    begin
      cara = grupo.entities.add_face(pts)
    rescue ArgumentError
      cara = nil
    end
    return nil if cara.nil?
    cara.reverse! if cara.normal.z < 0
    cara.pushpull((z1 - z0).m)
    cara
  end

  def self.poner(grupo, model, capa_nombre, mat_clave, nombre)
    grupo.name = nombre
    grupo.layer = capa(model, capa_nombre)
    m = material(model, mat_clave)
    grupo.material = m if m
    grupo
  end

  # Si la cara no se puede crear, se borra el grupo vacio y se avisa, en vez
  # de dejar un grupo con nombre y sin geometria que ademas contaria como
  # solido construido.
  def self.fallo(grupo, nombre)
    grupo.erase! if grupo && grupo.valid?
    @fallos << nombre
    puts "AVISO: no se pudo crear #{nombre}"
    nil
  end

  def self.caja(model, ents, capa_nombre, mat_clave, nombre, x0, y0, x1, y1, z0, z1)
    g = ents.add_group
    return fallo(g, nombre) if extruir(g, [[x0, y0], [x1, y0], [x1, y1], [x0, y1]], z0, z1).nil?
    poner(g, model, capa_nombre, mat_clave, nombre)
  end

  # Muro de canto variable: la cara se dibuja en el plano Y-Z y se extruye
  # en X. Sirve para la pared de la escalera, cuya coronacion sube con ella.
  def self.extruir_x(grupo, puntos_yz, x0, x1)
    pts = puntos_yz.map { |y, z| Geom::Point3d.new(x0.m, y.m, z.m) }
    begin
      cara = grupo.entities.add_face(pts)
    rescue ArgumentError
      cara = nil
    end
    return nil if cara.nil?
    cara.reverse! if cara.normal.x < 0
    cara.pushpull((x1 - x0).m)
    cara
  end

  def self.panel(model, ents, capa_nombre, mat_clave, nombre, pts, x0, x1)
    g = ents.add_group
    return fallo(g, nombre) if extruir_x(g, pts, x0, x1).nil?
    poner(g, model, capa_nombre, mat_clave, nombre)
  end

  def self.prisma(model, ents, capa_nombre, mat_clave, nombre, pts, z0, z1)
    g = ents.add_group
    return fallo(g, nombre) if extruir(g, pts, z0, z1).nil?
    poner(g, model, capa_nombre, mat_clave, nombre)
  end

  # add_circle deja un poligono INSCRITO: los vertices caen en el radio pedido
  # y las caras quedan por dentro. Con 32 segmentos eso son casi 3 mm de menos
  # en un tablero de 1,20. Aqui el numero de lados se ajusta al radio (lado de
  # ~15 mm, entre 24 y 128) y el radio se corrige para que el poligono tenga la
  # misma AREA que el circulo: el error baja a decimas de milimetro.
  LADO_ARCO = 0.015
  SEGMENTOS_MIN = 32
  SEGMENTOS_MAX = 128

  def self.segmentos(r)
    n = (2 * Math::PI * r / LADO_ARCO).round
    [[n, SEGMENTOS_MIN].max, SEGMENTOS_MAX].min
  end

  def self.radio_equivalente(r, n)
    t = 2 * Math::PI / n
    r * Math.sqrt(t / Math.sin(t))
  end

  def self.cilindro(model, ents, capa_nombre, mat_clave, nombre, cx, cy, r, z0, z1)
    g = ents.add_group
    n = segmentos(r)
    centro = Geom::Point3d.new(cx.m, cy.m, z0.m)
    aristas = g.entities.add_circle(centro, Geom::Vector3d.new(0, 0, 1),
                                    radio_equivalente(r, n).m, n)
    cara = aristas ? g.entities.add_face(aristas) : nil
    return fallo(g, nombre) if cara.nil?
    cara.reverse! if cara.normal.z < 0
    cara.pushpull((z1 - z0).m)
    poner(g, model, capa_nombre, mat_clave, nombre)
  end

  # --------------------------------------------------------------- limpieza
  # Borra TODOS los grupos raiz con este nombre, no solo el primero: si el
  # usuario copio el grupo o deshizo a medias puede haber mas de uno.
  def self.borrar_raices(model)
    model.entities.grep(Sketchup::Group)
         .select { |g| g.name == NOMBRE_MODELO }
         .each { |g| g.erase! if g.valid? }
  end

  def self.clear
    model = Sketchup.active_model
    model.start_operation("Borrar #{NOMBRE_MODELO}", true)
    borrar_raices(model)
    model.commit_operation
    @mats = {}
    @capas = {}
    model.active_view.invalidate
    "borrado"
  end

  # ---------------------------------------------------------------- montaje
  def self.build
    model = Sketchup.active_model
    @mats = {}
    @capas = {}

    # metros como unidad de trabajo del modelo
    begin
      # El ORDEN importa: con formato arquitectonico o fraccionario SketchUp
      # fuerza pulgadas, asi que hay que poner el formato decimal ANTES de
      # pedir metros. Al reves, el modelo se acota en pulgadas.
      model.options["UnitsOptions"]["LengthFormat"] = 0    # decimal
      model.options["UnitsOptions"]["LengthUnit"] = 4      # 4 = metros
      model.options["UnitsOptions"]["LengthPrecision"] = 3 # milimetro
    rescue StandardError
      # si la version no acepta estas opciones, seguimos: la geometria no cambia
    end

    n = 0
    abiertos = 0
    @fallos = []
    model.start_operation("Construir #{NOMBRE_MODELO}", true)
    begin
      borrar_raices(model)

      CAPAS.each { |c| capa(model, c) }

      raiz = model.entities.add_group
      raiz.name = NOMBRE_MODELO
      ents = raiz.entities

      CAJAS.each do |f|
        n += 1 if caja(model, ents, f[0], f[1], f[2], f[3], f[4], f[5], f[6], f[7], f[8])
      end
      PRISMAS.each do |f|
        n += 1 if prisma(model, ents, f[0], f[1], f[2], f[3], f[4], f[5])
      end
      CILINDROS.each do |f|
        n += 1 if cilindro(model, ents, f[0], f[1], f[2], f[3], f[4], f[5], f[6], f[7])
      end
      PANELES.each do |f|
        n += 1 if panel(model, ents, f[0], f[1], f[2], f[3], f[4], f[5])
      end

      CAPAS_OCULTAS.each do |c|
        l = model.layers[c]
        l.visible = false if l
      end

      # control de calidad: cada pieza tiene que ser un solido cerrado
      abiertos = ents.grep(Sketchup::Group).reject { |g| g.manifold? }.size

      model.commit_operation
    rescue StandardError => e
      model.abort_operation
      puts "ERROR al construir: #{e.message}"
      puts(e.backtrace ? e.backtrace.first(8) : "(sin backtrace)")
      raise
    end

    # todo lo que va despues del commit, fuera del bloque protegido: si algo
    # falla aqui no se puede abortar una operacion que ya esta confirmada.
    model.active_view.zoom_extents
    total = CAJAS.length + PRISMAS.length + CILINDROS.length + PANELES.length
    puts "#{NOMBRE_MODELO}: #{n} de #{total} solidos en #{CAPAS.length} capas."
    puts "AVISO: #{@fallos.length} piezas sin crear -> #{@fallos.join(', ')}" unless @fallos.empty?
    puts "AVISO: #{abiertos} piezas no son solido cerrado." if abiertos > 0
    n
  end

end

Local3D.build if defined?(Sketchup)
