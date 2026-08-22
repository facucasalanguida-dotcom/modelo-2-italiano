# encoding: UTF-8
#
# ============================================================================
#  CAFÉ NAPOLI — MÁLAGA
#  Generador de modelo 3D para SketchUp (planta baja + planta alta)
# ============================================================================
#
#  USO
#  ---
#  1) Abre SketchUp con un modelo nuevo (en metros, preferiblemente).
#  2) Ventana > Consola Ruby  (Window > Ruby Console)
#  3) Escribe:      load "C:/ruta/al/cafe_napoli_malaga.rb"
#     (en Mac:      load "/Users/tu_usuario/.../cafe_napoli_malaga.rb")
#  4) El modelo se genera solo. Para volver a generarlo:
#         CafeNapoliMalaga.build!
#
#  También se instala un menú:  Extensiones > Café Napoli > Generar modelo 3D
#
#  ORIGEN DE LAS MEDIDAS
#  ---------------------
#  Toda la geometría se deriva de los dos planos entregados, midiendo
#  directamente los vectores del PDF y convirtiéndolos a metros:
#
#    * planimetria_2.pdf  (PLANTA ALTA) ...... escala 1:50  -> 56,6929 pt/m
#    * PROPOSTA_MALAGA.pdf (PLANTA BAJA) ..... escala 1:30  -> 94,4882 pt/m
#
#  Verificaciones de escala (coinciden con las cotas rotuladas del plano):
#    - ASEO        medido 3,92 m²   rotulado 3,90 m²
#    - ALMACÉN-2   medido 2,59 m²   rotulado 2,60 m²
#    - Huella de peldaño = 0,260 m  (17 tabicas de 3,00/17 = 0,1765 m)
#    - Barra "272" -> 2,721 m ;  "188" -> 1,880 m ;  "134,5" -> 1,345 m
#
#  Los dos planos encajan entre sí al milímetro: el pilar de fachada
#  (X 1,300–1,901 / Y 7,048–7,596) y el machón del muro oeste
#  (Y 3,799–4,397) aparecen idénticos en ambos documentos.
#
#  SISTEMA DE COORDENADAS DEL MODELO (metros)
#  ------------------------------------------
#    X = 0  cara exterior del muro OESTE      X = 10,040  medianera ESTE
#    Y = 0  punto más al sur (pilar fachada)  Y =  9,156  medianera NORTE
#    Z = 0  nivel de planta baja              Z =  3,000  nivel planta alta (+3.00)
#
#  COTAS NO GRAFIADAS EN LOS PLANOS
#  --------------------------------
#  Los planos sólo acotan el nivel +3.00. El resto de alturas está agrupado
#  en el bloque "ALTURAS" de más abajo: basta cambiar el número y volver a
#  ejecutar CafeNapoliMalaga.build!
#
#  Dos decisiones que conviene conocer (detalle en README.md):
#    * La propuesta dibuja el recinto de cocina CERRADO, sin ningún hueco.
#      Se ha abierto un paso de 0,80 m en el tabique sur, en la prolongación
#      exacta del pasillo de servicio. Se mueve en el método cocina().
#    * Los planos no grafían mesas ni sillas. El mobiliario de sala es una
#      propuesta y va en su propia etiqueta, para poder ocultarlo o borrarlo
#      sin tocar el resto del modelo.
#
# ============================================================================

require 'sketchup.rb'

