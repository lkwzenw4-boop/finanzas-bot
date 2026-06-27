import re

class ClasificadorIA:
    """
    Clasificador por palabras clave (sin modelo ONNX).
    Categoriza instantáneamente usando un diccionario de keywords.
    Las categorías se cachean en RAM al primer uso.
    """

    # ── Cache de categorías (se carga una sola vez desde la BD) ──────
    _cache_categorias = None

    # ── Mapa de palabras clave por tipo de transacción ───────────────
    KEYWORDS = {
        'gasto': {
            'Alimentacion': [
                'comida','almuerzo','cena','desayuno','pizza','burger','hamburguesa',
                'restaurante','pollo','arroz','sopa','ceviche','mercado','verdura',
                'fruta','pan','snack','bebida','cafe','helado','lomo','chicha',
                'anticucho','taco','sandwich','menu','lonche','delivery','rappi',
                'ifood','pedidosya','chifa','polleria','cevicheria','panaderia',
                'minimarket','bodega','supermercado','wong','plaza vea','tottus',
                'metro','vivanda','candy','dulce','postre','jugo','gaseosa',
                'cerveza','leche','agua','ensalada','sushi','pasta','fideos',
            ],
            'Transporte': [
                'taxi','bus','uber','indriver','moto','combustible','gasolina',
                'pasaje','metro','tren','colectivo','combi','cabify','beat',
                'toll','peaje','estacionamiento','parking','bicicleta','scooter',
                'boleto','ticket','transporte','movilidad','llenado',
            ],
            'Salud': [
                'farmacia','medicina','doctor','medico','consulta','clinica',
                'hospital','pastilla','remedio','analisis','examen','vacuna',
                'dentista','odontologo','optico','lentes','seguro salud',
                'botica','inkafarma','mifarma','arcangel','fybeca',
                'termometro','jeringa','alcohol','mascarilla','vitamina',
            ],
            'Entretenimiento': [
                'cine','pelicula','juego','deporte','gym','gimnasio','streaming',
                'netflix','spotify','disney','hbo','prime','youtube','concierto',
                'evento','fiesta','karaoke','discoteca','bar','partido',
                'videojuego','steam','playstation','xbox','switch','anime',
                'viaje','tour','excursion','hotel','hospedaje','airbnb',
                'entrada','boleto cine','multicines','cineplanet','cinemark',
            ],
            'Educacion': [
                'universidad','colegio','curso','libro','matricula','mensualidad',
                'educacion','taller','diplomado','carrera','certificado','capacitacion',
                'cibertec','senati','tecsup','upc','pucp','upn','utp','usil',
                'ucv','unmsm','idat','sencico','cetpro','academia','instituto',
                'pension','escuela','facultad','maestria','posgrado','tutoria',
                'material escolar','utiles','lapiz','cuaderno','mochila escolar',
            ],
            'Vivienda': [
                'alquiler','luz','agua','internet','gas','cable','renta',
                'mantenimiento','condominio','limpieza','departamento','casa',
                'electricidad','enel','luz del sur','sedapal','natural gas',
                'conegas','limagas','entel hogar','movistar hogar','claro hogar',
                'impuesto predial','arbitrios','junta','porteria','ascensor',
            ],
            'Servicios': [
                'telefono','celular','suscripcion','plan','recarga','movistar',
                'claro','entel','bitel','yape','plin','transferencia','giro',
                'seguro vehicular','soat','notaria','tramite','apostilla',
                'municipalidad','sunat','reniec','dni','pasaporte',
            ],
            'Tecnologia': [
                'laptop','computadora','electronico','tablet','audifonos',
                'cargador','software','app','programa','monitor','teclado','mouse',
                'celular','smartphone','iphone','samsung','xiaomi','impresora',
                'disco duro','memoria','usb','camara','smartwatch','router',
                'reparacion','tecnico','servicio tecnico',
            ],
            'Ropa': [
                'ropa','camisa','pantalon','zapatos','vestido','polo','zapatillas',
                'tenis','chompa','casaca','cartera','bolsa','mochila','ropa interior',
                'calcetines','medias','gorra','sombrero','cinturon','corbata',
                'saga falabella','ripley','oechsle','zara','h&m','forever21',
            ],
            'Prestamos': [
                'prestamo','cuota','credito','hipoteca','financiamiento',
                'amortizacion','vehicular','interes','deuda','letra','pago deuda',
                'cuota prestamo','banco','financiera','caja',
            ],
            'Tarjetas de Credito': [
                'bcp','interbank','bbva','falabella','ripley','scotiabank',
                'visa','mastercard','tarjeta','tc bcp','tc interbank',
                'pago tarjeta','pago tc','cuota tc',
            ],
        },
        'ingreso': {
            'Salario': [
                'sueldo','salario','pago','quincena','mensual','remuneracion',
                'haberes','nomina','planilla','gratificacion','bonificacion',
                'bono','aguinaldo','liquidacion','cts','utilidades',
                'horas extra','sobresueldo',
            ],
            'Freelance': [
                'proyecto','freelance','trabajo','servicio','consultoria',
                'honorarios','encargo','cliente','factura','boleta honorarios',
                'recibo por honorarios','rph','desarrollo web','diseño',
            ],
            'Inversiones': [
                'dividendo','interes','rendimiento','acciones','cripto','bitcoin',
                'inversion','utilidad','ganancia','forex','trading','fondo',
                'deposito plazo','cuenta ahorro',
            ],
            'Ventas': [
                'venta','vendido','vendi','mercaderia','producto','tienda',
                'marketplace','mercadolibre','olx','facebook marketplace',
            ],
        }
    }

    def __init__(self):
        print("\n[Sistema] Cargando clasificador de categorías...")
        # Pre-cargar categorías en cache al iniciar
        self._cargar_cache()
        print("[Sistema] Clasificador listo.")

    def _cargar_cache(self):
        """Carga las categorías de la BD una sola vez y las guarda en RAM."""
        if ClasificadorIA._cache_categorias is None:
            try:
                from services.category_service import get_all_categories
                ClasificadorIA._cache_categorias = get_all_categories()
                print(f"[Sistema] {len(ClasificadorIA._cache_categorias)} categorías cargadas en cache.")
            except Exception as e:
                print(f"[Sistema] Error cargando categorías: {e}")
                ClasificadorIA._cache_categorias = []

    def _normalizar(self, texto: str) -> str:
        """Convierte a minúsculas y elimina acentos."""
        texto = texto.lower()
        for a, b in [('á','a'),('é','e'),('í','i'),('ó','o'),('ú','u'),('ñ','n')]:
            texto = texto.replace(a, b)
        return texto

    def _buscar_keyword(self, descripcion: str, type_txn: str) -> str | None:
        """Busca categoría por keywords. Retorna nombre de categoría o None."""
        texto = self._normalizar(descripcion)
        mapa = self.KEYWORDS.get(type_txn, {})
        for categoria, palabras in mapa.items():
            for palabra in palabras:
                if palabra in texto:
                    return categoria
        return None

    def categorizar_y_mapear(self, descripcion, type_txn='gasto'):
        """
        Categoriza una descripción y retorna (id_category, description).
        Usa cache en RAM + keywords. Completamente instantáneo.
        """
        # Usar cache (ya cargada al inicio)
        categorias_db = ClasificadorIA._cache_categorias or []

        categorias_principales = [
            c for c in categorias_db
            if c.id_subcategory is None and c.type_category == type_txn
        ]

        nombre_otros = 'otros ingresos' if type_txn == 'ingreso' else 'otros gastos'
        categoria_otros = next(
            (c for c in categorias_principales if c.description.lower() == nombre_otros), None
        )

        # Buscar por keyword
        match = self._buscar_keyword(descripcion, type_txn)
        if match:
            for cat in categorias_principales:
                if cat.description.lower() == match.lower():
                    print(f"   -> [Keyword] '{descripcion}' → '{cat.description}'")
                    return cat.id_category, cat.description

        # Sin match → categoría comodín
        if categoria_otros:
            print(f"   -> [Keyword] '{descripcion}' → '{categoria_otros.description}' (sin match)")
            return categoria_otros.id_category, categoria_otros.description

        return None, "Desconocida"

    def categorizar_y_mapear_subcategoria(self, descripcion, subcategorias_db):
        """
        Categoriza subcategoría por keywords.
        Si no hay match, retorna la primera subcategoría disponible.
        """
        if not subcategorias_db:
            return None, "Sin subcategoria"

        texto = self._normalizar(descripcion)

        # Buscar en el nombre de cada subcategoría
        for sub in subcategorias_db:
            nombre_sub = self._normalizar(sub.description)
            if nombre_sub in texto or texto in nombre_sub:
                return sub.id_category, sub.description

        # Buscar palabras del keyword map en las subcategorías
        for sub in subcategorias_db:
            nombre_sub = self._normalizar(sub.description)
            palabras_sub = nombre_sub.split()
            for palabra in palabras_sub:
                if len(palabra) > 3 and palabra in texto:
                    return sub.id_category, sub.description

        # Sin match → primera subcategoría
        return subcategorias_db[0].id_category, subcategorias_db[0].description

    # Métodos legacy mantenidos por compatibilidad (no usados)
    def clasificar_con_candidatas(self, descripcion, candidatas):
        if not candidatas:
            return None, 0.0
        match = self._buscar_keyword(descripcion, 'gasto') or candidatas[0]
        return match, 1.0
