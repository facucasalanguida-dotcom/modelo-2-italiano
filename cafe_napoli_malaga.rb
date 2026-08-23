# encoding: UTF-8
#
# ============================================================================
#  CAFÉ NAPOLI — MÁLAGA
#  Modelo 3D ESTRUCTURAL para SketchUp  ·  planta baja + planta alta
# ============================================================================
#
#  Contiene ÚNICAMENTE la caja arquitectónica: solera, muros, pilares,
#  machones, forjado, viga, particiones, huecos de paso, escalera,
#  barandillas, escaparate y bajante.
#  NO contiene mobiliario ni equipamiento de ningún tipo.
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
    'CN Muro'        => [238, 234, 227, 255],
    'CN Medianera'   => [221, 216, 208, 255],
    'CN Hormigon'    => [199, 196, 191, 255],
    'CN Tabique'     => [244, 242, 238, 255],
    'CN Vidrio'      => [186, 212, 228,  70],
    'CN Carpinteria' => [ 62,  64,  66, 255],
    'CN Rotulo'      => [ 62, 107, 153, 255],
    'CN Instalacion' => [170, 172, 174, 255]
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
    '11 Instalaciones'
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
    model.start_operation('Generar Café Napoli Málaga (estructura)', true)
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
      instalaciones(ents, mat, tag)
      cubierta(ents, mat, tag)

      encuadre(model)
    ensure
      model.commit_operation
    end
    informe
  end

  def self.informe
    txt = <<~TXT
      CAFÉ NAPOLI — MÁLAGA · modelo estructural generado

        Huella exterior ......... 81,73 m²
        Superficie útil PB ...... 74,20 m²
        Forjado planta alta ..... 33,74 m²
        Ancho total ............. 10,040 m   Fondo total ..... 9,156 m
        Planta alta ............. +3,00 m    Cubierta ........ +5,50 m
        Escalera ................ 16 huellas de 0,26 · 17 tabicas de 0,1765

      Sin mobiliario ni equipamiento: sólo solera, muros, pilares, machones,
      forjado, viga, particiones, huecos, escalera, barandillas, escaparate
      y bajante.
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

    # Muro sur del cuerpo posterior  (e = 0,249)
    box(ents, ax(167.2), ay(456.9), ax(477.3), ay(471.0), 0.0, H_TOT, mu, t,
        'Muro Sur')

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

    # Viga descolgada del machón oeste al borde del forjado  (e = 0,25)
    box(ents, ax(173.5), ay(271.6), ax(275.0), ay(285.8), Z_VIGA_INF, H_PA, h, t,
        'Viga descolgada')
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
          mat['CN Hormigon'], tag['04 Forjado planta alta'],
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

  def self.particiones_pb(ents, mat, tag)
    t = tag['07 Particiones planta baja']
    m = mat['CN Tabique']

    box(ents, bx(349.2), by(62.4), bx(354.0), by(249.9), 0.0, Z_FORJ_INF, m, t,
        'PB Tabique Este de la cocina')

    # Tabique sur con paso de 0,80 m alineado con el pasillo de servicio
    box(ents, bx(117.8), by(249.9), bx(181.6), by(254.6), 0.0, Z_FORJ_INF, m, t,
        'PB Tabique Sur cocina - tramo Oeste')
    box(ents, bx(257.2), by(249.9), bx(354.0), by(254.6), 0.0, Z_FORJ_INF, m, t,
        'PB Tabique Sur cocina - tramo Este')
    box(ents, bx(181.6), by(249.9), bx(257.2), by(254.6),
        H_PUERTA, Z_FORJ_INF, m, t, 'PB Dintel paso cocina (hueco 0,80 m)')
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

  # --------------------------------------------------------------------------
  #  10. INSTALACIONES
  # --------------------------------------------------------------------------

  def self.instalaciones(ents, mat, tag)
    # Bajante grafiada en el rincón noroeste del vacío (Ø exterior 0,20)
    cyl(ents, ax(264.5), ay(57.6), 0.1005, 0.0, H_TOT,
        mat['CN Instalacion'], tag['11 Instalaciones'], 'Bajante (D 0,20)')
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