module CafeNapoliMalaga

  # ==========================================================================
  #  ESCALAS Y CONVERSIÓN PLANO -> MODELO
  # ==========================================================================

  M_TO_IN = 39.3700787401575       # SketchUp trabaja internamente en pulgadas

  SP = 56.692913385826770          # pt por metro — planimetría  (1:50)
  SB = 94.488188976377950          # pt por metro — propuesta    (1:30)

  PA_OX = 138.3                    # pt X  esquina NO exterior (planimetría)
  PA_OY =  40.4                    # pt Y  cara exterior medianera norte
  PA_YS = 559.5                    # pt Y  punto más al sur del solar

  PB_AX = 117.8                    # pt X propuesta  <->  152.5 planimetría
  PB_AY =  52.9                    # pt Y propuesta  <->   48.8 planimetría

  YMAX = (PA_YS - PA_OY) / SP      # 9,1564 m  (fondo total del local)

  # planimetría (pt) -> modelo (m)
  def self.ax(v) ; (v - PA_OX) / SP ; end
  def self.ay(v) ; YMAX - (v - PA_OY) / SP ; end
  # propuesta (pt) -> modelo (m), anclada a la planimetría
  def self.bx(v) ; ax(152.5) + (v - PB_AX) / SB ; end
  def self.by(v) ; ay(48.8)  - (v - PB_AY) / SB ; end

  # ==========================================================================
  #  ALTURAS  (editar aquí si se dispone de la sección real)
  # ==========================================================================

  H_PA        = 3.00     # nivel planta alta  <-- COTA DEL PLANO (+3.00)
  T_FORJADO   = 0.30     # canto del forjado de planta alta
  Z_FORJ_INF  = H_PA - T_FORJADO          # 2,70 intradós
  H_LIBRE_PA  = 2.50     # altura libre en planta alta
  H_TOTAL     = H_PA + H_LIBRE_PA         # 5,50 cara inferior de cubierta
  T_CUBIERTA  = 0.30
  T_SOLERA    = 0.20

  H_PUERTA    = 2.10     # hueco de paso
  H_BARANDA   = 1.00     # antepecho de vidrio
  H_MOSTRADOR = 0.90     # altura de trabajo de barras y cocina
  T_ENCIMERA  = 0.04
  H_VITRINA   = 1.90     # "VETRINA EXPO ALTA"
  H_ESCAPARATE= 3.00     # altura del acristalamiento de fachada
  Z_VIGA_INF  = 2.60     # intradós de la viga descolgada del plano

  # Escalera: 16 huellas dibujadas entre y=356,6 y y=120,8 pt
  N_TABICAS   = 17
  T_ZANCA     = 0.20     # canto vertical de la losa de escalera

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

  # Prisma vertical a partir de un polígono en planta [[x,y], ...]
  def self.prism(ents, poly, z0, z1, mat = nil, tag = nil, name = nil)
    return nil if (z1 - z0).abs < 1e-6
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
    g = ents.add_group
    f = g.entities.add_face(prof.map { |q| p3(xa, q[0], q[1]) })
    if f.nil?
      g.erase!
      return nil
    end
    f.reverse! if f.normal.x < 0
    f.pushpull((xb - xa) * M_TO_IN)
    finish(g, mat, tag, name)
  end

  # Cilindro vertical
  def self.cyl(ents, cx, cy, r, z0, z1, mat = nil, tag = nil, name = nil)
    za, zb = [z0, z1].minmax
    g = ents.add_group
    c = g.entities.add_circle(p3(cx, cy, za), Geom::Vector3d.new(0, 0, 1),
                              r * M_TO_IN, 36)
    f = g.entities.add_face(c)
    if f.nil?
      g.erase!
      return nil
    end
    f.reverse! if f.normal.z < 0
    f.pushpull((zb - za) * M_TO_IN)
    finish(g, mat, tag, name)
  end

  # ==========================================================================
  #  MATERIALES Y ETIQUETAS
  # ==========================================================================

  PALETA = {
    'CN Muro blanco'      => [244, 241, 236, 255],
    'CN Medianera'        => [225, 220, 212, 255],
    'CN Azul Napoli'      => [ 62, 107, 153, 255],
    'CN Madera roble'     => [214, 183, 142, 255],
    'CN Madera listones'  => [225, 199, 160, 255],
    'CN Pavimento madera' => [223, 200, 168, 255],
    'CN Piedra encimera'  => [242, 240, 234, 255],
    'CN Acero inox'       => [200, 205, 210, 255],
    'CN Vidrio'           => [190, 214, 228,  70],
    'CN Vidrio vitrina'   => [205, 226, 236,  90],
    'CN Drop-in frio'     => [125, 226, 232, 220],
    'CN Hormigon'         => [178, 176, 172, 255],
    'CN Acera'            => [199, 196, 190, 255],
    'CN Tapiceria'        => [231, 226, 216, 255],
    'CN Negro mate'       => [ 58,  58,  58, 255],
    'CN Sanitario'        => [250, 250, 250, 255]
  }

  TAGS = [
    '00 Terreno y acera',
    '01 Solera y pavimentos',
    '02 Muros y pilares',
    '03 Forjado planta alta',
    '04 Cubierta',
    '05 Particiones planta alta',
    '06 Escalera',
    '07 Barandillas vidrio',
    '08 Fachada - escaparate',
    '09 Cocina - equipamiento',
    '10 Barra y mostrador',
    '11 Sanitarios',
    '12 Mobiliario sala (propuesta)'
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
    tags['04 Cubierta'].visible = false
    tags
  end

  # ==========================================================================
  #  CONSTRUCCIÓN DEL MODELO
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
        # algunas versiones no exponen estas opciones; no es crítico
      end

      mat  = setup_materials(model)
      tag  = setup_tags(model)
      root = model.active_entities

      shell(root, mat, tag)
      forjado_y_cubierta(root, mat, tag)
      particiones_planta_alta(root, mat, tag)
      escalera(root, mat, tag)
      barandillas(root, mat, tag)
      fachada(root, mat, tag)
      cocina(root, mat, tag)
      barra_y_mostrador(root, mat, tag)
      sanitarios(root, mat, tag)
      mobiliario_sala(root, mat, tag)

      encuadre(model)
    ensure
      model.commit_operation
    end

    msg = "Café Napoli — Málaga: modelo generado.\n\n" \
          "Superficie PB ~74,7 m²   ·   Planta alta +3.00 m\n" \
          "ZONA DE PASO-ALMACÉN-1 25,05 m² · ASEO 3,90 m² · " \
          "ALMACÉN-2 2,60 m² · ESCALERA 3,76 m²"
    puts msg
    msg
  end

  # --------------------------------------------------------------------------
  #  1. ENVOLVENTE: solera, muros perimetrales, pilares
  # --------------------------------------------------------------------------

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

  def self.perimetro_interior
    [[ax(152.5), ay( 48.8)],
     [ax(699.0), ay( 48.8)],
     [ax(699.0), ay(478.5)],
     [ax(688.8), ay(478.5)],
     [ax(688.8), ay(538.0)],
     [ax(491.5), ay(538.0)],
     [ax(491.5), ay(505.1)],
     [ax(477.3), ay(505.1)],
     [ax(477.3), ay(456.9)],
     [ax(246.1), ay(456.9)],
     [ax(246.1), ay(440.0)],
     [ax(212.0), ay(440.0)],
     [ax(212.0), ay(456.9)],
     [ax(167.2), ay(456.9)],
     [ax(167.2), ay(445.6)],
     [ax(152.5), ay(445.6)],
     [ax(152.5), ay(289.7)],
     [ax(173.5), ay(289.7)],
     [ax(173.5), ay(255.8)],
     [ax(152.5), ay(255.8)]]
  end

  def self.shell(ents, mat, tag)
    t02 = tag['02 Muros y pilares']
    t01 = tag['01 Solera y pavimentos']
    t00 = tag['00 Terreno y acera']

    # --- solera y pavimento ------------------------------------------------
    prism(ents, perimetro_exterior, -T_SOLERA, 0.0,
          mat['CN Hormigon'], t01, 'Solera PB')
    prism(ents, perimetro_interior, 0.0, 0.015,
          mat['CN Pavimento madera'], t01, 'Pavimento PB (madera)')

    # --- acera / terreno exterior (contexto) -------------------------------
    box(ents, ax(463.2) - 2.20, ay(559.5) - 2.60, ax(707.5) + 0.60, ay(538.0),
        -0.02, 0.0, mat['CN Acera'], t00, 'Acera')

    # --- muros perimetrales -------------------------------------------------
    # Medianera norte (e = 0,148 m)
    box(ents, ax(138.3), ay(40.4), ax(707.5), ay(48.8),
        0.0, H_TOTAL, mat['CN Medianera'], t02, 'Medianera Norte')

    # Muro oeste (e = 0,250 m) + machón
    box(ents, ax(138.3), ay(48.8), ax(152.5), ay(445.6),
        0.0, H_TOTAL, mat['CN Muro blanco'], t02, 'Muro Oeste')
    box(ents, ax(152.5), ay(255.8), ax(173.5), ay(289.7),
        0.0, H_TOTAL, mat['CN Muro blanco'], t02, 'Machon muro Oeste')
    box(ents, ax(138.3), ay(445.6), ax(167.2), ay(471.0),
        0.0, H_TOTAL, mat['CN Muro blanco'], t02, 'Muro Oeste - esquina SO')

    # Muro sur del cuerpo posterior (e = 0,249 m) + pilastra
    box(ents, ax(167.2), ay(456.9), ax(477.3), ay(471.0),
        0.0, H_TOTAL, mat['CN Muro blanco'], t02, 'Muro Sur')
    box(ents, ax(212.0), ay(440.0), ax(246.1), ay(456.9),
        0.0, H_TOTAL, mat['CN Muro blanco'], t02, 'Pilastra muro Sur')

    # Muro oeste del cuello de fachada + pilar de esquina
    box(ents, ax(463.2), ay(471.0), ax(477.3), ay(505.1),
        0.0, H_TOTAL, mat['CN Muro blanco'], t02, 'Muro Oeste cuello')
    box(ents, ax(463.2), ay(505.1), ax(491.5), ay(559.5),
        0.0, H_TOTAL, mat['CN Hormigon'], t02, 'Pilar de fachada')

    # Medianera este (e = 0,150 m ; 0,330 m en el cuello)
    box(ents, ax(699.0), ay(48.8), ax(707.5), ay(478.5),
        0.0, H_TOTAL, mat['CN Medianera'], t02, 'Medianera Este')
    box(ents, ax(688.8), ay(478.5), ax(707.5), ay(540.8),
        0.0, H_TOTAL, mat['CN Medianera'], t02, 'Medianera Este - cuello')

    # Trasdosado de 0,10 m bajo el forjado (grafiado en la propuesta)
    box(ents, bx(326.5), ay(48.8), ax(699.0), by(62.4),
        0.0, Z_FORJ_INF, mat['CN Muro blanco'], t02, 'Trasdosado Norte PB')

    # Viga descolgada del plano (0,25 m de ancho)
    box(ents, ax(173.5), ay(271.6), ax(275.0), ay(285.8),
        Z_VIGA_INF, H_PA, mat['CN Hormigon'], t02, 'Viga descolgada')
  end

  # --------------------------------------------------------------------------
  #  2. FORJADO DE PLANTA ALTA Y CUBIERTA
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

  def self.forjado_y_cubierta(ents, mat, tag)
    prism(ents, planta_forjado, Z_FORJ_INF, H_PA,
          mat['CN Hormigon'], tag['03 Forjado planta alta'], 'Forjado planta alta')
    prism(ents, planta_forjado, H_PA, H_PA + 0.015,
          mat['CN Pavimento madera'], tag['01 Solera y pavimentos'],
          'Pavimento planta alta')
    prism(ents, perimetro_exterior, H_TOTAL, H_TOTAL + T_CUBIERTA,
          mat['CN Hormigon'], tag['04 Cubierta'], 'Forjado de cubierta')
  end

  # --------------------------------------------------------------------------
  #  3. PARTICIONES DE PLANTA ALTA  (ASEO / ALMACÉN-2)
  # --------------------------------------------------------------------------

  def self.particiones_planta_alta(ents, mat, tag)
    t = tag['05 Particiones planta alta']
    m = mat['CN Muro blanco']
    z0 = H_PA
    z1 = H_TOTAL
    zd = H_PA + H_PUERTA          # arranque de dinteles

    # Cerramiento oeste del bloque ASEO
    box(ents, ax(277.8), ay(48.8), ax(283.4), ay(133.8), z0, z1, m, t,
        'PA Tabique Oeste aseo')

    # Tabique sur del bloque ASEO / ALMACÉN-2, con hueco de puerta
    box(ents, ax(283.4), ay(128.2), ax(313.4), ay(133.8), z0, z1, m, t,
        'PA Tabique Sur (tramo O)')
    box(ents, ax(356.5), ay(128.2), ax(564.1), ay(133.8), z0, z1, m, t,
        'PA Tabique Sur (tramo E)')
    box(ents, ax(313.4), ay(128.2), ax(356.5), ay(133.8), zd, z1, m, t,
        'PA Dintel puerta aseo (0,76 m)')

    # Tabique del inodoro
    box(ents, ax(391.2), ay(94.2), ax(396.8), ay(128.2), z0, z1, m, t,
        'PA Tabique inodoro')
    box(ents, ax(391.2), ay(48.8), ax(396.8), ay(94.2), zd, z1, m, t,
        'PA Dintel puerta inodoro (0,80 m)')

    # Separación inodoro / ALMACÉN-2
    box(ents, ax(447.8), ay(48.8), ax(453.4), ay(128.2), z0, z1, m, t,
        'PA Tabique aseo-almacen')

    # Cerramiento este de ALMACÉN-2, con hueco de puerta
    box(ents, ax(558.3), ay(101.9), ax(564.1), ay(128.2), z0, z1, m, t,
        'PA Tabique Este almacen')
    box(ents, ax(558.3), ay(48.8), ax(564.1), ay(101.9), zd, z1, m, t,
        'PA Dintel puerta almacen (0,94 m)')
  end

  # --------------------------------------------------------------------------
  #  4. ESCALERA  (16 huellas de 0,26 m · 17 tabicas de 3,00/17 = 0,1765 m)
  # --------------------------------------------------------------------------

  def self.esc_datos
    y_pie  = ay(356.6)          # arranque en planta baja
    y_alto = ay(120.8)          # llegada a +3.00
    huella = (y_alto - y_pie) / 16.0
    tabica = H_PA / N_TABICAS
    [y_pie, y_alto, huella, tabica]
  end

  def self.esc_cota(y)          # cota de la escalera a una Y dada
    y_pie, _y_alto, huella, tabica = esc_datos
    z = ((y - y_pie) / huella) * tabica
    z < 0.0 ? 0.0 : z
  end

  def self.escalera(ents, mat, tag)
    t = tag['06 Escalera']
    y_pie, y_alto, huella, tabica = esc_datos

    prof = [[y_pie, 0.0]]
    (1..N_TABICAS).each do |i|
      y_r = y_pie + (i - 1) * huella
      prof << [y_r, i * tabica]                    # tabica
      prof << [y_r + huella, i * tabica] if i <= 16 # huella
    end
    prof << [y_alto, H_PA - T_ZANCA]
    prof << [y_pie + T_ZANCA * (16 * huella) / H_PA, 0.0]

    profile_x(ents, prof, ax(637.8), ax(699.0),
              mat['CN Hormigon'], t, 'Escalera - 17 tabicas')

    # primer peldaño ensanchado, tal como aparece grafiado
    box(ents, ax(628.0), ay(356.6), ax(637.8), ay(341.9),
        0.0, tabica, mat['CN Hormigon'], t, 'Escalera - peldano de arranque')
  end

  # --------------------------------------------------------------------------
  #  5. BARANDILLAS DE VIDRIO  (e = 0,05 m, como en el plano)
  # --------------------------------------------------------------------------

  def self.barandillas(ents, mat, tag)
    t = tag['07 Barandillas vidrio']
    v = mat['CN Vidrio']

    # borde oeste y sur del hueco (VACÍO SOBRE PLANTA BAJA)
    box(ents, ax(275.0), ay(133.8), ax(277.8), ay(333.4),
        H_PA, H_PA + H_BARANDA, v, t, 'Barandilla hueco - Oeste')
    box(ents, ax(275.0), ay(333.4), ax(634.9), ay(336.2),
        H_PA, H_PA + H_BARANDA, v, t, 'Barandilla hueco - Sur')

    # borde de la caja de escalera: base inclinada siguiendo los peldaños
    y_pie, y_alto, _h, _tb = esc_datos
    y_forj = ay(336.2)
    z_forj = esc_cota(y_forj)

    profile_x(ents, [[y_forj, z_forj], [y_alto, H_PA],
                     [y_alto, H_PA + H_BARANDA], [y_forj, H_PA + H_BARANDA]],
              ax(634.9), ax(637.8), v, t, 'Barandilla caja de escalera')

    profile_x(ents, [[y_pie, 0.0], [y_forj, z_forj],
                     [y_forj, z_forj + H_BARANDA], [y_pie, H_BARANDA]],
              ax(634.9), ax(637.8), v, t, 'Barandilla escalera - tramo bajo')
  end

  # --------------------------------------------------------------------------
  #  6. FACHADA — ESCAPARATE
  # --------------------------------------------------------------------------

  def self.fachada(ents, mat, tag)
    t   = tag['08 Fachada - escaparate']
    y0  = ay(540.8)
    y1  = ay(538.0)
    xa  = ax(491.5)
    xm0 = ax(571.4)      # montante grafiado en el plano
    xm1 = ax(574.3)
    xb  = ax(688.8)

    # vidrio de los dos paños (entre umbral y cabecero)
    box(ents, xa,  y0, xm0, y1, 0.06, H_ESCAPARATE - 0.08,
        mat['CN Vidrio'], t, 'Escaparate - pano Oeste (acceso)')
    box(ents, xm1, y0, xb,  y1, 0.06, H_ESCAPARATE - 0.08,
        mat['CN Vidrio'], t, 'Escaparate - pano Este')

    # montante y cercos
    box(ents, xm0, y0, xm1, y1, 0.0, H_ESCAPARATE,
        mat['CN Negro mate'], t, 'Escaparate - montante')
    box(ents, xa,  y0, xb,  y1, 0.0, 0.06,
        mat['CN Negro mate'], t, 'Escaparate - umbral')
    box(ents, xa,  y0, xb,  y1, H_ESCAPARATE - 0.08, H_ESCAPARATE,
        mat['CN Negro mate'], t, 'Escaparate - cabecero')

    # banda de rótulo y peto sobre el escaparate
    box(ents, xa, y0, xb, y1, H_ESCAPARATE, H_ESCAPARATE + 0.55,
        mat['CN Azul Napoli'], t, 'Banda de rotulo')
    box(ents, xa, y0, xb, y1, H_ESCAPARATE + 0.55, H_TOTAL,
        mat['CN Muro blanco'], t, 'Peto sobre escaparate')
  end

  # --------------------------------------------------------------------------
  #  7. COCINA  (tabiques de 5 cm y equipamiento de la propuesta)
  # --------------------------------------------------------------------------

  def self.cocina(ents, mat, tag)
    t  = tag['09 Cocina - equipamiento']
    t2 = tag['02 Muros y pilares']
    m  = mat['CN Muro blanco']

    # Tabique este de la cocina (altura hasta el intradós del forjado)
    box(ents, bx(349.2), by(62.4), bx(354.0), by(254.6),
        0.0, Z_FORJ_INF, m, t2, 'Cocina - tabique Este')

    # Tabique sur, con paso de 0,80 m alineado con el pasillo de servicio
    box(ents, bx(117.8), by(249.9), bx(181.6), by(254.6),
        0.0, Z_FORJ_INF, m, t2, 'Cocina - tabique Sur (tramo O)')
    box(ents, bx(257.2), by(249.9), bx(354.0), by(254.6),
        0.0, Z_FORJ_INF, m, t2, 'Cocina - tabique Sur (tramo E)')
    box(ents, bx(181.6), by(249.9), bx(257.2), by(254.6),
        H_PUERTA, Z_FORJ_INF, m, t2, 'Cocina - dintel de paso (0,80 m)')

    # Equipamiento grafiado en la propuesta (medidas exactas del plano)
    box(ents, bx(122.5), by(57.7), bx(160.0), by(132.6),
        0.0, H_MOSTRADOR, mat['CN Acero inox'], t,
        'Mueble MICROONDAS / TOSTADORA (0,40 x 0,80)')
    box(ents, bx(126.0), by(62.0), bx(157.0), by(100.0),
        H_MOSTRADOR, H_MOSTRADOR + 0.30, mat['CN Negro mate'], t, 'Microondas')
    box(ents, bx(126.0), by(104.0), bx(157.0), by(128.0),
        H_MOSTRADOR, H_MOSTRADOR + 0.22, mat['CN Acero inox'], t, 'Tostadora')

    box(ents, bx(183.4), by(54.1), bx(221.5), by(120.2),
        0.0, H_MOSTRADOR, mat['CN Acero inox'], t,
        'FREIDORA (0,40 x 0,70)')
    box(ents, bx(231.6), by(52.9), bx(318.8), by(120.4),
        0.0, H_MOSTRADOR, mat['CN Acero inox'], t,
        'PLANCHA (0,92 x 0,71)')
    box(ents, bx(231.6), by(52.9), bx(318.8), by(120.4),
        H_MOSTRADOR, H_MOSTRADOR + 0.03, mat['CN Negro mate'], t,
        'PLANCHA - superficie')
  end

  # --------------------------------------------------------------------------
  #  8. BARRA DE SERVICIO Y MOSTRADOR DE VENTA
  # --------------------------------------------------------------------------

  def self.barra_y_mostrador(ents, mat, tag)
    t     = tag['10 Barra y mostrador']
    mad   = mat['CN Madera listones']
    inox  = mat['CN Acero inox']
    top   = mat['CN Piedra encimera']
    frio  = mat['CN Drop-in frio']
    vid   = mat['CN Vidrio vitrina']

    z_top = H_MOSTRADOR
    z_enc = H_MOSTRADOR + T_ENCIMERA

    # ---- Trasbarra oeste ---------------------------------------------------
    # RETRO REFRIGGERATO norte (0,675 x 1,50)
    box(ents, bx(117.8), by(254.6), bx(181.6), by(396.3),
        0.0, z_top, inox, t, 'RETRO REFRIGGERATO (norte)')
    box(ents, bx(117.8), by(254.6), bx(181.6), by(396.3),
        z_top, z_enc, top, t, 'Encimera trasbarra norte')

    # Trasbarra sur: 2,72 m de la cota "272".
    # El plano dibuja el testero en x=117,7 pt (1 mm dentro del muro):
    # se ajusta a la cara interior real del muro oeste.
    box(ents, ax(152.5), by(455.8), bx(181.6), by(712.9),
        0.0, z_top, mad, t, 'Trasbarra Sur - MACCHINA CAFFE / RETRO (2,72 m)')
    box(ents, ax(152.5), by(455.8), bx(181.6), by(712.9),
        z_top, z_enc, top, t, 'Encimera trasbarra Sur')

    # máquina de café sobre la trasbarra
    box(ents, bx(124.0), by(462.0), bx(176.0), by(538.0),
        z_enc, z_enc + 0.52, inox, t, 'MACCHINA CAFFE')
    box(ents, bx(124.0), by(545.0), bx(176.0), by(566.0),
        z_enc, z_enc + 0.62, inox, t, 'Molino de cafe')

    # dos senos circulares grafiados (D = 0,47 m, centros a 0,46 m)
    [595.8, 639.4].each_with_index do |cy, i|
      cyl(ents, bx(151.4), by(cy), 0.235, z_enc, z_enc + 0.14,
          inox, t, "Seno circular #{i + 1} (D 0,47)")
      cyl(ents, bx(128.0), by(cy), 0.022, z_enc, z_enc + 0.26,
          inox, t, "Griferia seno #{i + 1}")
    end

    # ---- Mostrador de venta ------------------------------------------------
    # VETRINA EXPO ALTA (FREDDA)  0,85 x 1,00
    box(ents, bx(257.2), by(258.4), bx(337.4), by(352.9),
        0.0, z_top, inox, t, 'VETRINA EXPO ALTA - base')
    box(ents, bx(259.0), by(260.2), bx(335.6), by(351.1),
        z_top, H_VITRINA, vid, t, 'VETRINA EXPO ALTA (FREDDA)')

    # Cuerpo del banco: tres módulos según el plano
    box(ents, bx(257.2), by(352.9), bx(337.4), by(530.5),
        0.0, z_top, mad, t, 'Banco - modulo DROP IN 1 (1,88 m)')
    box(ents, bx(257.2), by(530.5), bx(337.4), by(657.6),
        0.0, z_top, mad, t, 'Banco - modulo DROP IN 2 (1,345 m)')
    box(ents, bx(257.2), by(657.6), bx(337.4), by(704.8),
        0.0, z_top, inox, t, 'BANCO CASSA / RETRO REFRIGGERATO (0,50 m)')

    # Encimera del lado de servicio
    box(ents, bx(257.2), by(352.9), bx(301.6), by(704.8),
        z_top, z_enc, top, t, 'Encimera lado servicio')
    box(ents, bx(301.6), by(657.6), bx(337.4), by(704.8),
        z_top, z_enc, top, t, 'Encimera banco cassa')

    # Cubetas DROP IN CALDO/FREDDO (franja de 0,379 m del plano)
    box(ents, bx(301.6), by(353.8), bx(337.4), by(530.5),
        z_top - 0.05, z_enc, frio, t, 'DROP IN CLDO FREDDO (188)')
    box(ents, bx(301.6), by(531.4), bx(337.4), by(657.6),
        z_top - 0.05, z_enc, frio, t, 'DROP IN CLDO FREDDO (134,5)')

    # Vitrina de protección sobre las cubetas
    box(ents, bx(337.0), by(353.8), bx(337.4), by(657.6),
        z_enc, z_enc + 0.42, vid, t, 'Vitrina banco - frente')
    box(ents, bx(301.6), by(353.8), bx(337.4), by(657.6),
        z_enc + 0.42, z_enc + 0.44, vid, t, 'Vitrina banco - cubierta')

    # TPV sobre el banco cassa
    box(ents, bx(305.0), by(668.0), bx(325.0), by(694.0),
        z_enc, z_enc + 0.30, mat['CN Negro mate'], t, 'TPV')
  end

  # --------------------------------------------------------------------------
  #  9. SANITARIOS DE PLANTA ALTA
  # --------------------------------------------------------------------------

  def self.sanitarios(ents, mat, tag)
    t  = tag['11 Sanitarios']
    z0 = H_PA

    # Encimera de lavabo grafiada (0,50 x 1,40)
    box(ents, ax(283.4), ay(48.8), ax(311.8), ay(128.2),
        z0, z0 + 0.85, mat['CN Madera roble'], t, 'Encimera de lavabos')
    cyl(ents, ax(297.6), ay(87.2), 0.21, z0 + 0.85, z0 + 0.97,
        mat['CN Sanitario'], t, 'Lavabo sobre encimera (D 0,42)')

    # Lavabo mural
    box(ents, ax(365.0), ay(108.0), ax(388.0), ay(128.2),
        z0 + 0.78, z0 + 0.90, mat['CN Sanitario'], t, 'Lavabo mural')

    # Inodoro
    box(ents, ax(411.6), ay(88.7), ax(433.3), ay(101.0),
        z0, z0 + 0.90, mat['CN Sanitario'], t, 'Inodoro - cisterna')
    box(ents, ax(413.0), ay(101.0), ax(432.0), ay(128.0),
        z0 + 0.20, z0 + 0.42, mat['CN Sanitario'], t, 'Inodoro - taza')

    # Franja azul sobre el alicatado (imagen de referencia).
    # Se sitúa en la medianera norte, que no tiene huecos.
    box(ents, ax(283.4), ay(48.8), ax(447.8), ay(48.8) - 0.03,
        z0 + 1.20, H_TOTAL, mat['CN Azul Napoli'], t, 'Franja azul aseo')
  end

  # --------------------------------------------------------------------------
  #  10. MOBILIARIO DE SALA  (no grafiado en los planos — capa independiente)
  # --------------------------------------------------------------------------

  def self.mesa(ents, mat, tag, cx, cy, lado = 0.70)
    g = ents.add_group
    e = g.entities
    h = 0.75
    box(e, cx - lado / 2, cy - lado / 2, cx + lado / 2, cy + lado / 2,
        h - 0.04, h, mat['CN Piedra encimera'], nil, 'Tablero')
    box(e, cx - 0.04, cy - 0.04, cx + 0.04, cy + 0.04,
        0.02, h - 0.04, mat['CN Negro mate'], nil, 'Pie')
    box(e, cx - 0.20, cy - 0.20, cx + 0.20, cy + 0.20,
        0.0, 0.02, mat['CN Negro mate'], nil, 'Base')
    finish(g, nil, tag['12 Mobiliario sala (propuesta)'], 'Mesa 0,70 x 0,70')
  end

  def self.silla(ents, mat, tag, cx, cy, lado_respaldo)
    g = ents.add_group
    e = g.entities
    a = 0.45
    box(e, cx - a / 2, cy - a / 2, cx + a / 2, cy + a / 2,
        0.42, 0.47, mat['CN Tapiceria'], nil, 'Asiento')
    [[-1, -1], [1, -1], [-1, 1], [1, 1]].each do |sx, sy|
      px = cx + sx * (a / 2 - 0.04)
      py = cy + sy * (a / 2 - 0.04)
      box(e, px - 0.02, py - 0.02, px + 0.02, py + 0.02,
          0.0, 0.42, mat['CN Madera roble'], nil, 'Pata')
    end
    xr = cx + lado_respaldo * (a / 2 - 0.05)
    box(e, xr, cy - a / 2, xr + lado_respaldo * 0.05, cy + a / 2,
        0.47, 0.85, mat['CN Tapiceria'], nil, 'Respaldo')
    finish(g, nil, tag['12 Mobiliario sala (propuesta)'], 'Silla')
  end

  def self.taburete(ents, mat, tag, cx, cy)
    g = ents.add_group
    e = g.entities
    cyl(e, cx, cy, 0.17, 0.70, 0.75, mat['CN Madera roble'], nil, 'Asiento')
    cyl(e, cx, cy, 0.03, 0.03, 0.70, mat['CN Negro mate'], nil, 'Pie')
    cyl(e, cx, cy, 0.16, 0.0, 0.03, mat['CN Negro mate'], nil, 'Base')
    finish(g, nil, tag['12 Mobiliario sala (propuesta)'], 'Taburete')
  end

  def self.mobiliario_sala(ents, mat, tag)
    t = tag['12 Mobiliario sala (propuesta)']

    # Zona bajo el forjado (altura libre 2,70 m)
    [4.90, 6.50, 8.10].each do |cy|
      [4.00, 6.00, 8.00].each do |cx|
        mesa(ents, mat, tag, cx, cy)
        silla(ents, mat, tag, cx - 0.66, cy, -1)
        silla(ents, mat, tag, cx + 0.66, cy,  1)
      end
    end

    # Zona a doble altura, frente al mostrador
    [4.00, 6.00, 8.00].each do |cx|
      mesa(ents, mat, tag, cx, 2.85)
      silla(ents, mat, tag, cx - 0.66, 2.85, -1)
      silla(ents, mat, tag, cx + 0.66, 2.85,  1)
    end

    # Barra alta de ventana + taburetes (imagen de referencia).
    # Se apoya en el paño Este del escaparate, dejando libre el acceso.
    x0 = ax(574.3) + 0.10
    x1 = ax(688.8) - 0.10
    y0 = ay(538.0)                       # cara interior del escaparate
    box(ents, x0, y0, x1, y0 + 0.45, 1.01, 1.05,
        mat['CN Madera roble'], t, 'Barra de ventana')
    [x0 + 0.08, x1 - 0.14].each do |sx|
      box(ents, sx, y0 + 0.02, sx + 0.06, y0 + 0.08, 0.0, 1.01,
          mat['CN Negro mate'], t, 'Barra ventana - soporte')
    end

    n = 4
    (0...n).each do |i|
      cx = x0 + (x1 - x0) * (i + 0.5) / n
      taburete(ents, mat, tag, cx, y0 + 0.45 + 0.27)
    end
  end

  # --------------------------------------------------------------------------
  #  ENCUADRE FINAL
  # --------------------------------------------------------------------------

  def self.encuadre(model)
    view = model.active_view
    eye    = p3(-7.0, -8.0, 8.5)
    target = p3(5.0, 4.6, 1.4)
    view.camera = Sketchup::Camera.new(eye, target, Geom::Vector3d.new(0, 0, 1))
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

# Al cargar el archivo desde la Consola Ruby se genera el modelo directamente.
# Si el archivo se coloca en la carpeta Plugins, sólo se instala el menú.
begin
  plugins_dir = Sketchup.find_support_file('Plugins').to_s.downcase
  here        = File.dirname(File.expand_path(__FILE__)).downcase
  CafeNapoliMalaga.build! unless !plugins_dir.empty? && here.start_with?(plugins_dir)
rescue StandardError => e
  puts "Café Napoli: #{e.message}"
  puts e.backtrace.first(5)
end
