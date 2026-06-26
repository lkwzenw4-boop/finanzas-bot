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

    def categorizar_y_mapear(self, descripcion, type_txn='gasto'):
        """
        Categoriza y devuelve (id_category, description) desde la BD.
        Si la confianza es menor a 0.35, se asigna a la categoría comodín ('Otros Gastos' u 'Otros Ingresos').
        """
        from services.category_service import get_all_categories
        categorias_db = get_all_categories()

        # Filtrar solo categorías principales del tipo correcto (id_subcategory es None/Null)
        categorias_principales = [
            c for c in categorias_db 
            if c.id_subcategory is None and c.type_category == type_txn
        ]
        
        # Verificar palabras clave de educación primero
        if type_txn == 'gasto' and self._es_educacion_por_keywords(descripcion):
            categoria_educacion = next((c for c in categorias_principales if c.description.lower() == 'educacion'), None)
            if categoria_educacion:
                return categoria_educacion.id_category, categoria_educacion.description
                
        # Verificar palabras clave de préstamos
        if type_txn == 'gasto' and self._es_prestamo_por_keywords(descripcion):
            categoria_prestamos = next((c for c in categorias_principales if c.description.lower() == 'prestamos'), None)
            if categoria_prestamos:
                return categoria_prestamos.id_category, categoria_prestamos.description
        
        # Buscar si existe la categoría comodín correspondiente
        nombre_otros = 'otros ingresos' if type_txn == 'ingreso' else 'otros gastos'
        categoria_otros = next((c for c in categorias_principales if c.description.lower() == nombre_otros), None)
        
        # Candidatas específicas para evaluar con la IA (excluyendo la comodín)
        categorias_especificas = [c for c in categorias_principales if c.description.lower() != nombre_otros]
        candidatas_nombres = [c.description for c in categorias_especificas]

        # Si no hay categorías principales, retornar la de Otros si existe
        if not candidatas_nombres:
            if categoria_otros:
                return categoria_otros.id_category, categoria_otros.description
            return None, "Desconocida"

        categoria_texto, score = self.clasificar_con_candidatas(descripcion, candidatas_nombres)

        # Si la confianza es baja (menor a 0.35), clasificar como la comodín correspondiente
        if score < 0.35 and categoria_otros:
            print(f"   -> [IA] Confianza baja ({score:.2f}) para '{descripcion}'. Asignado a '{categoria_otros.description}'.")
            return categoria_otros.id_category, categoria_otros.description

        # Buscar en la BD la categoría ganadora
        for cat in categorias_especificas:
            if cat.description.lower() == categoria_texto.lower():
                return cat.id_category, cat.description

        if categoria_otros:
            return categoria_otros.id_category, categoria_otros.description
        return None, "Desconocida"  # si no encuentra

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
