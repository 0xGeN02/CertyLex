import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, ListFlowable, ListItem
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_JUSTIFY

# Datos de ejemplo
empresa_nombre = "Hermanos Santa Cristina y Aparejadores S.L."
empresa_nif = "B12345678"
representante_nombre = "Juan Pérez Rodríguez"
representante_nif = "98765432B"
empleados = [
    ("Ana García-Gomez Vitoria", "12345678A"),
    ("Luis Martínez de la Calle", "23456789B"),
    ("Jose Mª Rodríguez Miguez", "34567890C"),
    ("Mario David López-Sanmartin Gutierrez", "45678901D"),
    ("Elena Fernández Fernandez", "56789012E"),
]

# Crear documento PDF
file_path = "./samples/pdf/contrato_test.pdf"
os.makedirs(os.path.dirname(file_path), exist_ok=True)

doc = SimpleDocTemplate(file_path, pagesize=A4,
                        rightMargin=2*cm, leftMargin=2*cm,
                        topMargin=2*cm, bottomMargin=2*cm)
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY, leading=14, spaceAfter=6))
normal = styles['Justify']
heading = styles['Heading4']
title = styles['Title']
subheading = styles['Heading3']

elements = []

# Portada
elements.append(Paragraph("CONTRATO DE TRABAJO - ACUERDO MARCO", title))
elements.append(Spacer(1, 12))
elements.append(Paragraph(f"<b>Empresa:</b> {empresa_nombre}", normal))
elements.append(Paragraph(f"<b>NIF:</b> {empresa_nif}", normal))
elements.append(Spacer(1, 6))
elements.append(Paragraph(f"<b>Representante Legal:</b> {representante_nombre}", normal))
elements.append(Paragraph(f"<b>NIF Representante:</b> {representante_nif}", normal))
elements.append(Spacer(1, 24))

# Sección Historia y Misión
elements.append(Paragraph("1. ANTECEDENTES Y MISIÓN DE LA EMPRESA", subheading))
elements.append(Paragraph(
    "Hermanos Santa Cristina y Aparejadores S.L. es una empresa familiar "
    "fundada en 1985, especializada en servicios de ingeniería civil y "
    "gestión de proyectos de construcción. Durante más de tres décadas, "
    "ha participado en obras emblemáticas que han transformado el paisaje "
    "urbano y rural de la región.", normal))
elements.append(Paragraph(
    "La misión de la empresa es ofrecer soluciones innovadoras y sostenibles "
    "que garanticen la calidad, la seguridad y la eficiencia en cada proyecto. "
    "Nuestro compromiso es con el desarrollo de infraestructuras que mejoren "
    "la vida de las comunidades y contribuyan al progreso económico.",
    normal))
elements.append(Spacer(1, 12))

# Visión y Valores
elements.append(Paragraph("2. VISIÓN Y VALORES CORPORATIVOS", subheading))
elements.append(Paragraph(
    "La visión de Hermanos Santa Cristina y Aparejadores S.L. es consolidarse "
    "como referente nacional en proyectos de rehabilitación y obra nueva, "
    "manteniendo un liderazgo basado en la excelencia técnica y el respeto al entorno.",
    normal))
elements.append(Paragraph(
    "Los valores que guían nuestra actividad son:\n"
    "- <b>Compromiso:</b> con la calidad y el cumplimiento de los plazos.\n"
    "- <b>Innovación:</b> en métodos constructivos y materiales.\n"
    "- <b>Responsabilidad social:</b> con el medio ambiente y las personas.\n"
    "- <b>Transparencia:</b> en la gestión y en la comunicación con clientes.",
    normal))
elements.append(PageBreak())

# Sección Empleados
elements.append(Paragraph("3. EMPLEADOS CONTRATADOS", subheading))
data = [["Nombre completo", "NIF"]] + empleados
table = Table(data, colWidths=[10*cm, 4*cm], hAlign='LEFT')
table.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
    ('GRID', (0,0), (-1,-1), 0.5, colors.black),
    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
    ('VALIGN', (0,0), (-1,-1), 'TOP'),
]))
elements.append(table)
elements.append(Spacer(1, 12))

# Funciones
elements.append(Paragraph("4. DESCRIPCIÓN DE FUNCIONES Y RESPONSABILIDADES", subheading))
functions = [
    "Supervisión y control de calidad en obras de construcción y rehabilitación.",
    "Elaboración y revisión de planos, cálculos estructurales e informes técnicos.",
    "Coordinación con subcontratistas, proveedores y equipos multidisciplinares.",
    "Visitas periódicas a obra para verificar el cumplimiento de normativas.",
    "Asesoramiento técnico a clientes y resolución de incidencias.",
]
elements.append(ListFlowable([ListItem(Paragraph(f"- {f}", normal)) for f in functions], bulletType='bullet'))
elements.append(Spacer(1, 12))

# Horario y lugar
elements.append(Paragraph("5. HORARIO, LUGAR DE TRABAJO Y TELETRABAJO", subheading))
elements.append(Paragraph(
    "El horario ordinario de trabajo es de lunes a viernes, de 8:00 a 17:00 horas, "
    "con una pausa para almuerzo de 45 minutos. Se contempla flexibilidad horaria "
    "y la posibilidad de hasta dos días de teletrabajo semanal, previa autorización.",
    normal))
