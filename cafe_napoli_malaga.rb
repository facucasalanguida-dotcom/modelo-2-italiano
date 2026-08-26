# encoding: UTF-8
#
# ============================================================================
#  CAFÉ NAPOLI — MÁLAGA
#  Modelo 3D completo para SketchUp  ·  planta baja + planta alta
# ============================================================================
#
#  Caja arquitectónica (solera, muros, pilares, machones, forjado, viga,
#  particiones, escalera, barandillas, escaparate y bajante) MÁS el
#  interiorismo: pavimento, cocina con campana y revestimiento de inox,
#  mampara de vidrio, barra, vitrinas, estantería de hornacinas,
#  revestimientos de listones, mesas, sillas, iluminación y decoración.
#
#  EL CUELLO DE FACHADA (LA ENTRADA) SE DEJA VACÍO a propósito: sólo tiene
#  dos colgantes altos. No hay mesas, ni banco, ni plantas al sur de la
#  línea del muro sur (y = 1,810 m).
#
#  USO
#  ---
#  1) SketchUp, modelo nuevo y vacío.
#  2) Ventana > Consola Ruby  (Window > Ruby Console)
#  3) load "C:/ruta/al/cafe_napoli_malaga.rb"
#     Para regenerar:  CafeNapoliMalaga.build!
#  También instala el menú  Extensiones > Café Napoli > Generar modelo 3D.
#
#  ORIGEN DE LAS MEDIDAS
#  ---------------------
#  Cada coordenada del archivo es una medida tomada sobre los vectores de los
#  PDF entregados. No hay ninguna cota inventada.
#
#    planimetria_2.pdf   (PLANTA ALTA + perímetro)  escala 1:50 -> 56,6929 pt/m
#    PROPOSTA_MALAGA.pdf (PLANTA BAJA)              escala 1:30 -> 94,4882 pt/m
#
#  Escalas validadas contra las cotas rotuladas del propio plano:
#    ASEO 3,92 m² (rotulado 3,90) · ALMACÉN-2 2,59 m² (rotulado 2,60)
#    Huella de peldaño 0,260 m · 17 tabicas de 3,00/17 = 0,1765 m
#    Trasbarra «272» = 2,721 m · «188» = 1,880 m · «134,5» = 1,345 m
#
#  Los dos planos encajan al milímetro en los elementos que comparten
#  (pilastra sur, machón oeste, cara interior del muro sur): desviación
#  máxima 1,5 mm.
#
#  SISTEMA DE COORDENADAS (metros)
#  -------------------------------
#    X = 0  cara exterior del muro OESTE       X = 10,040  medianera ESTE
#    Y = 0  punto más al sur (pilar fachada)   Y =  9,156  medianera NORTE
#    Z = 0  planta baja                        Z =  3,000  planta alta (+3.00)
#
#  COTAS NO GRAFIADAS
#  ------------------
#  El plano sólo acota el nivel +3.00. Las demás alturas están agrupadas en el
#  bloque ALTURAS: cambiar el número y volver a ejecutar build!
#
#  ÚNICA LIBERTAD TOMADA
#  ---------------------
#  La propuesta dibuja el recinto de cocina cerrado, sin ningún hueco (es un
#  plano de equipamiento). Se abre un paso de 0,80 m en el tabique sur, en la
#  prolongación exacta del pasillo de servicio. Se mueve en particiones_pb().
#
# ============================================================================

require 'sketchup.rb'

