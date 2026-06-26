# Asistente Inteligente de Finanzas Personales y Clasificación de Ingresos y Gastos

Este proyecto es una solución backend robusta diseñada para centralizar, automatizar y categorizar inteligentemente los flujos financieros de los usuarios (ingresos y gastos). Utiliza una arquitectura moderna basada en Programación Orientada a Objetos (POO), integración en tiempo real con una base de datos relacional y un módulo de Inteligencia Artificial para la clasificación automática de transacciones.

---

## Características Principales

* **🧠 Clasificación Inteligente con IA (HuggingFace):** Implementación de modelos de procesamiento de lenguaje natural (NLP) para analizar las descripciones de las transacciones y asignarles automáticamente categorías óptimas.
* **📂 Arquitectura Robusta y Mantenible (POO):** Diseño estructurado bajo patrones de software limpios, separando la lógica de negocio en servicios, modelos de datos y controladores independientes.
* **☁️ Base de Datos en la Nube (PostgreSQL + Supabase):** Persistencia relacional segura y escalable conectada directamente a una instancia administrada en la nube mediante Supabase.
* **📊 Gestión Integral de Entidades:** CRUD completo y relacional para la administración de usuarios, categorías personalizadas y registros detallados de transacciones.

---

## Estructura de Directorios

El proyecto sigue una estructura limpia que facilita la escalabilidad y el mantenimiento de la aplicación:

LCD1-PF/
├── .venv/                  # Entorno virtual aislado de Python
├── ai/                     # Módulo de Inteligencia Artificial
│   └── clasificadorIA.py   # Consumo e integración del modelo de HuggingFace
├── database/               # Capa de persistencia y conexión
│   └── connection.py       # Configuración y pool de conexiones a PostgreSQL (Supabase)
├── models/                 # Modelos de datos / Entidades del negocio (POO)
│   ├── category.py
│   ├── transaction.py
│   └── user.py
├── services/               # Capa de servicios / Lógica de negocio
│   ├── category_service.py
│   ├── transaction_service.py
│   └── user_service.py
├── .env                    # Variables de entorno y credenciales sensibles (protegido)
├── .gitignore              # Exclusión de archivos innecesarios en el repositorio
├── main.py                 # Punto de entrada principal para la ejecución del sistema
├── README.md               # Documentación técnica del proyecto
└── requirements.txt        # Dependencias y librerías del ecosistema

---

## Autores
* Gerson Ronaldo Surco Alata - www.linkedin.com/in/gerson-surco-alata-53b42026a<br>
* Rocio del Pilar Apaza Machicao<br>
* Kevin Arnold Martinez Melendes - www.linkedin.com/in/kevinarnoldmartinezmelendes<br>
* Aldair Anthony Valdez Rosas