elements.append(Spacer(1, 12))

# Formación
elements.append(Paragraph("6. FORMACIÓN CONTINUA Y DESARROLLO PROFESIONAL", subheading))
elements.append(Paragraph(
    "La empresa instaura programas anuales de formación que incluyen:\n"
    "- Cursos de seguridad y prevención de riesgos laborales.\n"
    "- Talleres de software de modelado BIM y CAD avanzado.\n"
    "- Seminarios de sostenibilidad y nuevas técnicas constructivas.\n"
    "Se asignarán 40 horas anuales por empleado para actividades formativas.",
    normal))
elements.append(PageBreak())

# Beneficios
elements.append(Paragraph("7. BENEFICIOS SOCIALES Y CONDICIONES ECONÓMICAS", subheading))
elements.append(Paragraph(
    "Además de la retribución base, los empleados contarán con los siguientes beneficios:\n"
    "- Seguro médico privado de cobertura nacional.\n"
    "- Ticket restaurante o concesión de comedor.\n"
    "- Plan de pensiones de empleo con aportación empresarial.\n"
    "- Permisos adicionales por motivos personales y familiares.",
    normal))
elements.append(Spacer(1, 12))

# Salud y Seguridad
elements.append(Paragraph("8. SEGURIDAD Y PREVENCIÓN DE RIESGOS", subheading))
elements.append(Paragraph(
    "Se aplicará rigurosamente el Plan de Prevención de Riesgos Laborales "
    "adaptado a cada obra, conforme a la normativa RD 39/1997. Los empleados "
    "deberán asistir a las jornadas de formación obligatoria en PRL y utilizar "
    "el equipamiento de protección facilitado.",
    normal))
elements.append(Spacer(1, 12))

# Conducta y ética
elements.append(Paragraph("9. CÓDIGO DE CONDUCTA Y ÉTICA", subheading))
elements.append(Paragraph(
    "Se espera que los empleados mantengan una conducta ética, evitando conflictos de "
    "intereses, respetando la diversidad y la igualdad de oportunidades. Cualquier "
    "infracción podrá dar lugar a sanciones disciplinarias.",
    normal))
elements.append(PageBreak())

# Protección de datos y confidencialidad
elements.append(Paragraph("10. CONFIDENCIALIDAD Y PROTECCIÓN DE DATOS", subheading))
elements.append(Paragraph(
    "Los empleados se comprometen a guardar absoluta confidencialidad sobre la información "
    "comercial, técnica y financiera de la empresa y sus clientes. El tratamiento de datos "
    "se regirá por el RGPD (UE) 2016/679 y la LOPDGDD, garantizando derechos de acceso, "
    "rectificación y supresión.",
    normal))
elements.append(Spacer(1, 12))

# Terminación y jurisdicción
elements.append(Paragraph("11. TERMINACIÓN DEL CONTRATO", subheading))
elements.append(Paragraph(
    "Este contrato podrá extinguirse por las causas previstas en el Estatuto de los Trabajadores "
    "y por mutuo acuerdo. En caso de despido, se aplicarán los procedimientos legales y "
    "las indemnizaciones correspondientes.",
    normal))
elements.append(Spacer(1, 12))
elements.append(Paragraph("12. LEGISLACIÓN APLICABLE Y JURISDICCIÓN", subheading))
elements.append(Paragraph(
    "El presente contrato se regirá por el Estatuto de los Trabajadores, el Código Civil "
    "y demás normativa aplicable. Para la resolución de conflictos, las partes quedan "
    "sometidas a los Juzgados y Tribunales de Madrid.",
    normal))
elements.append(PageBreak())

# Firmas
elements.append(Paragraph("FIRMAS", subheading))
signature_data = [
    ["Por la Empresa", "", "Por los Empleados", ""],
    [f"{representante_nombre}", "", "Ana García-Gomez Vitoria", ""],
    [f"NIF: {representante_nif}", "", "NIF: 12345678A", ""],
    ["", "", "Luis Martínez de la Calle", ""],
    ["", "", "NIF: 23456789B", ""],
    ["", "", "Jose Mª Rodríguez Miguez", ""],
    ["", "", "NIF: 34567890C", ""],
    ["", "", "Mario David López-Sanmartin Gutierrez", ""],
    ["", "", "NIF: 45678901D", ""],
    ["", "", "Elena Fernández Fernandez", ""],
    ["", "", "NIF: 56789012E", ""],
]
sign_table = Table(signature_data, colWidths=[6*cm, 1*cm, 6*cm, 1*cm], hAlign='LEFT')
sign_table.setStyle(TableStyle([
    ('SPAN', (0,0), (1,0)),
    ('SPAN', (2,0), (3,0)),
    ('LINEBELOW', (0,1), (1,1), 0.5, colors.black),
    ('GRID', (0,0), (-1,-1), 0, colors.white),
]))
elements.append(sign_table)
elements.append(Spacer(1, 12))
elements.append(Paragraph("Fecha: ____________________", normal))

# Construir PDF
doc.build(elements)