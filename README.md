# 📘 README — SentIA

## Nombre del proyecto

**SentIA** – Sistema de Análisis Emocional Inteligente

---

## Descripción

SentIA es un sistema de análisis emocional basado en inteligencia artificial que integra datos personales, hábitos y fotografías faciales para generar reportes emocionales automatizados. El sistema combina modelos propios y externos (Gemini, ChatGPT) para analizar texto e imágenes y produce un **perfil emocional completo** para cada usuario.

Tecnologías utilizadas:

* **Frontend:** React (formulario web)
* **Orquestador:** n8n (gestión del flujo de datos)
* **Backend:** FastAPI (procesamiento de datos, ejecución del algoritmo IA, almacenamiento)
* **Base de datos:** PostgreSQL/MySQL

---

## Características principales

* Captura de datos personales, hábitos y emociones del usuario
* Procesamiento multimodal: texto + imagen + hábitos
* Análisis con modelo propio SentIA y APIs externas (Gemini, ChatGPT)
* Generación de reportes emocionales completos
* Persistencia de datos en base de datos
* Integración con n8n para automatización de flujos
* Gestión de errores y validaciones de entrada

---

## Requisitos del sistema

* Python 3.12+
* Node.js 20+
* FastAPI
* React 18+
* n8n
* ngrok
* PostgreSQL o MySQL
* Acceso a API de Gemini y ChatGPT

---

## Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/tuusuario/sentia.git
cd sentia
```

### 2. Crear entorno virtual (backend)

```bash
python -m venv venv
source venv/bin/activate  # Linux / Mac
venv\Scripts\activate     # Windows
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Crea un archivo `.env` con tus credenciales:

```env
DB_USER=tu_usuario
DB_PASSWORD=tu_contraseña
DB_NAME=nombre_base_de_datos
DB_HOST=localhost
API_KEY_GEMINI=tu_api_key
API_KEY_CHATGPT=tu_api_key
```

### 5. Inicializar la base de datos

```bash
python manage.py create_db
```

### 6. Ejecutar backend

```bash
uvicorn main:app --reload
```

### 7. Ejecutar frontend

```bash
cd frontend
npm install
npm start
```

---

## Uso

1. Accede al formulario web (React).
2. Completa los datos requeridos y sube la foto.
3. Envía el formulario.
4. El backend procesa los datos con SentIA y APIs externas.
5. El sistema devuelve un reporte emocional al usuario y guarda la información en la base de datos.

---

## Estructura de directorios sugerida

```
SentIA/
├─ backend/
│  ├─ main.py
│  ├─ models/
│  ├─ routes/
│  ├─ services/
│  ├─ utils/
│  ├─ requirements.txt
├─ frontend/
│  ├─ src/
│  │  ├─ components/
│  │  ├─ pages/
│  │  ├─ services/
│  ├─ package.json
├─ n8n/
│  ├─ workflows/
├─ README.md
├─ .env
```

---

## Dependencias principales

* FastAPI
* SQLAlchemy
* Pydantic
* Requests
* Numpy / Pandas
* NLTK / Spacy
* Uvicorn

---

## Contribución

1. Haz un fork del proyecto
2. Crea una rama nueva: `git checkout -b feature/nueva-funcionalidad`
3. Realiza tus cambios y haz commit
4. Envía un pull request explicando las modificaciones



---

## Licencia

MIT License — ver archivo `LICENSE` para más detalles.
