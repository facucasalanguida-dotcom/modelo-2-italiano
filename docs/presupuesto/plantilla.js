// Plantilla de presupuesto y contrato de obra de Grupo SUMA, editable en Word.
// Los textos entre [CORCHETES] son los que hay que sustituir en cada obra.
const fs = require('fs');
const {
  Document, Packer, Paragraph, TextRun, ImageRun, Table, TableRow, TableCell,
  WidthType, BorderStyle, AlignmentType, ShadingType, LevelFormat,
  VerticalAlign, PageBreak,
} = require('docx');

const TINTA = '1B2733';
const SUAVE = '5A6472';
const TENUE = '8A929B';
const LINEA = 'D7D2C8';
const ROJO  = 'E3000F';
const FONDO = 'F7F5F1';

const SERIF = 'Georgia';
const SANS  = 'Arial';

const sinBorde = { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' };
const nada = { top: sinBorde, bottom: sinBorde, left: sinBorde, right: sinBorde };

// ------------------------------------------------------------ utilidades
const txt = (t, o = {}) => new TextRun({
  text: t, font: o.font || SANS, size: o.size || 18,
  bold: o.bold, color: o.color || TINTA, italics: o.italics,
});

const p = (runs, o = {}) => new Paragraph({
  children: Array.isArray(runs) ? runs : [runs],
  spacing: { before: o.before || 0, after: o.after === undefined ? 60 : o.after,
             line: o.line || 260 },
  alignment: o.align,
  border: o.border,
  indent: o.indent,
});

// Rótulo de sección: rojo, versalitas y filete inferior
const rotulo = (t) => new Paragraph({
  children: [new TextRun({ text: t.toUpperCase(), font: SANS, size: 15,
    bold: true, color: ROJO, characterSpacing: 30 })],
  spacing: { before: 260, after: 100 },
  border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: LINEA, space: 3 } },
});

// Línea para escribir a mano
const raya = (etiqueta, punteada) => [
  new Paragraph({
    children: [new TextRun({ text: etiqueta.toUpperCase(), font: SANS, size: 13,
      color: TENUE, characterSpacing: 20 })],
    spacing: { before: 120, after: 40 },
  }),
  new Paragraph({
    children: [txt('')],
    spacing: { after: 60 },
    border: { bottom: { style: punteada ? BorderStyle.DOTTED : BorderStyle.SINGLE,
                        size: 4, color: TINTA, space: 2 } },
  }),
];

// ------------------------------------------------------------ contenido
const CAPITULOS = [
  ['01', 'Actuaciones previas', [
    'Limpieza y retiro de luminarias',
    'Retiro de cartelería existente en frente',
    'Contratación de cuba para materiales y escombros',
    'Andamio para trabajo en altura']],
  ['02', 'Albañilería', [
    'Preparación de pared para pintura',
    'Saneamiento de paredes',
    'Reparación y pintura de techos',
    'Pintura exterior según color de normativa']],
  ['03', 'Carpintería', [
    'Suelo de tarima de alto tránsito de uso comercial',
    'Rodapiés',
    'Revestimiento en barra']],
  ['04', 'Fontanería y saneamiento', [
    'Revisión de tuberías y desagües']],
  ['05', 'Baños', [
    'Cambio de lavabos, griferías y mueble',
    'Pintura general']],
  ['06', 'Electricidad', [
    'Revisión de circuitos',
    'Adecuación de enchufes',
    'Colocación de luminaria en techo']],
];

const NO_INCLUIDO = ['Mesas', 'Sillones', 'Sillas', 'Taburetes',
  'Elementos decorativos', 'Luminarias colgantes', 'Neveras',
  'Mobiliario y equipos de funcionamiento de cocina'];

const PAGOS = [
  ['30 %', '[0.000,00 €]', 'A la aceptación de la oferta y comienzo', '[fecha]'],
  ['20 %', '[0.000,00 €]', 'Por avance de obra', '[fecha]'],
  ['20 %', '[0.000,00 €]', 'Por avance de obra', '[fecha]'],
  ['20 %', '[0.000,00 €]', 'Por avance de obra', '[fecha]'],
  ['10 %', '[0.000,00 €]', 'A la entrega final', 'Fin de obra'],
];

