from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.pagesizes import landscape
from reportlab.lib.colors import HexColor
import os, json
from datetime import datetime
from services.alert_service import AlertService
from services.progression_service import ProgressionService

class PDFManager:
    FOOTER_DIRECCION_DEFAULT = "Martín de Alzaga 3083, B1678 Caseros, Provincia de Buenos Aires"
    FOOTER_TELEFONO_DEFAULT = "011 2089-3090"

    @staticmethod
    def _rutas_logo_candidatas():
        """Rutas sugeridas para detectar automáticamente el logo institucional."""
        base_repo = os.path.dirname(os.path.abspath(__file__))
        home = os.path.expanduser("~")
        return [
            os.path.join(base_repo, "config", "logo_ortopedia.png"),
            os.path.join(base_repo, "config", "branding", "logo_ortopedia.png"),
            os.path.join(base_repo, "assets", "logo_ortopedia.png"),
            os.path.join(home, "Ortopedia", "logo_ortopedia.png"),
        ]

    @staticmethod
    def _logo_path_configurado():
        """Permite usar un logo local por env o por búsqueda automática en rutas sugeridas."""
        logo_path = (os.getenv("PODOSCOPIO_REPORT_LOGO_PATH") or "").strip()
        if logo_path and os.path.exists(logo_path):
            return logo_path

        for candidato in PDFManager._rutas_logo_candidatas():
            if os.path.exists(candidato):
                return candidato
        return None

    @staticmethod
    def _direccion_footer_configurada():
        """Dirección configurable para el pie de página del reporte."""
        direccion = (os.getenv("PODOSCOPIO_REPORT_ADDRESS") or "").strip()
        return direccion or PDFManager.FOOTER_DIRECCION_DEFAULT

    @staticmethod
    def _telefono_footer_configurado():
        """Teléfono configurable para el pie de página del reporte."""
        telefono = (os.getenv("PODOSCOPIO_REPORT_PHONE") or "").strip()
        return telefono or PDFManager.FOOTER_TELEFONO_DEFAULT

    @staticmethod
    def _dibujar_header(c, w, h, titulo):
        logo_path = PDFManager._logo_path_configurado()
        if logo_path:
            try:
                logo_w = 210
                logo_h = 78
                c.drawImage(
                    logo_path,
                    (w - logo_w) / 2,
                    h - 88,
                    width=logo_w,
                    height=logo_h,
                    preserveAspectRatio=True,
                    mask='auto'
                )
            except Exception:
                pass

        c.setFillColor(HexColor("#0f172a"))
        c.setFont("Helvetica-Bold", 16)
        y_titulo = h - 105
        c.drawCentredString(w/2, y_titulo, titulo)
        c.setStrokeColor(HexColor("#0f172a"))
        c.setLineWidth(1)
        c.line((w/2)-135, y_titulo-4, (w/2)+135, y_titulo-4)

    @staticmethod
    def _dibujar_footer(c, w, texto_default):
        direccion = PDFManager._direccion_footer_configurada()
        telefono = PDFManager._telefono_footer_configurado()

        c.setStrokeColor(HexColor("#e5e7eb"))
        c.setLineWidth(1)
        c.line(45, 48, w-45, 48)

        c.setFont("Helvetica", 9)
        c.setFillColor(HexColor("#1f2937"))
        c.drawCentredString(w/2, 35, f"Dirección: {direccion}")

        c.setFont("Helvetica", 9)
        c.setFillColor(HexColor("#374151"))
        c.drawCentredString(w/2, 23, f"Teléfono: {telefono}")

        c.setFont("Helvetica", 8)
        c.setFillColor(HexColor("#9ca3af"))
        c.drawCentredString(w/2, 11, texto_default)

    @staticmethod
    def generar_pedido_taller(paciente, informe, ruta, datos=None):
        """Genera el PDF tipo ficha de pedido a taller (editable desde la app)."""
        c = canvas.Canvas(ruta, pagesize=A4)
        w, h = A4

        datos = datos or {}
        texto = lambda k, default="": str(datos.get(k, default) or "")
        checks = set(datos.get("checks", []))

        # Header (logo y título similar a layout de referencia)
        logo_path = PDFManager._logo_path_configurado()
        if logo_path:
            try:
                c.drawImage(logo_path, w - 190, h - 58, width=150, height=36, preserveAspectRatio=True, mask='auto')
            except Exception:
                pass

        c.setFillColor(HexColor("#000000"))
        c.setFont("Helvetica-Bold", 24)
        c.drawCentredString(w / 2, h - 95, "Medidas Plantillas")
        c.setLineWidth(1.5)
        c.line((w / 2) - 95, h - 100, (w / 2) + 95, h - 100)

        # Datos base
        y = h - 145
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, f"Paciente: {texto('paciente', paciente[1] or '')}")
        c.line(50, y - 2, 190, y - 2)
        c.setFont("Helvetica", 13)
        c.drawString(50, y - 24, f"Edad: {texto('edad', paciente[2] or '')}")

        diagnostico = texto("diagnostico", (informe[4] or "").strip().replace("\n", " "))
        if len(diagnostico) > 60:
            diagnostico = diagnostico[:60].rstrip() + "..."
        c.drawString(50, y - 48, f"Diagnóstico: {diagnostico}")

        c.setFont("Helvetica-Bold", 14)
        c.drawString(270, y, f"Cliente: {texto('cliente', paciente[1] or '')}")
        c.drawString(495, y, f"Fecha: {texto('fecha', informe[1] or '')}")
        c.setFont("Helvetica", 13)
        c.drawString(270, y - 24, f"Altura: {texto('altura')}")
        c.drawString(495, y - 24, f"Peso: {texto('peso')}")

        # Tipo / material
        y2 = h - 230
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y2, "Tipo de Plantilla:")
        c.drawString(50, y2 - 22, "Material:")

        c.setFont("Helvetica", 10)
        col_x = [160, 275, 390, 505]
        checkbox_offset = 92

        c.drawString(col_x[0], y2, "Convencional")
        c.drawString(col_x[1], y2, "Valente Valenti")
        c.drawString(col_x[2], y2, "Termoconformada")
        c.drawString(col_x[3], y2, "Deportiva")

        c.drawString(col_x[0], y2 - 22, "Cuero")
        c.drawString(col_x[1], y2 - 22, "Goma")
        c.drawString(col_x[2], y2 - 22, "Microperforado")
        c.drawString(col_x[3], y2 - 22, "Plastazote")

        checkbox_map = [
            ("tipo_convencional", col_x[0] + checkbox_offset, y2 - 6),
            ("tipo_valente", col_x[1] + checkbox_offset, y2 - 6),
            ("tipo_termoconformada", col_x[2] + checkbox_offset, y2 - 6),
            ("tipo_deportiva", col_x[3] + checkbox_offset, y2 - 6),
            ("material_cuero", col_x[0] + checkbox_offset, y2 - 28),
            ("material_goma", col_x[1] + checkbox_offset, y2 - 28),
            ("material_microperforado", col_x[2] + checkbox_offset, y2 - 28),
            ("material_plastazote", col_x[3] + checkbox_offset, y2 - 28),
        ]
        for key, x, y_box in checkbox_map:
            c.rect(x, y_box, 20, 20, stroke=1, fill=0)
            if key in checks:
                c.setFont("Helvetica-Bold", 14)
                c.drawCentredString(x + 10, y_box + 4, "X")


        # Correcciones
        y3 = h - 300
        c.setFont("Helvetica-Bold", 16)
        c.drawString(45, y3, "Correcciones:")
        c.line(45, y3 - 2, 160, y3 - 2)

        c.setFont("Helvetica", 12)
        c.drawString(125, y3 - 58, "Cuña Pie Izquierdo:")
        c.line(125, y3 - 64, 260, y3 - 64)
        c.drawString(430, y3 - 58, "Cuña Pie Derecho:")
        c.line(430, y3 - 64, 560, y3 - 64)

        # Cuñas esquemáticas
        c.setLineWidth(2)
        c.line(130, y3 - 118, 260, y3 - 118)
        c.line(130, y3 - 118, 130, y3 - 98)
        c.line(130, y3 - 98, 260, y3 - 58)
        c.line(260, y3 - 58, 260, y3 - 118)
        c.line(173, y3 - 118, 173, y3 - 90)
        c.line(216, y3 - 118, 216, y3 - 74)

        c.line(435, y3 - 118, 565, y3 - 118)
        c.line(435, y3 - 118, 435, y3 - 62)
        c.line(435, y3 - 62, 565, y3 - 100)
        c.line(565, y3 - 100, 565, y3 - 118)
        c.line(478, y3 - 118, 478, y3 - 73)
        c.line(521, y3 - 118, 521, y3 - 86)

        c.setLineWidth(1)
        c.setFont("Helvetica", 11)
        c.drawString(50, y3 - 145, f"MM: {texto('cuna_izq_mm')}")
        c.drawString(340, y3 - 145, f"MM: {texto('cuna_der_mm')}")

        c.setFont("Helvetica-Bold", 16)
        c.drawString(45, y3 - 195, "Realce Pie Izquierdo:")
        c.line(45, y3 - 197, 190, y3 - 197)
        c.drawString(355, y3 - 195, "Realce Pie Derecho:")
        c.line(355, y3 - 197, 500, y3 - 197)

        # Caja de mm y observaciones
        c.setLineWidth(1)
        c.rect(45, y3 - 310, (w - 90) / 2, 20, stroke=1, fill=0)
        c.rect(45 + (w - 90) / 2, y3 - 310, (w - 90) / 2, 20, stroke=1, fill=0)
        c.setFont("Helvetica", 12)
        c.drawString(52, y3 - 296, f"MM: {texto('realce_izq_mm')}")
        c.drawString(52 + (w - 90) / 2, y3 - 296, f"MM: {texto('realce_der_mm')}")

        c.setFont("Helvetica-Bold", 16)
        c.drawString(45, y3 - 350, "Observaciones:")
        c.line(45, y3 - 352, 155, y3 - 352)
        c.setLineWidth(1)
        c.rect(45, y3 - 525, w - 90, 165, stroke=1, fill=0)

        c.setFont("Helvetica", 10)
        obs_texto = texto("observaciones", "")
        if obs_texto:
            PDFManager._wrap_text(c, obs_texto, 52, y3 - 368, w - 104)

        PDFManager._dibujar_footer(
            c,
            w,
            f"Pedido a Taller generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        )

        c.save()
        return True

    @staticmethod
    def _buscar_mapa_calor(imagen_original):
        if not imagen_original:
            return None
        if "_original.png" in imagen_original:
            candidato = imagen_original.replace("_original.png", "_mapa_calor.png")
            if os.path.exists(candidato):
                return candidato

        dir_estudio = os.path.dirname(imagen_original)
        if not os.path.exists(dir_estudio):
            return None

        archivos = os.listdir(dir_estudio)
        mapa_files = [f for f in archivos if "mapa" in f.lower() and f.endswith(".png")]
        if not mapa_files:
            return None
        return os.path.join(dir_estudio, mapa_files[0])

    @staticmethod
    def _mediciones_por_clave(mediciones_json):
        if not mediciones_json:
            return {}
        try:
            meds = json.loads(mediciones_json)
        except Exception:
            return {}

        out = {}
        for m in meds:
            lado = m.get("lado")
            tipo = m.get("tipo")
            if not lado or not tipo:
                continue
            valor = m.get("valor_mm")
            if valor is None:
                valor = (m.get("valor_cm") or 0) * 10
            try:
                out[(lado, tipo)] = float(valor)
            except Exception:
                continue
        return out

    @staticmethod
    def _wrap_text(c, text, x, y, width, page_height=None, min_y=55):
        """Envuelve texto largo en múltiples líneas, respetando saltos de línea manuales."""
        if width <= 0:
            return y

        text = "" if text is None else str(text)
        if not text:
            return y

        # Separar primero por los "Enter" reales que haya hecho el usuario o el sistema
        lineas_manuales = text.split('\n')
        
        for linea in lineas_manuales:
            words = linea.split(' ')
            
            # Si es un renglón vacío (el usuario tocó Enter dos veces)
            if not words or all(w == '' for w in words):
                y -= 14
                continue
                
            line = []
            for word in words:
                if not word: continue
                line.append(word)
                # Si la línea actual es más ancha que el margen, bajamos
                if c.stringWidth(' '.join(line)) > width:
                    line.pop()
                    if line:
                        if page_height and y < min_y:
                            c.showPage()
                            y = page_height - 55
                            c.setFont("Helvetica", 10)
                            c.setFillColor(HexColor("#000000"))
                        c.drawString(x, y, ' '.join(line))
                        y -= 14
                    line = [word]
            
            # Dibujar la línea restante
            if line:
                if page_height and y < min_y:
                    c.showPage()
                    y = page_height - 55
                    c.setFont("Helvetica", 10)
                    c.setFillColor(HexColor("#000000"))
                c.drawString(x, y, ' '.join(line))
                y -= 14 # Bajar el cursor para el próximo renglón
                
        return y

    @staticmethod
    def generar_simple(paciente, informe, ruta, postura_estudio=None, postura_estudios=None, postural_mode="compacto"):
        """
        Genera un PDF profesional con AMBAS imágenes:
        - Imagen original (procesada con fondo blanco)
        - Mapa de calor
        """
        c = canvas.Canvas(ruta, pagesize=A4)
        w, h = A4
        
        # ===================================
        # HEADER CON ESTILO
        # ===================================
        PDFManager._dibujar_header(c, w, h, "REPORTE DE PRESIONES DE PISADA")
        
        # ===================================
        # INFORMACIÓN DEL PACIENTE
        # ===================================
        c.setFillColor(HexColor("#000000"))
        y = h - 140

        def ensure_space(needed=40):
            nonlocal y
            if y - needed < 55:
                c.showPage()
                y = h - 55
                c.setFillColor(HexColor("#000000"))

        
        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, y, f"Paciente: {paciente[1]}")
        c.drawString(400, y, f"Fecha: {informe[1]}")
        
        y -= 18
        c.setFont("Helvetica", 10)
        datos_paciente = f"Edad: {paciente[2]} años"
        if paciente[3]:  # Obra social
            datos_paciente += f" | OS: {paciente[3]}"
        if paciente[6]:  # Talle
            datos_paciente += f" | Talle pie: {paciente[6]} mm"
        c.drawString(50, y, datos_paciente)
        
        # ===================================
        # SECCIÓN DE IMÁGENES (MEJORADA)
        # ===================================
        y -= 30
        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, y, "ANÁLISIS VISUAL:")
        c.setStrokeColor(HexColor("#0f172a"))
        c.line(50, y-3, 550, y-3)
        
        y -= 250
        
        # Buscar las imágenes con los nombres correctos
        imagen_original = informe[3]  # Path guardado en la BD
        
        # Construir path del mapa de calor
        imagen_mapa = PDFManager._buscar_mapa_calor(imagen_original)
        
        # Mostrar ambas imágenes
        imagenes_mostradas = 0
        
        if os.path.exists(imagen_original):
            # Imagen Original (Izquierda)
            c.setFont("Helvetica-Bold", 10)
            c.setFillColor(HexColor("#374151"))
            c.drawCentredString(w/4 + 20, y+220, "ESCANEO ORIGINAL")
            
            # Borde decorativo
            c.setStrokeColor(HexColor("#e5e7eb"))
            c.setLineWidth(2)
            c.rect(45, y-5, 250, 210, fill=False, stroke=True)
            
            try:
                c.drawImage(imagen_original, 50, y, width=240, height=200, preserveAspectRatio=True, mask='auto')
                imagenes_mostradas += 1
            except Exception:
                c.setFont("Helvetica", 8)
                c.setFillColor(HexColor("#ef4444"))
                c.drawString(60, y+100, "Error cargando imagen")
        
        if imagen_mapa and os.path.exists(imagen_mapa):
            # Mapa de Calor (Derecha)
            c.setFont("Helvetica-Bold", 10)
            c.setFillColor(HexColor("#374151"))
            c.drawCentredString(3*w/4 - 20, y+220, "MAPA DE PRESIONES")
            
            # Borde decorativo
            c.setStrokeColor(HexColor("#e5e7eb"))
            c.setLineWidth(2)
            c.rect(300, y-5, 250, 210, fill=False, stroke=True)
            
            try:
                c.drawImage(imagen_mapa, 305, y, width=240, height=200, preserveAspectRatio=True, mask='auto')
                imagenes_mostradas += 1
            except Exception:
                c.setFont("Helvetica", 8)
                c.setFillColor(HexColor("#ef4444"))
                c.drawString(315, y+100, "Error cargando mapa")
        
        # Si no se encontró el mapa de calor, mostrar mensaje
        if imagenes_mostradas == 1 and not (imagen_mapa and os.path.exists(imagen_mapa)):
            c.setFont("Helvetica", 9)
            c.setFillColor(HexColor("#9ca3af"))
            c.drawCentredString(3*w/4 - 20, y+100, "(Mapa de calor no disponible)")
        
        ensure_space(80)
        # ===================================
        # SECCIÓN DE MEDICIONES
        # ===================================
        y -= 50
        c.setFillColor(HexColor("#000000"))
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "MEDICIONES REALIZADAS:")
        c.setStrokeColor(HexColor("#0f172a"))
        c.line(50, y-3, 550, y-3)
        
        y -= 25
        c.setFont("Helvetica", 10)
        
        if informe[6]:  # Si hay mediciones en la BD
            try:
                meds = json.loads(informe[6])
                if meds:
                    # Separar por lado, asegurándonos de que soporte la nueva variable 'valor_mm' (o 'valor_cm' de versiones viejas)
                    izq = [m for m in meds if m.get('lado') == 'IZQ' and ('valor_mm' in m or 'valor_cm' in m)]
                    der = [m for m in meds if m.get('lado') == 'DER' and ('valor_mm' in m or 'valor_cm' in m)]
                    
                    # Encabezados
                    c.setFont("Helvetica-Bold", 10)
                    c.drawString(60, y, "PIE IZQUIERDO")
                    c.drawString(320, y, "PIE DERECHO")
                    y -= 18
                    
                    # Mediciones
                    c.setFont("Helvetica", 9)
                    max_items = max(len(izq), len(der))
                    
                    for i in range(max_items):
                        if i < len(izq):
                            valor = izq[i].get('valor_mm', izq[i].get('valor_cm', 0) * 10)
                            c.drawString(60, y-(i*14), f"• {izq[i]['tipo']}: {valor:.1f} mm")
                        if i < len(der):
                            valor = der[i].get('valor_mm', der[i].get('valor_cm', 0) * 10)
                            c.drawString(320, y-(i*14), f"• {der[i]['tipo']}: {valor:.1f} mm")
                    
                    y -= (max_items * 14) + 15
                else:
                    c.setFont("Helvetica", 9)
                    c.setFillColor(HexColor("#6b7280"))
                    c.drawString(60, y, "No se realizaron mediciones automáticas")
                    y -= 20
            except Exception:
                c.setFont("Helvetica", 9)
                c.setFillColor(HexColor("#ef4444"))
                c.drawString(60, y, f"Error al cargar mediciones")
                y -= 20
        else:
            c.setFont("Helvetica", 9)
            c.setFillColor(HexColor("#6b7280"))
            c.drawString(60, y, "No se registraron mediciones")
            y -= 20

        ensure_space(80)
        # ===================================
        # SECCIÓN DE ALERTAS AUTOMÁTICAS
        # ===================================
        alertas_det = AlertService.desde_mediciones_json(informe[6] if len(informe) > 6 else None)
        semaforo = AlertService.resumen_semaforo(alertas_det)

        c.setFillColor(HexColor("#000000"))
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "ALERTAS AUTOMÁTICAS:")
        c.setStrokeColor(HexColor("#0f172a"))
        c.line(50, y-3, 550, y-3)

        y -= 18
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(HexColor(semaforo["color"]))
        c.drawString(60, y, f"Semáforo: {semaforo['nivel']} - {semaforo['mensaje']}")
        y -= 16

        c.setFont("Helvetica", 9)
        c.setFillColor(HexColor("#374151"))
        if alertas_det:
            for a in alertas_det[:6]:
                c.drawString(60, y, f"• {a['message']}")
                y -= 13
        else:
            c.drawString(60, y, "Sin alertas automáticas relevantes")
            y -= 13

        
        ensure_space(80)
        # ===================================
        # SECCIÓN DE DIAGNÓSTICO
        # ===================================
        c.setFillColor(HexColor("#000000"))
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "DIAGNÓSTICO Y OBSERVACIONES:")
        c.setStrokeColor(HexColor("#0f172a"))
        c.line(50, y-3, 550, y-3)
        
        y -= 20
        c.setFont("Helvetica", 10)
        
        if informe[4] and informe[4].strip():
            y = PDFManager._wrap_text(c, informe[4], 50, y, 500, page_height=h)
        else:
            c.setFillColor(HexColor("#6b7280"))
            c.drawString(50, y, "Sin observaciones registradas")
            y -= 20
        
        ensure_space(80)
        # ===================================
        # SECCIÓN DE RECOMENDACIONES
        # ===================================
        if informe[5] and informe[5].strip():
            y -= 15
            c.setFillColor(HexColor("#000000"))
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y, "RECOMENDACIONES:")
            c.setStrokeColor(HexColor("#0f172a"))
            c.line(50, y-3, 550, y-3)
            
            y -= 20
            c.setFont("Helvetica", 10)
            y = PDFManager._wrap_text(c, informe[5], 50, y, 500, page_height=h)
        

        # ===================================
        # SECCIÓN DE ANÁLISIS POSTURAL
        # ===================================
        if postura_estudio:
            ensure_space(120)
            c.setFillColor(HexColor("#000000"))
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y, "ANÁLISIS POSTURAL (ESTÁTICO):")
            c.setStrokeColor(HexColor("#0f172a"))
            c.line(50, y-3, 550, y-3)

            y -= 18
            c.setFont("Helvetica", 10)
            try:
                c.drawString(60, y, f"Fecha: {postura_estudio[1]} | Vista: {postura_estudio[2]} | Protocolo: {postura_estudio[3]}")
                y -= 16

                if postura_estudios:
                    fotos_validas = [pe for pe in postura_estudios if len(pe) > 4 and pe[4] and os.path.exists(pe[4])]
                    if fotos_validas:
                        fotos_validas = fotos_validas[:3]
                        ensure_space(230)
                        c.setFont("Helvetica-Bold", 10)
                        c.setFillColor(HexColor("#374151"))
                        c.drawString(60, y, "Fotos posturales:")
                        y -= 12
                        x_positions = [60, 220, 380]
                        for idx, pe in enumerate(fotos_validas):
                            x = x_positions[idx]
                            try:
                                c.setStrokeColor(HexColor("#e5e7eb"))
                                c.rect(x - 2, y - 142, 146, 146, fill=False, stroke=True)
                                c.drawImage(pe[4], x, y - 140, width=142, height=142, preserveAspectRatio=True, mask='auto')
                                c.setFont("Helvetica", 8)
                                c.setFillColor(HexColor("#374151"))
                                vista = pe[2] if len(pe) > 2 else "vista"
                                c.drawString(x, y - 150, f"{vista}")
                            except Exception:
                                c.setFont("Helvetica", 8)
                                c.setFillColor(HexColor("#ef4444"))
                                c.drawString(x, y - 70, "Error cargando foto")
                        y -= 170

                obs = postura_estudio[9] if len(postura_estudio) > 9 else ""
                if obs and str(obs).strip():
                    obs_txt = str(obs).strip()
                    if len(obs_txt) > 1200:
                        obs_txt = obs_txt[:1200].rstrip() + "..."
                    y = PDFManager._wrap_text(c, obs_txt, 60, y, 480, page_height=h)
                else:
                    c.setFillColor(HexColor("#6b7280"))
                    c.drawString(60, y, "Sin observaciones posturales guardadas")
                    y -= 14
            except Exception:
                c.setFillColor(HexColor("#ef4444"))
                c.drawString(60, y, "Error al renderizar análisis postural")
                y -= 14

        # ===================================
        # FOOTER
        # ===================================
        PDFManager._dibujar_footer(
            c,
            w,
            f"Podoscopio Pro v3.0 - Reporte generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        )
        
        c.save()
        return True

    @staticmethod
    def generar_comparativo(paciente, informe_anterior, informe_actual, ruta, historial_informes=None):
        """Genera un PDF comparativo entre dos estudios del mismo paciente."""
        c = canvas.Canvas(ruta, pagesize=A4)
        w, h = A4


        fecha_ant = informe_anterior[1]
        fecha_act = informe_actual[1]
        titulo = f"COMPARATIVO DE ESTUDIOS ({fecha_ant} → {fecha_act})"

        PDFManager._dibujar_header(c, w, h, titulo)

        c.setFillColor(HexColor("#000000"))
        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, h - 140, f"Paciente: {paciente[1]}")
        c.setFont("Helvetica", 10)
        c.drawString(50, h - 158, f"Edad: {paciente[2]} años")

        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, h - 190, "Comparación de mediciones (mm):")
        c.setStrokeColor(HexColor("#0f172a"))
        c.line(50, h - 195, 550, h - 195)

        y = h - 220
        c.setFont("Helvetica-Bold", 9)
        c.drawString(55, y, "LADO")
        c.drawString(110, y, "TIPO")
        c.drawString(280, y, fecha_ant)
        c.drawString(360, y, fecha_act)
        c.drawString(455, y, "DELTA")

        ant_map = PDFManager._mediciones_por_clave(informe_anterior[6] if len(informe_anterior) > 6 else None)
        act_map = PDFManager._mediciones_por_clave(informe_actual[6] if len(informe_actual) > 6 else None)
        claves = sorted(set(ant_map) | set(act_map))

        c.setFont("Helvetica", 9)
        y -= 16
        if not claves:
            c.drawString(55, y, "No hay mediciones comparables entre ambos estudios.")
            y -= 16
        else:
            for lado, tipo in claves:
                if y < 100:
                    c.showPage()
                    y = h - 60
                    c.setFont("Helvetica", 9)
                v_ant = ant_map.get((lado, tipo))
                v_act = act_map.get((lado, tipo))
                delta_txt = "-"
                ant_txt = "-" if v_ant is None else f"{v_ant:.1f}"
                act_txt = "-" if v_act is None else f"{v_act:.1f}"
                if v_ant is not None and v_act is not None:
                    delta = v_act - v_ant
                    signo = "+" if delta >= 0 else ""
                    delta_txt = f"{signo}{delta:.1f}"

                c.drawString(55, y, lado)
                c.drawString(110, y, tipo)
                c.drawRightString(335, y, ant_txt)
                c.drawRightString(415, y, act_txt)
                c.drawRightString(520, y, delta_txt)
                y -= 14

        y -= 10
        c.setFont("Helvetica-Bold", 11)
        c.setFillColor(HexColor("#000000"))
        c.drawString(50, y, "Resumen clínico:")
        c.setStrokeColor(HexColor("#0f172a"))
        c.line(50, y - 3, 550, y - 3)
        y -= 20

        resumen = (
            f"Estudio anterior ({fecha_ant}): {informe_anterior[4] or 'Sin observaciones'}\n"
            f"Estudio actual ({fecha_act}): {informe_actual[4] or 'Sin observaciones'}"
        )
        c.setFillColor(HexColor("#374151"))
        c.setFont("Helvetica", 9)
        y = PDFManager._wrap_text(c, resumen, 50, y, 500)

        evolucion = ProgressionService.score_progresion(informe_anterior, informe_actual)
        y -= 6
        c.setFillColor(HexColor("#000000"))
        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, y, f"Score evolución: {evolucion['score']}/100 ({evolucion['nivel']})")
        y -= 14
        c.setFillColor(HexColor("#374151"))
        c.setFont("Helvetica", 9)
        y = PDFManager._wrap_text(c, evolucion['detalle'], 50, y, 500)

        if historial_informes and len(historial_informes) >= 3:
            y -= 8
            c.setFillColor(HexColor("#000000"))
            c.setFont("Helvetica-Bold", 11)
            c.drawString(50, y, "Tendencia últimos estudios:")
            c.line(50, y - 3, 550, y - 3)
            y -= 18
            c.setFont("Helvetica", 9)

            baseline = PDFManager._mediciones_por_clave(historial_informes[0][6] if len(historial_informes[0]) > 6 else None)
            latest = PDFManager._mediciones_por_clave(historial_informes[-1][6] if len(historial_informes[-1]) > 6 else None)
            claves = sorted(set(baseline) | set(latest))
            if not claves:
                c.drawString(55, y, "No hay datos suficientes para tendencia.")
            else:
                for lado, tipo in claves[:8]:
                    v_base = baseline.get((lado, tipo))
                    v_last = latest.get((lado, tipo))
                    if v_base is None or v_last is None:
                        continue
                    delta = v_last - v_base
                    signo = "+" if delta >= 0 else ""
                    c.drawString(55, y, f"• {lado} | {tipo}: {v_base:.1f} → {v_last:.1f} mm ({signo}{delta:.1f} mm)")
                    y -= 13

        def _agregar_pagina_estudio(titulo, fecha, path_original):
            c.showPage()
            c.setPageSize(landscape(A4))
            w_l, h_l = landscape(A4)
            c.setFillColor(HexColor("#0f172a"))
            c.rect(0, h_l - 65, w_l, 65, fill=True, stroke=False)
            c.setFillColor(HexColor("#ffffff"))
            c.setFont("Helvetica-Bold", 15)
            c.drawCentredString(w_l / 2, h_l - 40, f"{titulo} - {fecha}")

            mapa = PDFManager._buscar_mapa_calor(path_original)
            y_img = h_l - 340

            c.setFillColor(HexColor("#374151"))
            c.setFont("Helvetica-Bold", 10)
            c.drawCentredString(w_l / 4, y_img + 245, "ESCANEO")
            c.drawCentredString(3 * w_l / 4, y_img + 245, "MAPA DE PRESIONES")

            if path_original and os.path.exists(path_original):
                c.drawImage(path_original, 35, y_img, width=360, height=230, preserveAspectRatio=True, mask='auto')
            else:
                c.setFont("Helvetica", 10)
                c.drawString(50, y_img + 110, "Imagen no disponible")

            if mapa and os.path.exists(mapa):
                c.drawImage(mapa, 445, y_img, width=360, height=230, preserveAspectRatio=True, mask='auto')
            else:
                c.setFont("Helvetica", 10)
                c.drawString(460, y_img + 110, "Mapa no disponible")

        ant_original = informe_anterior[3] if len(informe_anterior) > 3 else None
        act_original = informe_actual[3] if len(informe_actual) > 3 else None
        _agregar_pagina_estudio("ESTUDIO ANTERIOR", fecha_ant, ant_original)
        _agregar_pagina_estudio("ESTUDIO ACTUAL", fecha_act, act_original)

        PDFManager._dibujar_footer(
            c,
            w,
            f"Podoscopio Pro v3.0 - Comparativo generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        )
        c.save()
        return True
