import os
import re
import numpy as np
import onnxruntime as ort
from tokenizers import Tokenizer
from utils.paths import get_base_path


class ClasificadorIA:
    def __init__(self):
        print("\n[Sistema] Cargando modelo IA...")
        
        model_dir = os.path.join(get_base_path(), "ai", "model_onnx")
        
        if not os.path.exists(model_dir):
            raise FileNotFoundError(
                f"No se encontro el modelo ONNX en: {model_dir}\n"
                "Ejecuta primero: python ai/export_model.py"
            )
        
        # Cargar modelo ONNX
        model_path = os.path.join(model_dir, "model.onnx")
        self.session = ort.InferenceSession(
            model_path,
            providers=['CPUExecutionProvider']
        )
        
        # Cargar tokenizer
        tokenizer_path = os.path.join(model_dir, "tokenizer.json")
        self.tokenizer = Tokenizer.from_file(tokenizer_path)
        
        # Configuracion del tokenizer para NLI (premise + hypothesis)
        self.tokenizer.enable_truncation(max_length=512)
        self.tokenizer.enable_padding(length=512)
        
        # Labels del modelo NLI: contradiction, neutral, entailment
        # Para zero-shot: entailment = la descripcion pertenece a la categoria
        self.entailment_id = 0  # indice de "entailment" en mDeBERTa-mnli-xnli
        self.contradiction_id = 2
        
        # Palabras clave para detectar educación
        self.keywords_educacion = [
            "cibertec", "senati", "sencico", "tecsup", "idat", "iest", "cetpro",
            "pucp", "upc", "upn", "utp", "usil", "ucsur", "ucv", "unmsm",
            "universidad", "instituto", "colegio", "escuela", "academia",
            "facultad", "diplomado", "maestria", "posgrado",
            "matricula", "mensualidad", "pension escolar", "pension universitaria",
            "certamen", "examen de admision", "tutoria",
            "curso", "taller educativo", "capacitacion",
        ]
        
        # Palabras clave para detectar prestamos
        self.keywords_prestamos = [
            "prestamo", "cuota", "credito", "hipoteca", "financiamiento", 
            "amortizacion", "vehicular", "personal", "tasa", "interes", "yape"
        ]
        
        print("[Sistema] Modelo IA cargado correctamente.")

    def _es_educacion_por_keywords(self, descripcion: str) -> bool:
        texto = descripcion.lower()
        texto = texto.replace("á","a").replace("é","e").replace("í","i").replace("ó","o").replace("ú","u")
        for kw in self.keywords_educacion:
            kw_norm = kw.replace("á","a").replace("é","e").replace("í","i").replace("ó","o").replace("ú","u")
            if re.search(r'\b' + re.escape(kw_norm) + r'\b', texto):
                return True
        return False

    def _es_prestamo_por_keywords(self, descripcion: str) -> bool:
        texto = descripcion.lower()
        texto = texto.replace("á","a").replace("é","e").replace("í","i").replace("ó","o").replace("ú","u")
        for kw in self.keywords_prestamos:
            kw_norm = kw.replace("á","a").replace("é","e").replace("í","i").replace("ó","o").replace("ú","u")
            if re.search(r'\b' + re.escape(kw_norm) + r'\b', texto):
                return True
        return False

    def _softmax(self, logits):
        """Calcula softmax sobre logits."""
        exp_logits = np.exp(logits - np.max(logits))
        return exp_logits / exp_logits.sum()

    def _nli_predict(self, premise, hypothesis):
        """Ejecuta inferencia NLI y retorna probabilidad de entailment."""
        # Tokenizar como par premise + hypothesis
        encoding = self.tokenizer.encode(premise, hypothesis)
        
        input_ids = np.array([encoding.ids], dtype=np.int64)
        attention_mask = np.array([encoding.attention_mask], dtype=np.int64)
        
        # Preparar inputs para ONNX
        inputs = {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
        }
        
        # Agregar token_type_ids si el modelo lo necesita
        input_names = [inp.name for inp in self.session.get_inputs()]
        if "token_type_ids" in input_names:
            inputs["token_type_ids"] = np.array([encoding.type_ids], dtype=np.int64)
        
        # Inferencia
        outputs = self.session.run(None, inputs)
        logits = outputs[0][0]
        probs = self._softmax(logits)
        
        return probs[self.entailment_id]

    def clasificar_con_candidatas(self, descripcion, candidatas):
        """Clasifica la descripción entre una lista dinámica de candidatas, devolviendo (etiqueta, score)"""
        if not candidatas:
            return None, 0.0
        
        scores = []
        for candidata in candidatas:
            hypothesis = f"Este texto es sobre {candidata}."
            score = self._nli_predict(descripcion, hypothesis)
            scores.append(score)
        
        best_idx = int(np.argmax(scores))
        return candidatas[best_idx], float(scores[best_idx])

    # ── Mapa rápido de palabras clave (sin IA) ──────────────────────
    KEYWORDS_RAPIDOS = {
        'gasto': {
            'Alimentacion':    ['comida','almuerzo','cena','desayuno','pizza','burger','hamburguesa',
                                'restaurante','pollo','arroz','sopa','ceviche','mercado','verdura',
                                'fruta','pan','snack','bebida','cafe','helado','lomo','chicha',
                                'anticucho','taco','sandwich','menu','lonche','delivery','rappi','ifood'],
            'Transporte':      ['taxi','bus','uber','indriver','moto','combustible','gasolina',
                                'pasaje','metro','tren','colectivo','combi','cabify','beat','toll','peaje'],
            'Salud':           ['farmacia','medicina','doctor','medico','consulta','clinica',
                                'hospital','pastilla','remedio','analisis','examen','vacuna','dentista'],
            'Entretenimiento': ['cine','pelicula','juego','deporte','gym','gimnasio','streaming',
                                'netflix','spotify','disney','hbo','prime','youtube','concierto',
                                'evento','fiesta','karaoke','discoteca','bar','partido'],
            'Educacion':       ['universidad','colegio','curso','libro','matricula','mensualidad',
                                'educacion','taller','diplomado','carrera','certificado','capacitacion',
                                'cibertec','senati','tecsup','upc','pucp','upn','utp'],
            'Vivienda':        ['alquiler','luz','agua','internet','gas','cable','renta',
                                'mantenimiento','condominio','limpieza','departamento','casa'],
            'Servicios':       ['telefono','celular','suscripcion','plan','recarga','movistar',
                                'claro','entel','bitel','yape','plin','transferencia'],
            'Tecnologia':      ['laptop','computadora','electronico','tablet','audifonos',
                                'cargador','software','app','programa','monitor','teclado','mouse'],
            'Ropa':            ['ropa','camisa','pantalon','zapatos','vestido','polo','zapatillas',
                                'tenis','chompa','casaca','cartera','bolsa','mochila'],
            'Prestamos':       ['prestamo','cuota','credito','hipoteca','financiamiento',
                                'amortizacion','vehicular','interes','deuda'],
            'Tarjetas de Credito': ['bcp','interbank','bbva','falabella','ripley','scotiabank',
                                    'visa','mastercard','tarjeta'],
        },
        'ingreso': {
            'Salario':     ['sueldo','salario','pago','quincena','mensual','remuneracion',
                            'haberes','nomina','planilla','gratificacion','bonificacion','bono'],
            'Freelance':   ['proyecto','freelance','trabajo','servicio','consultoria',
                            'honorarios','encargo','cliente'],
            'Inversiones': ['dividendo','interes','rendimiento','acciones','cripto','bitcoin',
                            'inversion','utilidad'],
            'Ventas':      ['venta','vendido','vendi','mercaderia','producto','tienda'],
        }
    }

    def _keyword_rapido(self, descripcion: str, type_txn: str):
        """Busca categoría por palabras clave sin usar IA. Retorna nombre o None."""
        texto = descripcion.lower()
        for a, b in [('á','a'),('é','e'),('í','i'),('ó','o'),('ú','u')]:
            texto = texto.replace(a, b)
        mapa = self.KEYWORDS_RAPIDOS.get(type_txn, {})
        for categoria, palabras in mapa.items():
            for palabra in palabras:
                if palabra in texto:
                    return categoria
        return None

    def categorizar_y_mapear(self, descripcion, type_txn='gasto'):
        """
        Categoriza y devuelve (id_category, description) desde la BD.
        Primero intenta keywords rápidos; si no coincide, usa el modelo ONNX.
        Si la confianza es menor a 0.35, asigna a la categoría comodín.
        """
        from services.category_service import get_all_categories
        categorias_db = get_all_categories()

        categorias_principales = [
            c for c in categorias_db
            if c.id_subcategory is None and c.type_category == type_txn
        ]

        nombre_otros = 'otros ingresos' if type_txn == 'ingreso' else 'otros gastos'
        categoria_otros = next((c for c in categorias_principales if c.description.lower() == nombre_otros), None)

        # ── Paso 1: keywords rápidos (sin IA, instantáneo) ──
        match_rapido = self._keyword_rapido(descripcion, type_txn)
        if match_rapido:
            for cat in categorias_principales:
                if cat.description.lower() == match_rapido.lower():
                    print(f"   -> [Keywords] '{descripcion}' → '{cat.description}' (rápido)")
                    return cat.id_category, cat.description

        # ── Paso 2: IA ONNX como fallback (para descripciones no reconocidas) ──
        categorias_especificas = [c for c in categorias_principales if c.description.lower() != nombre_otros]
        candidatas_nombres = [c.description for c in categorias_especificas]

        if not candidatas_nombres:
            if categoria_otros:
                return categoria_otros.id_category, categoria_otros.description
            return None, "Desconocida"

        categoria_texto, score = self.clasificar_con_candidatas(descripcion, candidatas_nombres)
        print(f"   -> [IA-ONNX] '{descripcion}' → '{categoria_texto}' (score={score:.2f})")

        if score < 0.35 and categoria_otros:
            return categoria_otros.id_category, categoria_otros.description

        for cat in categorias_especificas:
            if cat.description.lower() == categoria_texto.lower():
                return cat.id_category, cat.description

        if categoria_otros:
            return categoria_otros.id_category, categoria_otros.description
        return None, "Desconocida"

    def categorizar_y_mapear_subcategoria(self, descripcion, subcategorias_db):
        """
        Categoriza y devuelve (id_subcategory, description) desde la BD
        
        subcategorias_db: lista de objetos Category() que son subcategorías
        """
        if not subcategorias_db:
            return None, "Sin subcategoria"
            
        candidatas = [s.description for s in subcategorias_db]
        subcat_texto, score = self.clasificar_con_candidatas(descripcion, candidatas)
        
        for sub in subcategorias_db:
            if sub.description.lower() == subcat_texto.lower():
                return sub.id_category, sub.description
                
        return None, "Sin subcategoria"