// ------------------------------------------------------------ membrete
const logo = fs.readFileSync(__dirname + '/logo_tinta.png');
const membrete = new Table({
  columnWidths: [4400, 5692],
  width: { size: 10092, type: WidthType.DXA },
  borders: { ...nada,
    bottom: { style: BorderStyle.SINGLE, size: 12, color: TINTA } },
  rows: [new TableRow({ children: [
    new TableCell({
      width: { size: 4400, type: WidthType.DXA }, borders: nada,
      verticalAlign: VerticalAlign.BOTTOM,
      margins: { bottom: 120 },
      children: [new Paragraph({ children: [new ImageRun({
        data: logo, type: 'png', transformation: { width: 168, height: 35 } })],
        spacing: { after: 0 } })],
    }),
    new TableCell({
      width: { size: 5692, type: WidthType.DXA }, borders: nada,
      verticalAlign: VerticalAlign.BOTTOM,
      margins: { bottom: 120 },
      children: [
        p(txt('GRUPO SUMA', { bold: true, size: 15 }), { align: AlignmentType.RIGHT, after: 0, line: 200 }),
        p(txt('Calle Eduardo de Palacio 14, 4.º piso B2 · Málaga, España', { size: 14, color: SUAVE }), { align: AlignmentType.RIGHT, after: 0, line: 200 }),
        p(txt('+34 680 75 74 91 · sebastian@gruposuma.eu', { size: 14, color: SUAVE }), { align: AlignmentType.RIGHT, after: 0, line: 200 }),
      ],
    }),
  ]})],
});

// ------------------------------------------------------------ capitulos
const capitulos = [];
CAPITULOS.forEach(([num, tit, items]) => {
  capitulos.push(new Paragraph({
    children: [
      new TextRun({ text: `  ${num}  `, font: SANS, size: 14, bold: true,
        color: 'FFFFFF', shading: { type: ShadingType.CLEAR, fill: TINTA } }),
      new TextRun({ text: '   ' }),
      new TextRun({ text: tit, font: SERIF, size: 19, bold: true, color: TINTA }),
    ],
    spacing: { before: 200, after: 70 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 3, color: 'EDEAE3', space: 2 } },
  }));
  items.forEach((it) => capitulos.push(new Paragraph({
    children: [txt(it, { color: SUAVE })],
    numbering: { reference: 'guion', level: 0 },
    spacing: { after: 30, line: 250 },
  })));
});

// ------------------------------------------------------ bloque economico
const celdaIzq = [
  rotulo('Alcance económico'),
  new Paragraph({
    children: [txt('Incluido: ', { bold: true }),
               txt('los materiales, la mano de obra, el seguimiento y la coordinación de obra están incluidos en el presupuesto.', { color: SUAVE })],
    shading: { type: ShadingType.CLEAR, fill: FONDO },
    border: { left: { style: BorderStyle.SINGLE, size: 12, color: ROJO, space: 6 } },
    spacing: { before: 60, after: 200, line: 250 },
    indent: { left: 120, right: 120 },
  }),
  new Table({
    columnWidths: [4700],
    width: { size: 4700, type: WidthType.DXA },
    borders: {
      top: { style: BorderStyle.SINGLE, size: 4, color: TINTA },
      bottom: { style: BorderStyle.SINGLE, size: 4, color: TINTA },
      left: { style: BorderStyle.SINGLE, size: 4, color: TINTA },
      right: { style: BorderStyle.SINGLE, size: 4, color: TINTA },
      insideHorizontal: { style: BorderStyle.SINGLE, size: 3, color: LINEA },
      insideVertical: sinBorde,
    },
    rows: [
      new TableRow({ children: [new TableCell({
        width: { size: 4700, type: WidthType.DXA },
        margins: { top: 140, bottom: 140, left: 160, right: 160 },
        children: [new Paragraph({ children: [
          new TextRun({ text: 'IMPORTE TOTAL', font: SANS, size: 14, color: TENUE, characterSpacing: 24 }),
          new TextRun({ text: '\t' }),
          new TextRun({ text: '[00.000,00 €]', font: SERIF, size: 30, bold: true, color: TINTA }),
        ], tabStops: [{ type: 'right', position: 4380 }], spacing: { after: 0 } })],
      })]}),
      new TableRow({ children: [new TableCell({
        width: { size: 4700, type: WidthType.DXA },
        margins: { top: 120, bottom: 120, left: 160, right: 160 },
        children: [p(txt('IVA no incluido; se aplicará el vigente al facturar.', { size: 15, color: SUAVE }), { after: 0 })],
      })]}),
    ],
  }),
  rotulo('Plazo de ejecución'),
  p([txt('Tiempo de ejecución aproximado de ', { color: SUAVE }),
     txt('[00 días]', { bold: true }),
     txt(' desde el comienzo de los trabajos.', { color: SUAVE })]),
];