module CafeNapoliMalaga

  # ==========================================================================
  #  ESCALAS Y CONVERSIÓN PLANO -> MODELO
  # ==========================================================================

  M_TO_IN = 39.3700787401575        # SketchUp trabaja internamente en pulgadas

  SP = 56.692913385826770           # pt por metro — planimetría (1:50)
  SB = 94.488188976377950           # pt por metro — propuesta   (1:30)

  PA_OX = 138.3                     # pt X esquina NO exterior
  PA_OY =  40.4                     # pt Y cara exterior medianera norte
  PA_YS = 559.5                     # pt Y punto más al sur del solar

  PB_AX = 117.8                     # pt X propuesta <-> 152.5 planimetría
  PB_AY =  52.9                     # pt Y propuesta <->  48.8 planimetría

  YMAX = (PA_YS - PA_OY) / SP       # 9,1564 m de fondo total

  def self.ax(v) ; (v - PA_OX) / SP ; end          # planimetría pt -> X (m)
  def self.ay(v) ; YMAX - (v - PA_OY) / SP ; end   # planimetría pt -> Y (m)
  def self.bx(v) ; ax(152.5) + (v - PB_AX) / SB ; end   # propuesta pt -> X
  def self.by(v) ; ay(48.8)  - (v - PB_AY) / SB ; end   # propuesta pt -> Y

  # ==========================================================================
  #  ALTURAS
  # ==========================================================================

  H_PA         = 3.00          # nivel planta alta  <-- COTA DEL PLANO (+3.00)
  T_FORJADO    = 0.30          # canto del forjado
  Z_FORJ_INF   = H_PA - T_FORJADO           # 2,70 intradós
  H_LIBRE_PA   = 2.50          # altura libre en planta alta
  H_TOT        = H_PA + H_LIBRE_PA          # 5,50 cara inferior de cubierta
  T_CUBIERTA   = 0.30
  T_SOLERA     = 0.20

  H_PUERTA     = 2.10          # huecos de paso
  H_BARANDA    = 1.00          # antepechos de vidrio
  H_ESCAPARATE = 3.00          # altura del acristalamiento de fachada
  Z_VIGA_INF   = 2.60          # intradós de la viga descolgada

  N_TABICAS    = 17            # 3,00 / 17 = 0,17647 m
  T_ZANCA      = 0.20          # canto vertical de la losa de escalera

  # ==========================================================================
  #  UTILIDADES DE CONSTRUCCIÓN
  # ==========================================================================

  def self.p3(x, y, z)
    Geom::Point3d.new(x * M_TO_IN, y * M_TO_IN, z * M_TO_IN)
  end

  def self.finish(g, mat, tag, name)
    return nil if g.nil?
    g.material = mat if mat
    g.layer    = tag if tag
    g.name     = name.to_s if name
    g
  end

  def self.dedupe(pts)
    out = []
    pts.each do |p|
      q = out.last
      out << p if q.nil? || (p[0] - q[0]).abs > 1e-7 || (p[1] - q[1]).abs > 1e-7
    end
    out.shift if out.length > 1 &&
                 (out.first[0] - out.last[0]).abs < 1e-7 &&
                 (out.first[1] - out.last[1]).abs < 1e-7
    out
  end

  # Prisma vertical a partir de un polígono en planta [[x,y], ...]
  def self.prism(ents, poly, z0, z1, mat = nil, tag = nil, name = nil)
    return nil if (z1 - z0).abs < 1e-6
    poly = dedupe(poly)
    return nil if poly.length < 3
    za, zb = [z0, z1].minmax
    g = ents.add_group
    begin
      f = g.entities.add_face(poly.map { |p| p3(p[0], p[1], za) })
    rescue StandardError => e
      puts "Café Napoli: cara no válida en '#{name}' (#{e.message})"
      f = nil
    end
    if f.nil?
      g.erase!
      return nil
    end
    f.reverse! if f.normal.z < 0
    f.pushpull((zb - za) * M_TO_IN)
    finish(g, mat, tag, name)
  end

  # Caja ortogonal definida por dos esquinas en planta
  def self.box(ents, x0, y0, x1, y1, z0, z1, mat = nil, tag = nil, name = nil)
    xa, xb = [x0, x1].minmax
    ya, yb = [y0, y1].minmax
    return nil if (xb - xa) < 1e-6 || (yb - ya) < 1e-6
    prism(ents, [[xa, ya], [xb, ya], [xb, yb], [xa, yb]], z0, z1, mat, tag, name)
  end

  # Extrusión en X de un perfil definido en el plano Y-Z: [[y,z], ...]
  def self.profile_x(ents, prof, x0, x1, mat = nil, tag = nil, name = nil)
    xa, xb = [x0, x1].minmax
    return nil if (xb - xa) < 1e-6
    prof = dedupe(prof)
    return nil if prof.length < 3
    g = ents.add_group
    begin
      f = g.entities.add_face(prof.map { |q| p3(xa, q[0], q[1]) })
    rescue StandardError => e
      puts "Café Napoli: perfil no válido en '#{name}' (#{e.message})"
      f = nil
    end
    if f.nil?
      g.erase!
      return nil
    end
    f.reverse! if f.normal.x < 0
    f.pushpull((xb - xa) * M_TO_IN)
    finish(g, mat, tag, name)
  end

  # Suaviza las aristas entre caras casi coplanarias. Las superficies curvas
  # que salen de extruir un perfil poligonal se leen entonces como una
  # superficie lisa, sin el rayado de las facetas.
  def self.suavizar(g, limite = 45.0)
    return g if g.nil?
    return g unless defined?(Sketchup::Edge)
    return g unless g.entities.respond_to?(:grep)
    cos_lim = Math.cos(limite * Math::PI / 180.0)
    g.entities.grep(Sketchup::Edge).each do |e|
      caras = e.faces
      next unless caras.length == 2
      next if caras[0].normal.dot(caras[1].normal) < cos_lim
      e.soft   = true
      e.smooth = true
    end
    g
  end

  def self.cyl(ents, cx, cy, r, z0, z1, mat = nil, tag = nil, name = nil)
    za, zb = [z0, z1].minmax
    g = ents.add_group
    c = g.entities.add_circle(p3(cx, cy, za), Geom::Vector3d.new(0, 0, 1),
                              r * M_TO_IN, 32)
    f = g.entities.add_face(c)
    if f.nil?
      g.erase!
      return nil
    end
    f.reverse! if f.normal.z < 0
    f.pushpull((zb - za) * M_TO_IN)
    finish(g, mat, tag, name)
  end

  # Recorte de un perfil [[y,z],...] por un semiplano en Y
  def self.clip_y(poly, val, keep_ge)
    out = []
    n = poly.length
    n.times do |i|
      a = poly[i]
      b = poly[(i + 1) % n]
      ain = keep_ge ? a[0] >= val - 1e-9 : a[0] <= val + 1e-9
      bin = keep_ge ? b[0] >= val - 1e-9 : b[0] <= val + 1e-9
      out << a if ain
      if ain != bin
        d = b[0] - a[0]
        next if d.abs < 1e-12
        t = (val - a[0]) / d
        out << [val, a[1] + t * (b[1] - a[1])]
      end
    end
    out
  end

  # ==========================================================================
  #  MATERIALES Y ETIQUETAS
  # ==========================================================================

  PALETA = {
    # Acabados generales pedidos por el cliente
    'CN Muro'          => [218, 216, 201, 255],   # "Light Gray" #DAD8C9
    'CN Medianera'     => [212, 210, 195, 255],
    'CN Tabique'       => [224, 222, 208, 255],
    'CN Techo'         => [228, 226, 214, 255],
    'CN Suelo roble'   => [216, 186, 143, 255],   # roble claro
    'CN Hormigon'      => [198, 193, 184, 255],
    'CN Piedra'        => [206, 196, 178, 255],   # losa de piedra tipo travertino
    # Maderas calidas: listones, barra y estanteria comparten tono
    'CN Madera liston' => [201, 158, 105, 255],
    'CN Madera tablero'=> [178, 128,  74, 255],
    'CN Madera clara'  => [214, 180, 133, 255],
    # Materiales de equipamiento
    'CN Acero inox'    => [199, 204, 209, 255],
    'CN Vidrio'        => [186, 212, 228,  60],
    'CN Carpinteria'   => [ 58,  58,  56, 255],
    'CN Rotulo'        => [ 62, 107, 153, 255],
    'CN Tela'          => [231, 223, 209, 255],
    'CN Negro mate'    => [ 48,  47,  45, 255],
    'CN Laton'         => [198, 158,  84, 255],
    'CN Planta'        => [110, 139,  90, 255],
    'CN Terracota'     => [186, 130,  99, 255],
    # Acento azul de la identidad Café Napoli
    'CN Azul Napoli'   => [ 62, 107, 153, 255],
    'CN Tela azul'     => [108, 138, 168, 255],
    'CN Opal'          => [246, 243, 236, 255],
    'CN Luz calida'    => [246, 222, 174, 255],   # fondo retroiluminado
    'CN Instalacion'   => [170, 172, 174, 255],
    'CN Blanco roto'   => [247, 245, 240, 255]
  }

  TAGS = [
    '01 Solera',
    '02 Muros perimetrales',
    '03 Pilares y machones',
    '04 Forjado planta alta',
    '05 Cubierta',
    '06 Particiones planta alta',
    '07 Particiones planta baja',
    '08 Escalera',
    '09 Barandillas',
    '10 Fachada - escaparate',
    '11 Instalaciones',
    '20 Pavimento',
    '21 Cocina',
    '22 Barra',
    '23 Vitrinas y equipos',
    '24 Estanteria',
    '25 Revestimiento de madera',
    '26 Mesas y sillas',
    '27 Iluminacion',
    '28 Decoracion'
  ]

  def self.setup_materials(model)
    mats = {}
    PALETA.each do |name, rgba|
      m = model.materials[name] || model.materials.add(name)
      m.color = Sketchup::Color.new(rgba[0], rgba[1], rgba[2])
      m.alpha = rgba[3] / 255.0
      mats[name] = m
    end
    mats
  end

  def self.setup_tags(model)
    tags = {}
    TAGS.each { |n| tags[n] = model.layers[n] || model.layers.add(n) }
    tags['05 Cubierta'].visible = false
    tags
  end

  # ==========================================================================
  #  CONSTRUCCIÓN
  # ==========================================================================

  def self.build!
    model = Sketchup.active_model
    model.start_operation('Generar Café Napoli Málaga', true)
    begin
      begin
        uo = model.options['UnitsOptions']
        uo['LengthUnit']   = 4     # metros
        uo['LengthFormat'] = 0     # decimal
      rescue StandardError
      end

      mat  = setup_materials(model)
      tag  = setup_tags(model)
      ents = model.active_entities

      solera(ents, mat, tag)
      muros_perimetrales(ents, mat, tag)
      pilares(ents, mat, tag)
      forjado_planta_alta(ents, mat, tag)
      particiones_planta_alta(ents, mat, tag)
      particiones_pb(ents, mat, tag)
      escalera(ents, mat, tag)
      barandillas(ents, mat, tag)
      fachada(ents, mat, tag)
      cubierta(ents, mat, tag)
      instalaciones(ents, mat, tag)

      pavimento(ents, mat, tag)
      revestimientos(ents, mat, tag)
      cocina(ents, mat, tag)
      barra(ents, mat, tag)
      equipos_barra(ents, mat, tag)
      estanteria(ents, mat, tag)
      mobiliario_sala(ents, mat, tag)
      iluminacion(ents, mat, tag)
      decoracion(ents, mat, tag)
      frente_altillo(ents, mat, tag)
      acabado_escalera(ents, mat, tag)

      encuadre(model)
    ensure
      model.commit_operation
    end
    informe
  end

  def self.informe
    txt = <<~TXT
      CAFÉ NAPOLI — MÁLAGA · modelo generado

        Huella exterior ......... 81,73 m²
        Superficie útil PB ...... 74,20 m²
        Forjado planta alta ..... 33,74 m²
        Ancho total ............. 10,040 m   Fondo total ..... 9,156 m
        Planta alta ............. +3,00 m    Cubierta ........ +5,50 m
        Escalera ................ 16 huellas de 0,26 · 17 tabicas de 0,1765

      Interiorismo: cocina con campana y revestimiento de inox, mampara de
      vidrio de 3,18 m en un solo paño, con borde exterior de 4 cm y coronada
      a 2,40 m, que muere en el arranque de la barra, barra de 4,53 m
      a dos niveles -el mostrador de las vitrinas baja 0,12 m- con dos
      vitrinas de cristal curvo continuo encastradas, estantería de cajas de acero
      negro retroiluminada, listones de suelo a techo en los soportes,
      6 mesas con 12 sillas tapizadas, iluminación y decoración.
      La entrada queda despejada.
    TXT
    puts txt
    txt
  end

  # --------------------------------------------------------------------------
  #  PERÍMETROS
  # --------------------------------------------------------------------------

  # Contorno exterior del local
  def self.perimetro_exterior
    [[ax(138.3), ay( 40.4)],
     [ax(707.5), ay( 40.4)],
     [ax(707.5), ay(540.8)],
     [ax(491.5), ay(540.8)],
     [ax(491.5), ay(559.5)],
     [ax(463.2), ay(559.5)],
     [ax(463.2), ay(471.0)],
     [ax(138.3), ay(471.0)]]
  end

  # --------------------------------------------------------------------------
  #  1. SOLERA
  # --------------------------------------------------------------------------

  def self.solera(ents, mat, tag)
    prism(ents, perimetro_exterior, -T_SOLERA, 0.0,
          mat['CN Hormigon'], tag['01 Solera'], 'Solera planta baja')
  end

  # --------------------------------------------------------------------------
  #  2. MUROS PERIMETRALES
  #     Los rectángulos teselan el espesor de muro sin solapes ni huecos.
  # --------------------------------------------------------------------------

  def self.muros_perimetrales(ents, mat, tag)
    t  = tag['02 Muros perimetrales']
    md = mat['CN Medianera']
    mu = mat['CN Muro']

    # Medianera norte  (e = 0,148)
    box(ents, ax(138.3), ay(40.4), ax(707.5), ay(48.8), 0.0, H_TOT, md, t,
        'Medianera Norte')

    # Muro oeste  (e = 0,250)
    box(ents, ax(138.3), ay(48.8), ax(152.5), ay(445.6), 0.0, H_TOT, mu, t,
        'Muro Oeste')
    box(ents, ax(138.3), ay(445.6), ax(167.2), ay(471.0), 0.0, H_TOT, mu, t,
        'Muro Oeste - esquina SO')

    # Muro sur del cuerpo posterior: en la realidad no es un muro ciego sino
    # el ventanal corrido de la cafeteria (foto de la fachada). Carpinteria
    # con el mismo lenguaje del escaparate: umbral, cuatro panos de vidrio
    # con montantes, cabecero, banda de rotulo y peto de muro arriba.
    vx0  = ax(167.2)
    vx1  = ax(477.3)
    vye  = ay(471.0)                   # cara exterior del cerramiento
    vyi  = vye + 0.06                  # profundidad de la carpinteria
    vid  = mat['CN Vidrio']
    carp = mat['CN Carpinteria']
    paso = (vx1 - vx0 - 3 * 0.05) / 4.0
    x = vx0
    4.times do |i|
      box(ents, x, vye, x + paso, vyi, 0.06, H_ESCAPARATE - 0.08, vid, t,
          "Ventanal Sur - pano #{i + 1}")
      if i < 3
        box(ents, x + paso, vye, x + paso + 0.05, vyi, 0.0, H_ESCAPARATE,
            carp, t, "Ventanal Sur - montante #{i + 1}")
      end
      x += paso + 0.05
    end
    box(ents, vx0, vye, vx1, vyi, 0.0, 0.06, carp, t, 'Ventanal Sur - umbral')
    box(ents, vx0, vye, vx1, vyi, H_ESCAPARATE - 0.08, H_ESCAPARATE, carp, t,
        'Ventanal Sur - cabecero')
    box(ents, vx0, vye, vx1, ay(456.9), H_ESCAPARATE, H_ESCAPARATE + 0.55,
        mat['CN Rotulo'], t, 'Ventanal Sur - banda de rotulo')
    box(ents, vx0, vye, vx1, ay(456.9), H_ESCAPARATE + 0.55, H_TOT, mu, t,
        'Ventanal Sur - peto alto')

    # Muro oeste del cuello de fachada
    box(ents, ax(463.2), ay(471.0), ax(477.3), ay(505.1), 0.0, H_TOT, mu, t,
        'Muro Oeste del cuello')

    # Medianera este  (e = 0,150 ; 0,330 en el cuello)
    box(ents, ax(699.0), ay(48.8), ax(707.5), ay(478.5), 0.0, H_TOT, md, t,
        'Medianera Este')
    box(ents, ax(688.8), ay(478.5), ax(707.5), ay(540.8), 0.0, H_TOT, md, t,
        'Medianera Este - cuello')

    # Trasdosado de 0,10 m bajo el forjado, grafiado en la propuesta
    box(ents, bx(326.5), ay(48.8), ax(699.0), by(62.4), 0.0, Z_FORJ_INF, mu, t,
        'Trasdosado Norte (planta baja)')
  end

  # --------------------------------------------------------------------------
  #  3. PILARES, MACHONES Y VIGA
  # --------------------------------------------------------------------------

  def self.pilares(ents, mat, tag)
    t = tag['03 Pilares y machones']
    h = mat['CN Hormigon']
    m = mat['CN Muro']

    # Machón del muro oeste  (0,37 x 0,60)
    box(ents, ax(152.5), ay(255.8), ax(173.5), ay(289.7), 0.0, H_TOT, m, t,
        'Machon muro Oeste')

    # Pilastra del muro sur  (0,60 x 0,30)
    box(ents, ax(212.0), ay(440.0), ax(246.1), ay(456.9), 0.0, H_TOT, m, t,
        'Pilastra muro Sur')

    # Machón de la medianera este, junto a la escalera  (0,60 x 0,20)
    box(ents, ax(687.6), ay(258.5), ax(699.0), ay(292.6), 0.0, H_TOT, m, t,
        'Machon medianera Este')

    # Pilar central del local  (0,60 x 0,90).
    # Se interrumpe en el forjado, como un pilar de hormigón real.
    box(ents, ax(456.9), ay(241.5), ax(490.9), ay(292.6), 0.0, Z_FORJ_INF, h, t,
        'Pilar central (planta baja)')
    box(ents, ax(456.9), ay(241.5), ax(490.9), ay(292.6), H_PA, H_TOT, h, t,
        'Pilar central (planta alta)')

    # Pilar de fachada  (0,50 x 0,96)
    box(ents, ax(463.2), ay(505.1), ax(491.5), ay(559.5), 0.0, H_TOT, h, t,
        'Pilar de fachada')

    # Viga descolgada del machón oeste al borde del forjado  (e = 0,25).
    # Muere en la cara vista del machón revestido, 3,8 cm al este del hormigón,
    # para que los listones del machón puedan correr de suelo a techo.
    box(ents, ax(173.5) + 0.038, ay(271.6), ax(275.0), ay(285.8),
        Z_VIGA_INF, H_PA, h, t, 'Viga descolgada')
  end

  # --------------------------------------------------------------------------
  #  4. FORJADO DE PLANTA ALTA
  # --------------------------------------------------------------------------

  def self.planta_forjado
    [[ax(277.8), ay( 48.8)],
     [ax(699.0), ay( 48.8)],
     [ax(699.0), ay(120.8)],
     [ax(637.8), ay(120.8)],
     [ax(637.8), ay(336.2)],
     [ax(275.0), ay(336.2)],
     [ax(275.0), ay(133.8)],
     [ax(277.8), ay(133.8)]]
  end

  def self.forjado_planta_alta(ents, mat, tag)
    prism(ents, planta_forjado, Z_FORJ_INF, H_PA,
          mat['CN Techo'], tag['04 Forjado planta alta'],
          'Forjado planta alta (+3.00)')
  end

  def self.cubierta(ents, mat, tag)
    prism(ents, perimetro_exterior, H_TOT, H_TOT + T_CUBIERTA,
          mat['CN Hormigon'], tag['05 Cubierta'], 'Forjado de cubierta')
  end

  # --------------------------------------------------------------------------
  #  5. PARTICIONES DE PLANTA ALTA  (ASEO / ALMACÉN-2)
  # --------------------------------------------------------------------------

  def self.particiones_planta_alta(ents, mat, tag)
    t  = tag['06 Particiones planta alta']
    m  = mat['CN Tabique']
    z0 = H_PA
    z1 = H_TOT
    zd = H_PA + H_PUERTA          # arranque de dinteles

    box(ents, ax(277.8), ay(48.8), ax(283.4), ay(133.8), z0, z1, m, t,
        'PA Tabique Oeste del aseo')

    box(ents, ax(283.4), ay(128.2), ax(313.4), ay(133.8), z0, z1, m, t,
        'PA Tabique Sur - tramo Oeste')
    box(ents, ax(356.5), ay(128.2), ax(564.1), ay(133.8), z0, z1, m, t,
        'PA Tabique Sur - tramo Este')
    box(ents, ax(313.4), ay(128.2), ax(356.5), ay(133.8), zd, z1, m, t,
        'PA Dintel puerta aseo (hueco 0,76 m)')

    box(ents, ax(391.2), ay(94.2), ax(396.8), ay(128.2), z0, z1, m, t,
        'PA Tabique del inodoro')
    box(ents, ax(391.2), ay(48.8), ax(396.8), ay(94.2), zd, z1, m, t,
        'PA Dintel puerta inodoro (hueco 0,80 m)')

    box(ents, ax(447.8), ay(48.8), ax(453.4), ay(128.2), z0, z1, m, t,
        'PA Tabique aseo / almacen')

    box(ents, ax(558.3), ay(101.9), ax(564.1), ay(128.2), z0, z1, m, t,
        'PA Tabique Este del almacen')
    box(ents, ax(558.3), ay(48.8), ax(564.1), ay(101.9), zd, z1, m, t,
        'PA Dintel puerta almacen (hueco 0,94 m)')
  end

  # --------------------------------------------------------------------------
  #  6. PARTICIONES DE PLANTA BAJA  (recinto de cocina de la propuesta)
  # --------------------------------------------------------------------------

  # Mampara de la cocina: una sola hoja de vidrio con un borde exterior fino.
  # Sin montantes ni travesaños intermedios.
  MAMP_B   = 0.04          # escuadría del borde exterior
  MAMP_ALT = 2.40          # coronación

  def self.particiones_pb(ents, mat, tag)
    t   = tag['07 Particiones planta baja']
    car = mat['CN Carpinteria']
    vid = mat['CN Vidrio']

    # El tabique este de la cocina se elimina: la cocina queda abierta al
    # office, por donde entra el personal desde detrás de la barra.
    #
    # El tabique sur se sustituye por una MAMPARA DE VIDRIO corrida que
    # arranca en el muro oeste y muere justo donde empieza la barra: 3,18 m
    # de largo, un único paño, con borde exterior de 4 cm y nada por dentro.
    #
    # Corona a 2,40 m, por debajo del frente del altillo -que arranca a
    # 2,48- y del intradós del forjado -2,70-, para que no la corte nada
    # de la planta primera.
    x0 = bx(117.8)                       # 0,251 · cara interior del muro oeste
    x1 = BAR_X0 - 0.06                   # 3,430 · arranque de la barra
    ya = by(254.6)
    yb = by(249.9)
    b  = MAMP_B

    box(ents, x0, ya, x0 + b, yb, 0.0, MAMP_ALT, car, t,
        'PB Mampara - borde Oeste')
    box(ents, x1 - b, ya, x1, yb, 0.0, MAMP_ALT, car, t,
        'PB Mampara - borde Este')
    box(ents, x0 + b, ya, x1 - b, yb, 0.0, b, car, t,
        'PB Mampara - borde inferior')
    box(ents, x0 + b, ya, x1 - b, yb, MAMP_ALT - b, MAMP_ALT, car, t,
        'PB Mampara - borde superior')
    box(ents, x0 + b, ya, x1 - b, yb, b, MAMP_ALT - b, vid, t,
        'PB Mampara de vidrio de la cocina (3,18 m)')
  end

  # --------------------------------------------------------------------------
  #  7. ESCALERA
  #     16 huellas de 0,26 m · 17 tabicas de 3,00/17 = 0,17647 m
  #     El machón de la medianera este invade los peldaños centrales, tal como
  #     está grafiado: la losa se parte para no atravesarlo.
  # --------------------------------------------------------------------------

  def self.esc_datos
    y_pie  = ay(356.6)                      # arranque en planta baja
    y_alto = ay(120.8)                      # llegada a +3.00
    huella = (y_alto - y_pie) / 16.0
    tabica = H_PA / N_TABICAS
    [y_pie, y_alto, huella, tabica]
  end

  def self.esc_perfil
    y_pie, y_alto, huella, tabica = esc_datos
    prof = [[y_pie, 0.0]]
    (1..N_TABICAS).each do |i|
      y_r = y_pie + (i - 1) * huella
      prof << [y_r, i * tabica]                       # tabica
      prof << [y_r + huella, i * tabica] if i <= 16   # huella
    end
    prof << [y_alto, H_PA - T_ZANCA]
    prof << [y_pie + T_ZANCA * (16 * huella) / H_PA, 0.0]
    prof
  end

  def self.escalera(ents, mat, tag)
    t = tag['08 Escalera']
    h = mat['CN Hormigon']
    _y_pie, _y_alto, _hu, tabica = esc_datos
    prof = esc_perfil

    # Banda libre del machón
    profile_x(ents, prof, ax(637.8), ax(687.6), h, t,
              'Escalera - losa (banda libre)')

    # Banda del machón: la losa se interrumpe entre Y del machón
    y_m0 = ay(292.6)      # extremo sur del machón
    y_m1 = ay(258.5)      # extremo norte del machón
    profile_x(ents, clip_y(prof, y_m0, false), ax(687.6), ax(699.0), h, t,
              'Escalera - losa junto al machon (tramo bajo)')
    profile_x(ents, clip_y(prof, y_m1, true), ax(687.6), ax(699.0), h, t,
              'Escalera - losa junto al machon (tramo alto)')

    # Peldaño de arranque ensanchado, tal como está grafiado
    box(ents, ax(628.0), ay(356.6), ax(637.8), ay(341.9), 0.0, tabica, h, t,
        'Escalera - peldano de arranque')
  end

  # --------------------------------------------------------------------------
  #  8. BARANDILLAS DE VIDRIO  (e = 0,05 m, según el trazado del plano)
  # --------------------------------------------------------------------------

  def self.esc_cota(y)
    y_pie, _y_alto, huella, tabica = esc_datos
    z = ((y - y_pie) / huella) * tabica
    z < 0.0 ? 0.0 : z
  end

  def self.barandillas(ents, mat, tag)
    t = tag['09 Barandillas']
    v = mat['CN Vidrio']

    # Borde oeste y sur del hueco (VACÍO SOBRE PLANTA BAJA)
    box(ents, ax(275.0), ay(133.8), ax(277.8), ay(333.4),
        H_PA, H_PA + H_BARANDA, v, t, 'Barandilla del hueco - Oeste')
    box(ents, ax(275.0), ay(333.4), ax(634.9), ay(336.2),
        H_PA, H_PA + H_BARANDA, v, t, 'Barandilla del hueco - Sur')

    # Borde de la caja de escalera. Arranca en la llegada de la escalera
    # (y = 120,8 pt) para dejar libre el paso del rellano a la zona de paso.
    box(ents, ax(634.9), ay(120.8), ax(637.8), ay(336.2),
        H_PA, H_PA + H_BARANDA, v, t, 'Barandilla de la caja de escalera')

    # Barandilla de vidrio del tramo inclinado: continua el mismo plano de
    # la caja, siguiendo la pendiente de la losa desde el arranque.
    y_pie, y_alto, _hu, _ta = esc_datos
    profile_x(ents, [[y_pie, 0.0], [y_alto, H_PA],
                     [y_alto, H_PA + H_BARANDA], [y_pie, H_BARANDA]],
              ax(634.9), ax(637.8), v, t, 'Barandilla de la escalera')
  end

  # --------------------------------------------------------------------------
  #  9. FACHADA
  # --------------------------------------------------------------------------

  def self.fachada(ents, mat, tag)
    t   = tag['10 Fachada - escaparate']
    y0  = ay(540.8)          # cara exterior
    y1  = ay(538.0)          # cara interior
    xa  = ax(491.5)
    xm0 = ax(571.4)          # montante grafiado en el plano
    xm1 = ax(574.3)
    xb  = ax(688.8)

    box(ents, xa,  y0, xm0, y1, 0.06, H_ESCAPARATE - 0.08,
        mat['CN Vidrio'], t, 'Escaparate - pano Oeste')
    box(ents, xm1, y0, xb,  y1, 0.06, H_ESCAPARATE - 0.08,
        mat['CN Vidrio'], t, 'Escaparate - pano Este')

    box(ents, xm0, y0, xm1, y1, 0.0, H_ESCAPARATE,
        mat['CN Carpinteria'], t, 'Escaparate - montante')
    [[xa, xm0], [xm1, xb]].each_with_index do |(u0, u1), i|
      box(ents, u0, y0, u1, y1, 0.0, 0.06,
          mat['CN Carpinteria'], t, "Escaparate - umbral #{i + 1}")
      box(ents, u0, y0, u1, y1, H_ESCAPARATE - 0.08, H_ESCAPARATE,
          mat['CN Carpinteria'], t, "Escaparate - cabecero #{i + 1}")
    end

    box(ents, xa, y0, xb, y1, H_ESCAPARATE, H_ESCAPARATE + 0.55,
        mat['CN Rotulo'], t, 'Banda de rotulo')
    box(ents, xa, y0, xb, y1, H_ESCAPARATE + 0.55, H_TOT,
        mat['CN Muro'], t, 'Peto sobre el escaparate')
  end

  # ==========================================================================
  #                            I N T E R I O R I S M O
  # ==========================================================================

  # Perímetro interior de planta baja (para el pavimento)
  def self.perimetro_interior
    # el borde sur de la sala llega ahora hasta la cara interior del ventanal
    yv = ay(471.0) + 0.06
    [[ax(152.5), ay( 48.8)], [ax(699.0), ay( 48.8)], [ax(699.0), ay(478.5)],
     [ax(688.8), ay(478.5)], [ax(688.8), ay(538.0)], [ax(491.5), ay(538.0)],
     [ax(491.5), ay(505.1)], [ax(477.3), ay(505.1)], [ax(477.3), yv],
     [ax(167.2), yv], [ax(167.2), ay(445.6)],
     [ax(152.5), ay(445.6)], [ax(152.5), ay(289.7)], [ax(173.5), ay(289.7)],
     [ax(173.5), ay(255.8)], [ax(152.5), ay(255.8)]]
  end

  # --------------------------------------------------------------------------
  #  11. INSTALACIONES
  # --------------------------------------------------------------------------

  # Bajante grafiada en el rincón noroeste del local (Ø exterior 0,20)
  def self.bajante_xy
    [ax(264.5), ay(57.6)]
  end

  def self.instalaciones(ents, mat, tag)
    cx, cy = bajante_xy
    cyl(ents, cx, cy, 0.1005, 0.0, H_TOT,
        mat['CN Instalacion'], tag['11 Instalaciones'], 'Bajante (D 0,20)')
  end

  def self.pavimento(ents, mat, tag)
    prism(ents, perimetro_interior, 0.0, 0.02,
          mat['CN Suelo roble'], tag['20 Pavimento'], 'Pavimento roble claro')
    prism(ents, planta_forjado, H_PA, H_PA + 0.02,
          mat['CN Suelo roble'], tag['20 Pavimento'], 'Pavimento roble planta alta')
  end

  # --------------------------------------------------------------------------
  #  Listones de madera sobre una cara (revestimiento acanalado)
  # --------------------------------------------------------------------------

  def self.slat_run(ents, x0, y0, x1, y1, z0, z1, thick, mat, tag, name,
                    pitch = 0.075, w = 0.048)
    if (y1 - y0).abs < 1e-9
      a0, a1 = [x0, x1].minmax
      n = ((a1 - a0) / pitch).round
      n = 1 if n < 1
      step = (a1 - a0) / n
      n.times do |i|
        a = a0 + i * step + (step - w) / 2.0
        box(ents, a, y0, a + w, y0 + thick, z0, z1, mat, tag, name)
      end
    else
      a0, a1 = [y0, y1].minmax
      n = ((a1 - a0) / pitch).round
      n = 1 if n < 1
      step = (a1 - a0) / n
      n.times do |i|
        a = a0 + i * step + (step - w) / 2.0
        box(ents, x0, a, x0 + thick, a + w, z0, z1, mat, tag, name)
      end
    end
  end

  # Reviste un soporte: tablero de fondo que envuelve el soporte + listones
  # sobre él + piezas de esquina que cierran la arista. Sin el fondo se vería
  # el hormigón entre listón y listón; sin las esquinas, en los cantos.
  def self.revestir(ents, x0, y0, x1, y1, z1, caras, mats, tag, name,
                    t = 0.026, z0 = 0.0)
    tc  = 0.012                                   # canto del tablero de fondo
    fon = mats['CN Madera tablero']
    lis = mats['CN Madera liston']
    sx0 = caras.include?(:o) ? x0 - tc : x0
    sx1 = caras.include?(:e) ? x1 + tc : x1
    sy0 = caras.include?(:s) ? y0 - tc : y0
    sy1 = caras.include?(:n) ? y1 + tc : y1
    nf  = "#{name} - fondo"

    box(ents, sx0, sy0, sx1, y0, z0, z1, fon, tag, nf) if caras.include?(:s)
    box(ents, sx0, y1, sx1, sy1, z0, z1, fon, tag, nf) if caras.include?(:n)
    box(ents, sx0, y0, x0, y1, z0, z1, fon, tag, nf) if caras.include?(:o)
    box(ents, x1, y0, sx1, y1, z0, z1, fon, tag, nf) if caras.include?(:e)

    slat_run(ents, sx0, sy0, sx1, sy0, z0, z1, -t, lis, tag, name) if caras.include?(:s)
    slat_run(ents, sx0, sy1, sx1, sy1, z0, z1,  t, lis, tag, name) if caras.include?(:n)
    slat_run(ents, sx0, sy0, sx0, sy1, z0, z1, -t, lis, tag, name) if caras.include?(:o)
    slat_run(ents, sx1, sy0, sx1, sy1, z0, z1,  t, lis, tag, name) if caras.include?(:e)

    g  = 0.0135
    nm = "#{name} - esquina"
    if caras.include?(:s) && caras.include?(:o)
      box(ents, sx0 - t, sy0 - t, sx0, sy0 + g, z0, z1, lis, tag, nm)
      box(ents, sx0, sy0 - t, sx0 + g, sy0, z0, z1, lis, tag, nm)
    end
    if caras.include?(:s) && caras.include?(:e)
      box(ents, sx1, sy0 - t, sx1 + t, sy0 + g, z0, z1, lis, tag, nm)
      box(ents, sx1 - g, sy0 - t, sx1, sy0, z0, z1, lis, tag, nm)
    end
    if caras.include?(:n) && caras.include?(:o)
      box(ents, sx0 - t, sy1 - g, sx0, sy1 + t, z0, z1, lis, tag, nm)
      box(ents, sx0, sy1, sx0 + g, sy1 + t, z0, z1, lis, tag, nm)
    end
    if caras.include?(:n) && caras.include?(:e)
      box(ents, sx1, sy1 - g, sx1 + t, sy1 + t, z0, z1, lis, tag, nm)
      box(ents, sx1 - g, sy1, sx1, sy1 + t, z0, z1, lis, tag, nm)
    end
  end

  # Aplacado de losa de piedra sobre las caras vistas de un soporte. El
  # despiece de las losas lo dibuja la textura; aqui solo va la costra.
  def self.aplacar(ents, x0, y0, x1, y1, z1, caras, mats, tag, name,
                   t = 0.02, z0 = 0.0)
    pie = mats['CN Piedra']
    box(ents, x0 - t, y0 - t, x1 + t, y0, z0, z1, pie, tag, name) if caras.include?(:s)
    box(ents, x0 - t, y1, x1 + t, y1 + t, z0, z1, pie, tag, name) if caras.include?(:n)
    box(ents, x0 - t, y0, x0, y1, z0, z1, pie, tag, name) if caras.include?(:o)
    box(ents, x1, y0, x1 + t, y1, z0, z1, pie, tag, name) if caras.include?(:e)
  end

  def self.revestimientos(ents, mat, tag)
    t = tag['25 Revestimiento de madera']
    m = mat
    h = Z_FORJ_INF

    # Pilar central: las cuatro caras, en planta baja y de nuevo en el
    # tramo de planta alta (el forjado lo interrumpe entre medias)
    revestir(ents, ax(456.9), ay(292.6), ax(490.9), ay(241.5), h,
             [:s, :n, :o, :e], m, t, 'Listones pilar central')
    revestir(ents, ax(456.9), ay(292.6), ax(490.9), ay(241.5), H_TOT,
             [:s, :n, :o, :e], m, t, 'Listones pilar central PA',
             0.026, H_PA + 0.02)
    # Machon del muro oeste: listones de madera de suelo a techo, como el
    # resto de soportes revestidos (esta en la doble altura).
    revestir(ents, ax(152.5), ay(289.7), ax(173.5), ay(255.8), H_TOT,
             [:s, :n, :e], m, t, 'Listones machon Oeste')
    # La pilastra del muro sur y el machon del cuello quedan con el color
    # de la pared: solo el pilar central de la entrada lleva piedra.
    # Pilar de fachada: losa de piedra en todas las caras vistas, como el
    # pilar real de la foto de fachada.
    aplacar(ents, ax(463.2), ay(559.5), ax(491.5), ay(505.1), H_TOT,
            [:s, :o], m, t, 'Aplacado pilar fachada')
    box(ents, ax(477.3), ay(505.1), ax(491.5) + 0.02, ay(505.1) + 0.02,
        0.0, H_TOT, m['CN Piedra'], t, 'Aplacado pilar fachada - cara norte')
    box(ents, ax(491.5), ay(538.0) + 0.04, ax(491.5) + 0.02, ay(505.1),
        0.0, H_TOT, m['CN Piedra'], t, 'Aplacado pilar fachada - cara este')
    box(ents, ax(491.5), ay(559.5), ax(491.5) + 0.02, ay(538.0) - 0.01,
        0.0, H_TOT, m['CN Piedra'], t, 'Aplacado pilar fachada - cara este')
    # Machon de la medianera este: revestido sobre el peldañeado hasta el
    # forjado, y de nuevo en el tramo de planta alta hasta la cubierta.
    revestir(ents, ax(687.6), ay(292.6), ax(699.0), ay(258.5), h,
             [:s, :n, :o], m, t, 'Listones machon Este', 0.026, 1.30)
    revestir(ents, ax(687.6), ay(292.6), ax(699.0), ay(258.5), H_TOT,
             [:s, :n, :o], m, t, 'Listones machon Este PA',
             0.026, H_PA + 0.02)

    # Viga descolgada: aplacado de losa de piedra en intrados y costados.
    # Arranca 3,8 cm mas al este, en la cara vista del machon revestido.
    vx0 = ax(173.5) + 0.038; vx1 = ax(275.0)
    vy0 = ay(285.8); vy1 = ay(271.6)
    box(ents, vx0, vy0 - 0.028, vx1, vy1 + 0.028,
        Z_VIGA_INF - 0.028, Z_VIGA_INF, mat['CN Piedra'], t,
        'Aplacado de la viga - intrados')
    box(ents, vx0, vy0 - 0.028, vx1, vy0, Z_VIGA_INF, H_PA,
        mat['CN Piedra'], t, 'Aplacado de la viga - costado Sur')
    box(ents, vx0, vy1, vx1, vy1 + 0.028, Z_VIGA_INF, H_PA,
        mat['CN Piedra'], t, 'Aplacado de la viga - costado Norte')
  end

  # --------------------------------------------------------------------------
  #  COCINA  (bloque de coccion contra la medianera norte, con campana)
  # --------------------------------------------------------------------------

  def self.cocina(ents, mat, tag)
    t    = tag['21 Cocina']
    inox = mat['CN Acero inox']
    neg  = mat['CN Negro mate']

    yn  = ay(48.8)          # cara interior de la medianera norte
    ynt = by(62.4)          # idem con trasdosado (X > 2,46)
    xo  = bx(117.8)         # cara interior del muro oeste
    xe  = bx(354.0)         # extremo este de la cocina
    ys  = by(249.9)         # cara norte de la mampara de vidrio

    # Revestimiento de acero inoxidable: muro de la coccion y el de su izquierda
    box(ents, xo, yn - 0.05, bx(326.5), yn, 0.0, 2.20, inox, t,
        'Inox muro Norte de cocina')
    box(ents, xo, ys, xo + 0.05, yn - 0.05, 0.0, 2.20, inox, t,
        'Inox muro Oeste de cocina')

    # Bloque de coccion. Muere antes de la bajante, que baja por este rincon.
    xlim = bajante_xy[0] - 0.1005 - 0.06       # tope este libre de la bajante
    xb0  = xo + 0.17
    xb1  = xlim - 0.05
    box(ents, xb0, yn - 0.75, xb1, yn - 0.05, 0.0, 0.90, inox, t,
        'Bloque de coccion')
    box(ents, xb0, yn - 0.75, xb1, yn - 0.05, 0.90, 0.93, neg, t,
        'Encimera de coccion')
    4.times do |i|
      cyl(ents, xb0 + (i + 0.5) * (xb1 - xb0) / 4.0, yn - 0.38, 0.115,
          0.93, 0.955, neg, t, "Fuego #{i + 1}")
    end
    # Horno bajo la encimera
    box(ents, xo + 1.15, yn - 0.78, xb1 - 0.03, yn - 0.75, 0.18, 0.78,
        neg, t, 'Horno - puerta')

    # Campana extractora y conducto
    box(ents, xb0 - 0.05, yn - 0.95, xlim, yn - 0.05, 1.95, 2.05, inox, t,
        'Campana - faldon')
    box(ents, xb0 + 0.05, yn - 0.85, xlim - 0.10, yn - 0.05, 2.05, 2.32,
        inox, t, 'Campana - cuerpo')
    box(ents, xo + 0.85, yn - 0.42, xo + 1.25, yn - 0.05, 2.32, Z_FORJ_INF,
        inox, t, 'Campana - conducto')

    # Mesa de trabajo contra el muro oeste
    box(ents, xo + 0.05, ys + 0.10, xo + 0.80, yn - 0.85, 0.0, 0.88, inox, t,
        'Mesa de trabajo')
    box(ents, xo + 0.05, ys + 0.10, xo + 0.80, yn - 0.85, 0.88, 0.92, inox, t,
        'Mesa de trabajo - encimera')
    # Estante mural
    box(ents, xo + 0.05, ys + 0.35, xo + 0.42, yn - 1.10, 1.55, 1.59, inox, t,
        'Estante mural de cocina')
  end

  # --------------------------------------------------------------------------
  #  BARRA  (base con frente de listones + tabla de madera maciza encima)
  # --------------------------------------------------------------------------

  BAR_X0 = 3.49
  BAR_X1 = 8.02
  BAR_Y0 = 6.55
  BAR_Y1 = 7.43
  BAR_H  = 0.92

  # La barra tiene dos niveles: el tramo de las vitrinas baja 0,12 m respecto
  # al de la cafetera y la caja, como en los mostradores de pastelería.
  BAR_XSTEP = 6.16                # eje del desnivel
  BAR_DZ    = 0.12                # cuánto baja el mostrador de las vitrinas
  BAR_HB    = BAR_H - BAR_DZ      # 0,80 · coronación del cuerpo bajo

  # Rebaje de las vitrinas dentro del mostrador bajo: quedan 0,22 m por debajo
  # de su tabla de madera, encastradas, no apoyadas encima.
  VIT_Y0  = BAR_Y0 + 0.06         # borde delantero del rebaje, lado sala
  VIT_Y1  = BAR_Y1 - 0.08         # borde trasero, lado servicio
  VIT_Z0  = BAR_HB - 0.16         # 0,64 · fondo del rebaje
  VIT_REV = 0.02                  # holgura entre la vitrina y el rebaje
  VIT_ZD  = VIT_Z0 + 0.10         # 0,74 · cara alta de la bandeja de acero
  VIT_ZS  = VIT_ZD + 0.18         # 0,92 · arranque de la curva
  VIT_R   = 0.24                  # radio del cristal curvo
  VIT_ZT  = VIT_ZS + VIT_R        # 1,16 · coronación, 0,30 sobre la tabla

  # Huella en planta de cada vitrina
  def self.huecos_vitrina
    [[3.62, 4.78], [4.86, 6.02]]
  end

  def self.barra(ents, mat, tag)
    t   = tag['22 Barra']
    cla = mat['CN Madera clara']
    tab = mat['CN Madera tablero']
    hu  = huecos_vitrina

    # Zócalo retranqueado y cuerpo macizo hasta el fondo del rebaje
    box(ents, BAR_X0 + 0.05, BAR_Y0 + 0.05, BAR_X1 - 0.05, BAR_Y1 - 0.05,
        0.0, 0.10, mat['CN Negro mate'], t, 'Barra - zocalo retranqueado')
    box(ents, BAR_X0, BAR_Y0, BAR_X1, BAR_Y1, 0.10, VIT_Z0, cla, t,
        'Barra - cuerpo')

    # Mostrador BAJO, el de las vitrinas: sube a 0,80 y se parte por los rebajes
    macizos_x(BAR_X0, BAR_XSTEP, hu).each do |a, b|
      box(ents, a, BAR_Y0, b, BAR_Y1, VIT_Z0, BAR_HB, cla, t,
          'Barra - cuerpo del mostrador bajo')
    end
    hu.each do |a, b|
      box(ents, a, BAR_Y0, b, VIT_Y0, VIT_Z0, BAR_HB, cla, t,
          'Barra - antepecho del rebaje')
      box(ents, a, VIT_Y1, b, BAR_Y1, VIT_Z0, BAR_HB, cla, t,
          'Barra - trasera del rebaje')
    end

    # Mostrador ALTO, el de la cafetera y la caja
    box(ents, BAR_XSTEP, BAR_Y0, BAR_X1, BAR_Y1, VIT_Z0, BAR_H, cla, t,
        'Barra - cuerpo del mostrador alto')

    # Frente de listones azules, en dos tramos por el desnivel
    azul = mat.dup
    azul['CN Madera liston'] = mat['CN Azul Napoli']   # listones azules
    revestir(ents, BAR_X0, BAR_Y0, BAR_XSTEP, BAR_Y1, BAR_HB, [:s, :o],
             azul, t, 'Barra - listones del mostrador bajo', 0.026, 0.10)
    revestir(ents, BAR_XSTEP, BAR_Y0, BAR_X1, BAR_Y1, BAR_H, [:s, :e],
             azul, t, 'Barra - listones del mostrador alto', 0.026, 0.10)

    # Tabla de madera maciza, a dos niveles, recortada por los dos rebajes
    tx0 = BAR_X0 - 0.06 ; tx1 = BAR_X1 + 0.06
    ty0 = BAR_Y0 - 0.09 ; ty1 = BAR_Y1 + 0.04
    macizos_x(tx0, BAR_XSTEP, hu).each do |a, b|
      box(ents, a, ty0, b, ty1, BAR_HB, BAR_HB + 0.06, tab, t,
          'Barra - tabla del mostrador bajo')
    end
    hu.each do |a, b|
      box(ents, a, ty0, b, VIT_Y0, BAR_HB, BAR_HB + 0.06, tab, t,
          'Barra - tabla, borde delantero')
      box(ents, a, VIT_Y1, b, ty1, BAR_HB, BAR_HB + 0.06, tab, t,
          'Barra - tabla, borde trasero')
    end

    # Frente del desnivel y tabla del mostrador alto, que vuela 3 cm sobre él
    box(ents, BAR_XSTEP - 0.026, BAR_Y0, BAR_XSTEP, BAR_Y1,
        BAR_HB + 0.06, BAR_H, tab, t, 'Barra - frente del desnivel')
    box(ents, BAR_XSTEP - 0.03, ty0, tx1, ty1, BAR_H, BAR_H + 0.06, tab, t,
        'Barra - tabla del mostrador alto')
  end

  # Tramos macizos de [x0, x1] una vez descontados los huecos
  def self.macizos_x(x0, x1, huecos)
    cortes = [x0] + huecos.flatten + [x1]
    (0...cortes.length).step(2).map { |i| [cortes[i], cortes[i + 1]] }
                       .select { |a, b| b - a > 1e-6 }
  end

  # --------------------------------------------------------------------------
  #  VITRINAS DE CRISTAL CURVO
  #  Bandeja de acero en el fondo del rebaje, tres baldas escalonadas y un
  #  cristal que sube recto y voltea en cuarto de círculo, como el de las
  #  vitrinas de pastelería.
  # --------------------------------------------------------------------------

  # Sección de la vitrina en el plano Y-Z, del frente al fondo. La curva es
  # tangente al frente vertical y a la tapa plana, así que una vez suavizada
  # se lee como un cristal continuo, sin aristas intermedias.
  def self.vit_perfil(y0, y1, n = 20)
    p = [[y0, VIT_ZD], [y0, VIT_ZS]]
    (1..n).each do |i|
      a = (Math::PI / 2) * i / n
      p << [y0 + VIT_R - VIT_R * Math.cos(a), VIT_ZS + VIT_R * Math.sin(a)]
    end
    p << [y1, VIT_ZT]
    p
  end

  def self.vitrina(ents, mat, tag, x0, x1, nombre)
    t    = tag['23 Vitrinas y equipos']
    inox = mat['CN Acero inox']
    vid  = mat['CN Vidrio']
    e    = 0.010                       # espesor del cristal
    n    = 20

    # La vitrina se posa dentro del rebaje con holgura por los cuatro lados:
    # ninguna cara queda a ras de la madera, así que nada se atraviesa.
    gx0 = x0 + VIT_REV ; gx1 = x1 - VIT_REV
    gy0 = VIT_Y0 + VIT_REV ; gy1 = VIT_Y1 - VIT_REV
    paso = (gy1 - gy0 - 0.10) / 3.0    # fondo de cada balda escalonada

    # Bandeja de acero en el fondo del rebaje
    box(ents, gx0, gy0, gx1, gy1, VIT_Z0, VIT_ZD, inox, t,
        "#{nombre} - bandeja")

    # Cristal curvo: banda cerrada, cara exterior y cara interior
    ext = vit_perfil(gy0, gy1, n)
    int = [[gy1, VIT_ZT - e], [gy0 + VIT_R, VIT_ZT - e]]
    n.downto(1) do |i|
      a = (Math::PI / 2) * i / n
      int << [gy0 + VIT_R - (VIT_R - e) * Math.cos(a),
              VIT_ZS + (VIT_R - e) * Math.sin(a)]
    end
    int << [gy0 + e, VIT_ZS] << [gy0 + e, VIT_ZD]
    suavizar(profile_x(ents, ext + int, gx0 + e, gx1 - e, vid, t,
                       "#{nombre} - cristal"))

    # Costados de cristal: el mismo perfil, macizo
    lado = ext + [[gy1, VIT_ZD]]
    suavizar(profile_x(ents, lado, gx0, gx0 + e, vid, t,
                       "#{nombre} - costado Oeste"))
    suavizar(profile_x(ents, lado, gx1 - e, gx1, vid, t,
                       "#{nombre} - costado Este"))

    # Trasera corredera, lado servicio
    box(ents, gx0 + e, gy1 - e, gx1 - e, gy1, VIT_ZD, VIT_ZT - e, vid, t,
        "#{nombre} - trasera")

    # Tres baldas escalonadas, cada una un poco más atrás y más alta
    3.times do |i|
      ya = gy0 + 0.04 + i * paso
      z  = VIT_ZD + 0.05 + i * 0.11
      box(ents, gx0 + 0.03, ya, gx1 - 0.03, ya + paso, z, z + 0.02, inox, t,
          "#{nombre} - balda #{i + 1}")
      nb = ((gx1 - gx0 - 0.12) / 0.20).floor
      nb.times do |j|
        cx = gx0 + 0.09 + (j + 0.5) * (gx1 - gx0 - 0.18) / nb
        box(ents, cx - 0.07, ya + 0.04, cx + 0.07, ya + paso - 0.04,
            z + 0.02, z + 0.08, mat['CN Terracota'], t,
            "#{nombre} - producto")
      end
    end
  end

  def self.equipos_barra(ents, mat, tag)
    t    = tag['23 Vitrinas y equipos']
    inox = mat['CN Acero inox']
    neg  = mat['CN Negro mate']
    z    = BAR_H + 0.06

    hu = huecos_vitrina
    vitrina(ents, mat, tag, hu[0][0], hu[0][1], 'Vitrina refrigerada')
    vitrina(ents, mat, tag, hu[1][0], hu[1][1], 'Vitrina caliente')

    # Maquina de cafe
    box(ents, 6.30, BAR_Y0 + 0.20, 7.05, BAR_Y1 - 0.12, z, z + 0.46, inox, t,
        'Maquina de cafe')
    box(ents, 6.30, BAR_Y0 + 0.20, 7.05, BAR_Y0 + 0.26, z + 0.46, z + 0.52,
        neg, t, 'Maquina de cafe - remate')
    2.times do |i|
      box(ents, 6.46 + i * 0.30, BAR_Y0 + 0.12, 6.60 + i * 0.30, BAR_Y0 + 0.22,
          z + 0.10, z + 0.24, neg, t, "Grupo de cafe #{i + 1}")
    end
    # Molinillo
    box(ents, 7.18, BAR_Y0 + 0.26, 7.36, BAR_Y0 + 0.46, z, z + 0.48, neg, t,
        'Molinillo')
    # Caja registradora
    box(ents, 7.55, BAR_Y0 + 0.30, 7.95, BAR_Y0 + 0.62, z, z + 0.10, neg, t,
        'Caja - base')
    box(ents, 7.60, BAR_Y0 + 0.34, 7.90, BAR_Y0 + 0.40, z + 0.10, z + 0.34,
        neg, t, 'Caja - pantalla')
  end

  # --------------------------------------------------------------------------
  #  ESTANTERIA DE FONDO  (contra la medianera norte, detrás de la barra)
  #  Mueble bajo liso de roble + rejilla de acero negro que forma cajas de
  #  distinto tamaño, con el fondo retroiluminado en cálido.
  # --------------------------------------------------------------------------

  EST_X0   = 4.20             # extremo oeste del mueble bajo
  EST_X1   = 7.60             # extremo este
  EST_PROF = 0.36             # fondo del mueble bajo
  EST_ENC  = 0.94             # cara superior de la encimera

  REJ_X0   = 4.30             # rejilla de cajas
  REJ_X1   = 7.50
  REJ_Z0   = 1.18
  REJ_Z1   = 2.48
  REJ_T    = 0.03             # escuadría del perfil
  REJ_PROF = 0.30             # fondo de las cajas

  # Montantes verticales: [x de la cara oeste, [[z0, z1], ...]]
  #   el de 6,70 se interrumpe en la fila central para dejar una caja ancha
  def self.rej_montantes
    [[4.30, [[REJ_Z0, REJ_Z1]]],
     [5.14, [[1.21, 2.45]]],
     [5.92, [[1.21, 2.45]]],
     [6.70, [[1.21, 1.64], [2.02, 2.45]]],
     [REJ_X1 - REJ_T, [[REJ_Z0, REJ_Z1]]]]
  end

  # Huecos entre montantes y alturas de travesaño presentes en cada hueco.
  #   en el primer hueco falta el travesaño de 1,61: es la caja alta
  def self.rej_huecos
    [[4.33, 5.14, [REJ_Z0, 2.02, 2.45]],
     [5.17, 5.92, [REJ_Z0, 1.61, 2.02, 2.45]],
     [5.95, 6.70, [REJ_Z0, 1.61, 2.02, 2.45]],
     [6.73, REJ_X1 - REJ_T, [REJ_Z0, 1.61, 2.02, 2.45]]]
  end

  # Cajas resultantes: [x0, x1, z0, z1]
  def self.rej_cajas
    [[4.33, 5.14, 1.21, 2.02], [4.33, 5.14, 2.05, 2.45],
     [5.17, 5.92, 1.21, 1.61], [5.17, 5.92, 1.64, 2.02],
     [5.17, 5.92, 2.05, 2.45],
     [5.95, 6.70, 1.21, 1.61], [6.73, 7.47, 1.21, 1.61],
     [5.95, 7.47, 1.64, 2.02],
     [5.95, 6.70, 2.05, 2.45], [6.73, 7.47, 2.05, 2.45]]
  end

  def self.estanteria(ents, mat, tag)
    t   = tag['24 Estanteria']
    rob = mat['CN Madera tablero']
    cla = mat['CN Madera clara']
    neg = mat['CN Negro mate']
    luz = mat['CN Luz calida']
    vid = mat['CN Vidrio']

    yb = by(62.4)                       # paramento del trasdosado norte
    yf = yb - EST_PROF                  # frente del mueble bajo

    # 1 · mueble bajo liso, sin molduras
    box(ents, EST_X0 + 0.05, yf + 0.05, EST_X1 - 0.05, yb, 0.0, 0.10, neg, t,
        'Estanteria - zocalo')
    box(ents, EST_X0, yf, EST_X1, yb, 0.10, 0.90, rob, t,
        'Estanteria - mueble bajo')
    4.times do |i|
      a = EST_X0 + 0.02 + i * (EST_X1 - EST_X0) / 4.0
      b = a + (EST_X1 - EST_X0) / 4.0 - 0.04
      box(ents, a, yf - 0.016, b, yf, 0.14, 0.86, cla, t,
          "Estanteria - puerta #{i + 1}")
    end
    box(ents, EST_X0 - 0.03, yf - 0.04, EST_X1 + 0.03, yb, 0.90, EST_ENC,
        cla, t, 'Estanteria - encimera')

    # 2 · fondo retroiluminado de la rejilla
    box(ents, REJ_X0, yb - REJ_T, REJ_X1, yb, REJ_Z0, REJ_Z1, luz, t,
        'Estanteria - fondo retroiluminado')
    # linea de luz bajo la rejilla
    box(ents, REJ_X0, yb - REJ_PROF, REJ_X1, yb - REJ_PROF + 0.03,
        REJ_Z0 - 0.03, REJ_Z0, luz, t, 'Estanteria - linea de luz')

    ry0 = yb - REJ_PROF
    ry1 = yb - REJ_T

    # 3 · montantes
    rej_montantes.each_with_index do |(x, tramos), i|
      tramos.each_with_index do |(z0, z1), j|
        box(ents, x, ry0, x + REJ_T, ry1, z0, z1, neg, t,
            "Estanteria - montante #{i + 1}.#{j + 1}")
      end
    end

    # 4 · travesaños, tramo a tramo entre montantes
    rej_huecos.each_with_index do |(a, b, alturas), i|
      alturas.each_with_index do |z, j|
        box(ents, a, ry0, b, ry1, z, z + REJ_T, neg, t,
            "Estanteria - travesano #{i + 1}.#{j + 1}")
      end
    end

    # 5 · botellas dentro de las cajas
    rej_cajas.each_with_index do |(a, b, z0, z1), i|
      nb = [((b - a) / 0.115).floor, 1].max
      hueco = z1 - z0 - 0.03
      nb.times do |j|
        next if (i + j) % 5 == 4
        cx = a + 0.055 + (j + 0.5) * (b - a - 0.11) / nb
        alto = [0.24 + 0.04 * ((i + j) % 3), hueco].min
        cyl(ents, cx, ry0 + 0.13, 0.037, z0, z0 + alto,
            (i + j).even? ? mat['CN Terracota'] : rob, t, 'Botella')
      end
    end

    # 6 · copas sobre la encimera
    5.times do |i|
      cx = EST_X0 + 0.55 + i * 0.62
      cyl(ents, cx, yf + 0.14, 0.014, EST_ENC, EST_ENC + 0.08, vid, t, 'Copa')
      cyl(ents, cx, yf + 0.14, 0.036, EST_ENC + 0.08, EST_ENC + 0.19, vid, t,
          'Copa')
    end
  end

  # --------------------------------------------------------------------------
  #  MESAS Y SILLAS
  # --------------------------------------------------------------------------

  # eje = :x  respaldo hacia el este/oeste   ·   eje = :y  hacia el norte/sur
  def self.silla(ents, mat, tag, cx, cy, eje, lado, azul = false)
    t = tag['26 Mesas y sillas']
    tela = azul ? mat['CN Tela azul'] : mat['CN Tela']
    g = ents.add_group
    e = g.entities
    a = 0.44
    box(e, cx - a / 2, cy - a / 2, cx + a / 2, cy + a / 2, 0.43, 0.50,
        tela, nil, 'Asiento')
    if eje == :y
      yr = cy + lado * (a / 2 - 0.06)
      box(e, cx - a / 2, yr, cx + a / 2, yr + lado * 0.06, 0.50, 0.84,
          tela, nil, 'Respaldo')
    else
      xr = cx + lado * (a / 2 - 0.06)
      box(e, xr, cy - a / 2, xr + lado * 0.06, cy + a / 2, 0.50, 0.84,
          tela, nil, 'Respaldo')
    end
    [[-1, -1], [1, -1], [-1, 1], [1, 1]].each do |sx, sy|
      px = cx + sx * (a / 2 - 0.05)
      py = cy + sy * (a / 2 - 0.05)
      box(e, px - 0.022, py - 0.022, px + 0.022, py + 0.022, 0.0, 0.44,
          mat['CN Madera clara'], nil, 'Pata')
    end
    finish(g, nil, t, 'Silla tapizada')
  end

  def self.mesa(ents, mat, tag, cx, cy, lado = 0.75)
    t = tag['26 Mesas y sillas']
    g = ents.add_group
    e = g.entities
    box(e, cx - lado / 2, cy - lado / 2, cx + lado / 2, cy + lado / 2,
        0.72, 0.76, mat['CN Madera tablero'], nil, 'Tablero')
    box(e, cx - 0.045, cy - 0.045, cx + 0.045, cy + 0.045, 0.03, 0.72,
        mat['CN Negro mate'], nil, 'Pie')
    box(e, cx - 0.22, cy - 0.22, cx + 0.22, cy + 0.22, 0.0, 0.03,
        mat['CN Negro mate'], nil, 'Base')
    finish(g, nil, t, 'Mesa 0,75 x 0,75')
  end

  # Centros de mesa y eje de las sillas.
  #
  # EL CUELLO DE FACHADA (la entrada) QUEDA VACÍO: no hay ninguna mesa, ni
  # banco, ni planta al sur de la línea del muro sur, y = 1,810 m.
  #
  # Sólo queda el bloque oeste, separado 0,55 m del muro oeste respecto a la
  # versión anterior: el respaldo más cercano queda a 0,91 m del paramento.
  # Separación entre ejes de columna 2,15 m -0,47 m libres entre respaldos-
  # y 1,50 / 1,45 m entre filas.
  def self.mesas_sala
    [[2.00, 2.65, :x], [2.00, 4.15, :x], [2.00, 5.60, :x],
     [4.15, 2.65, :x], [4.15, 4.15, :x], [4.15, 5.60, :x]]
  end

  def self.mobiliario_sala(ents, mat, tag)
    mesas_sala.each_with_index do |(cx, cy, eje), i|
      mesa(ents, mat, tag, cx, cy)
      if eje == :y
        silla(ents, mat, tag, cx, cy - 0.62, :y, -1, i.even?)
        silla(ents, mat, tag, cx, cy + 0.62, :y,  1, i.odd?)
      else
        silla(ents, mat, tag, cx - 0.62, cy, :x, -1, i.even?)
        silla(ents, mat, tag, cx + 0.62, cy, :x,  1, i.odd?)
      end
    end
  end

  # --------------------------------------------------------------------------
  #  ILUMINACION
  # --------------------------------------------------------------------------

  def self.lampara(ents, mat, tag, cx, cy, z_techo, z_lampara, r = 0.15)
    t = tag['27 Iluminacion']
    g = ents.add_group
    e = g.entities
    cyl(e, cx, cy, 0.012, z_lampara + 0.16, z_techo, mat['CN Negro mate'],
        nil, 'Cable')
    cyl(e, cx, cy, r, z_lampara + 0.02, z_lampara + 0.17, mat['CN Opal'],
        nil, 'Pantalla')
    cyl(e, cx, cy, r, z_lampara, z_lampara + 0.02, mat['CN Laton'],
        nil, 'Aro')
    cyl(e, cx, cy, r * 0.5, z_lampara - 0.04, z_lampara,
        mat['CN Opal'], nil, 'Foco')
    finish(g, nil, t, 'Lampara colgante')
  end

  def self.iluminacion(ents, mat, tag)
    t = tag['27 Iluminacion']

    # Colgantes sobre la barra
    [4.15, 5.45, 6.75, 7.75].each do |cx|
      lampara(ents, mat, tag, cx, 6.99, Z_FORJ_INF, 2.02, 0.17)
    end

    # Un colgante por mesa; el techo depende de si está bajo el forjado
    y_forj = ay(336.2)
    mesas_sala.each do |cx, cy, _eje|
      techo = cy > y_forj ? Z_FORJ_INF : H_TOT
      lampara(ents, mat, tag, cx, cy, techo, cy > y_forj ? 1.98 : 2.25, 0.14)
    end

    # Dos colgantes altos en el cuello de fachada. Es lo único que hay en la
    # entrada: cuelgan a 2,90 m y dejan el suelo completamente libre.
    [[7.30, 0.95], [8.90, 0.95]].each do |cx, cy|
      lampara(ents, mat, tag, cx, cy, H_TOT, 2.90, 0.21)
    end

    # Empotrados en el intradós del forjado
    [4.60, 5.90, 7.20, 8.50].each do |cy|
      [1.10, 2.60, 4.10, 8.60].each do |cx|
        next if cx > 8.4 && cy > 3.9 && cy < 7.8      # hueco de escalera
        cyl(ents, cx, cy, 0.055, Z_FORJ_INF - 0.02, Z_FORJ_INF,
            mat['CN Tela'], t, 'Empotrado de techo')
      end
    end

    # Apliques en el muro oeste
    [2.30, 3.30, 6.20].each do |cy|
      box(ents, ax(152.5), cy - 0.09, ax(152.5) + 0.12, cy + 0.09,
          1.92, 2.10, mat['CN Laton'], t, 'Aplique de pared')
    end
  end

  # --------------------------------------------------------------------------
  #  DECORACION
  # --------------------------------------------------------------------------

  def self.planta(ents, mat, tag, cx, cy, alto = 1.25, r = 0.24)
    t = tag['28 Decoracion']
    g = ents.add_group
    e = g.entities
    cyl(e, cx, cy, r, 0.0, 0.34, mat['CN Terracota'], nil, 'Maceta')
    cyl(e, cx, cy, 0.035, 0.34, 0.34 + alto * 0.45, mat['CN Madera tablero'],
        nil, 'Tronco')
    cyl(e, cx, cy, r * 1.5, 0.34 + alto * 0.40, 0.34 + alto, mat['CN Planta'],
        nil, 'Copa')
    finish(g, nil, t, 'Planta')
  end

  def self.decoracion(ents, mat, tag)
    t = tag['28 Decoracion']

    # Plantas. Ninguna en el cuello de fachada: la entrada queda despejada.
    planta(ents, mat, tag, 0.70, 2.60, 1.15)
    planta(ents, mat, tag, 0.70, 6.30, 1.30)
    planta(ents, mat, tag, 6.60, 2.60, 1.25)
    planta(ents, mat, tag, 6.90, 5.90, 1.20)

    # Cuadros en el muro oeste
    [2.90, 3.75, 5.90].each_with_index do |cy, i|
      box(ents, ax(152.5), cy - 0.26, ax(152.5) + 0.035, cy + 0.26,
          1.35, 1.95, mat['CN Madera tablero'], t, "Cuadro Oeste #{i + 1}")
      box(ents, ax(152.5) + 0.035, cy - 0.22, ax(152.5) + 0.045, cy + 0.22,
          1.40, 1.90, mat['CN Tela'], t, "Cuadro Oeste #{i + 1} - lamina")
    end

    # Pizarra de carta, al este de la estantería
    box(ents, 7.62, by(62.4) - 0.05, 9.32, by(62.4), 1.45, 2.25,
        mat['CN Negro mate'], t, 'Pizarra de carta')
    box(ents, 7.57, by(62.4) - 0.07, 9.37, by(62.4) - 0.05, 1.40, 2.30,
        mat['CN Madera tablero'], t, 'Pizarra - marco')
  end

  # --------------------------------------------------------------------------
  #  FRENTE DEL ALTILLO Y ACABADO DE LA ESCALERA
  # --------------------------------------------------------------------------

  def self.frente_altillo(ents, mat, tag)
    t   = tag['28 Decoracion']
    bl  = mat['CN Blanco roto']
    az  = mat['CN Azul Napoli']
    ys  = ay(336.2)            # borde sur del forjado
    xo  = ax(275.0)            # borde oeste del forjado
    xe  = ax(637.8)            # borde de la caja de escalera
    z0  = 2.48

    box(ents, xo, ys - 0.05, xe, ys, z0, H_PA, bl, t, 'Frente de altillo - Sur')
    # El frente oeste se parte a ambos lados de la viga descolgada
    box(ents, xo - 0.05, ys, xo, ay(285.8), z0, H_PA, bl, t,
        'Frente de altillo - Oeste (tramo Sur)')
    box(ents, xo - 0.05, ay(271.6), xo, ay(133.8), z0, H_PA, bl, t,
        'Frente de altillo - Oeste (tramo Norte)')
    # Banda de rótulo CAFÉ NAPOLI
    box(ents, 4.00, ys - 0.062, 7.00, ys - 0.05, 2.58, 2.90, az, t,
        'Banda de rotulo del altillo')
  end

  def self.acabado_escalera(ents, mat, tag)
    t = tag['08 Escalera']
    m = mat['CN Madera clara']
    y_pie, _y_alto, huella, tabica = esc_datos
    xa = ax(637.8)
    (1..16).each do |i|
      ya = y_pie + (i - 1) * huella
      yb = ya + huella
      # los peldaños 5 a 7 se acortan por el machón de la medianera este
      xb = (5..7).include?(i) ? ax(687.6) : ax(699.0)
      box(ents, xa, ya, xb, yb, i * tabica, i * tabica + 0.025, m, t,
          "Escalera - huella de madera #{i}")
    end
    box(ents, ax(628.0), ay(356.6), xa, ay(341.9), tabica, tabica + 0.025,
        m, t, 'Escalera - huella de arranque')
  end

  # --------------------------------------------------------------------------
  #  ENCUADRE
  # --------------------------------------------------------------------------

  def self.encuadre(model)
    view = model.active_view
    view.camera = Sketchup::Camera.new(p3(-7.0, -8.0, 8.5),
                                       p3(5.0, 4.6, 1.4),
                                       Geom::Vector3d.new(0, 0, 1))
    view.zoom_extents
  rescue StandardError
    nil
  end

  # ==========================================================================
  #  MENÚ
  # ==========================================================================

  unless defined?(@menu_cargado)
    @menu_cargado = true
    begin
      menu = UI.menu('Plugins').add_submenu('Café Napoli')
      menu.add_item('Generar modelo 3D') { CafeNapoliMalaga.build! }
    rescue StandardError => e
      puts "Café Napoli: no se pudo crear el menú (#{e.message})"
    end
  end

end

# Al cargar desde la Consola Ruby se genera el modelo. Si el archivo vive en la
# carpeta Plugins, sólo se instala el menú.
begin
  plugins_dir = Sketchup.find_support_file('Plugins').to_s.downcase
  here        = File.dirname(File.expand_path(__FILE__)).downcase
  CafeNapoliMalaga.build! unless !plugins_dir.empty? && here.start_with?(plugins_dir)
rescue StandardError => e
  puts "Café Napoli: #{e.message}"
  puts e.backtrace.first(5)
end