const celdaDer = [rotulo('Materiales y elementos no incluidos')].concat(
  NO_INCLUIDO.map((x) => new Paragraph({
    children: [txt(x, { color: SUAVE })],
    numbering: { reference: 'cruz', level: 0 },
    spacing: { after: 30, line: 250 },
  })));

const dosColumnas = new Table({
  columnWidths: [4846, 400, 4846],
  width: { size: 10092, type: WidthType.DXA },
  borders: nada,
  rows: [new TableRow({ children: [
    new TableCell({ width: { size: 4846, type: WidthType.DXA }, borders: nada, children: celdaIzq }),
    new TableCell({ width: { size: 400, type: WidthType.DXA }, borders: nada, children: [p(txt(''), { after: 0 })] }),
    new TableCell({ width: { size: 4846, type: WidthType.DXA }, borders: nada, children: celdaDer }),
  ]})],
});

// ------------------------------------------------------------- pagos
const cabPago = (t, der) => new TableCell({
  width: { size: 100, type: WidthType.DXA }, borders: {
    ...nada, bottom: { style: BorderStyle.SINGLE, size: 4, color: LINEA } },
  margins: { top: 40, bottom: 80, right: 100 },
  children: [p(new TextRun({ text: t.toUpperCase(), font: SANS, size: 13,
    bold: true, color: TENUE, characterSpacing: 20 }),
    { after: 0, align: der ? AlignmentType.RIGHT : undefined })],
});

const celdaPago = (t, w, bold, der) => new TableCell({
  width: { size: w, type: WidthType.DXA },
  borders: { ...nada, bottom: { style: BorderStyle.SINGLE, size: 2, color: 'EDEAE3' } },
  margins: { top: 90, bottom: 90, right: 100 },
  children: [p(txt(t, { bold, color: bold ? TINTA : SUAVE }),
    { after: 0, align: der ? AlignmentType.RIGHT : undefined })],
});

const filasPago = PAGOS.map(([pc, im, co, fe]) => new TableRow({
  children: [
    celdaPago(pc, 900, true, false),
    celdaPago(im, 1700, true, false),
    celdaPago(co, 5292, false, false),
    celdaPago(fe, 2200, false, true),
  ],
}));

const tablaPagos = new Table({
  columnWidths: [900, 1700, 5292, 2200],
  width: { size: 10092, type: WidthType.DXA },
  borders: nada,
  rows: [
    new TableRow({
      tableHeader: true,
      children: [cabPago('%'), cabPago('Importe'), cabPago('Concepto'),
                 cabPago('Fecha', true)],
    }),
    ...filasPago,
  ],
});

// ------------------------------------------------------------- firmas
const cajaFirma = (titulo, rol) => new TableCell({
  width: { size: 4846, type: WidthType.DXA },
  borders: {
    top: { style: BorderStyle.SINGLE, size: 4, color: LINEA },
    bottom: { style: BorderStyle.SINGLE, size: 4, color: LINEA },
    left: { style: BorderStyle.SINGLE, size: 4, color: LINEA },
    right: { style: BorderStyle.SINGLE, size: 4, color: LINEA },
  },
  margins: { top: 180, bottom: 160, left: 200, right: 200 },
  children: [
    p(txt(titulo, { font: SERIF, size: 20, bold: true }), { after: 20 }),
    p(new TextRun({ text: rol.toUpperCase(), font: SANS, size: 13, color: TENUE,
      characterSpacing: 20 }), { after: 120 }),
    ...raya('Nombre y apellidos', false),
    ...raya('DNI / NIF', true),
    ...raya('Lugar y fecha', true),
    p(txt(''), { after: 0 }), p(txt(''), { after: 0 }), p(txt(''), { after: 0 }),
    new Paragraph({ children: [txt('')], spacing: { after: 60 },
      border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: TINTA, space: 2 } } }),
    p(new TextRun({ text: 'FIRMA', font: SANS, size: 13, color: TENUE,
      characterSpacing: 20 }), { after: 0 }),
  ],
});

const tablaFirmas = new Table({
  columnWidths: [4846, 400, 4846],
  width: { size: 10092, type: WidthType.DXA },
  borders: nada,
  rows: [new TableRow({ children: [
    cajaFirma('Grupo SUMA', 'La empresa contratista'),
    new TableCell({ width: { size: 400, type: WidthType.DXA }, borders: nada,
      children: [p(txt(''), { after: 0 })] }),
    cajaFirma('La propiedad', 'El cliente'),
  ]})],
});

// ------------------------------------------------------------ documento
const doc = new Document({
  numbering: { config: [
    { reference: 'guion', levels: [{ level: 0, format: LevelFormat.BULLET, text: '—',
      alignment: AlignmentType.LEFT,
      style: { paragraph: { indent: { left: 260, hanging: 200 } },
               run: { color: LINEA, font: SANS } } }] },
    { reference: 'cruz', levels: [{ level: 0, format: LevelFormat.BULLET, text: '×',
      alignment: AlignmentType.LEFT,
      style: { paragraph: { indent: { left: 260, hanging: 200 } },
               run: { color: LINEA, font: SANS } } }] },
  ]},
  sections: [{
    properties: { page: { margin: { top: 850, bottom: 800, left: 907, right: 907 } } },
    children: [
      membrete,
      p(txt('Presupuesto y contrato de obra', { font: SERIF, size: 42, bold: true }),
        { before: 320, after: 40, line: 480 }),
      p(txt('[Reforma y ambientación de local comercial]', { size: 21, color: SUAVE }),
        { after: 60 }),
      p([txt('Presupuesto n.º ', { size: 18, color: SUAVE }),
         txt('[F00000000]', { size: 18, bold: true }),
         txt('   ·   [00 de mes de 0000]', { size: 18, color: SUAVE })], { after: 0 }),

      rotulo('Objeto del contrato'),
      p([txt('[Reforma y ambientación del local, según diseño.] ', { font: SERIF, size: 23, bold: true }),
         txt('[Nombre del establecimiento] — [dirección], [ciudad].', { font: SERIF, size: 23 })],
        { after: 60, line: 320 }),

      rotulo('Trabajos incluidos en la cotización'),
      ...capitulos,

      new Paragraph({ children: [new PageBreak()] }),

      membrete,
      dosColumnas,
      rotulo('Calendario de pagos'),
      tablaPagos,
      p(txt('Importes calculados sobre la base imponible, IVA aparte.',
        { size: 14, color: TENUE }), { before: 80 }),

      rotulo('Conformidad y aceptación'),
      p(txt('Las partes que suscriben manifiestan su conformidad con el alcance de los trabajos, el importe, el calendario de pagos y el plazo de ejecución recogidos en el presente documento, que firman por duplicado y a un solo efecto en el lugar y la fecha indicados.',
        { color: SUAVE }), { after: 200, line: 260 }),
      tablaFirmas,
    ],
  }],
});

Packer.toBuffer(doc).then((b) => {
  fs.writeFileSync(__dirname + '/Plantilla_Presupuesto_GrupoSUMA.docx', b);
  console.log('docx escrito:', (b.length / 1024).toFixed(0), 'KB');
});
