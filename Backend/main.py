import re
import os
import nltk
import logging
import numpy as np
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from tensorflow.keras.models import Sequential
from tensorflow.keras.utils import to_categorical
from sklearn.model_selection import train_test_split
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.layers import Embedding, LSTM, Dense, Dropout

load_dotenv()

# Logging básico para depuración de payloads
logging.basicConfig(level=logging.INFO)

from fastapi import FastAPI, Body, HTTPException
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    Date,
    DateTime,
    ForeignKey,
    func,
)
from sqlalchemy.orm import sessionmaker, declarative_base

# ============================================
# 🔹 INICIALIZAR FASTAPI
# ============================================
app = FastAPI(title="Backend IA BERT")

# ============================================
# 🔹 BASE DE DATOS
# ============================================
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_PORT = os.getenv("DB_PORT", "3306")

DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# No usar `check_same_thread` (SQLite); usar ping de pool para MySQL
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ============================================
# 🔹 MODELOS SEGÚN EL DIAGRAMA E-R
# ============================================

class Empleado(Base):
    __tablename__ = "Empleado"

    documento_Identidad = Column(String(20), primary_key=True, index=True)
    tipo_Documento = Column(String(20), nullable=False, default="CC")
    nombre_Completo = Column(String(100), nullable=False)
    genero = Column(String(15))
    empresa = Column(String(100))
    cargo = Column(String(50))
    fecha_Nacimiento = Column(Date)
    edad = Column(Integer)
    correo = Column(String(150))
    hobby = Column(String(100))


class Reporte(Base):
    __tablename__ = "Reporte"

    id_Reporte = Column(Integer, primary_key=True, index=True, autoincrement=True)
    documento_Identidad = Column(
        String(20),
        ForeignKey("Empleado.documento_Identidad"),
        nullable=False,
    )
    nivel_Energia = Column(Integer)
    horas_Sueño_Promedio = Column(Float)
    como_Se_Siente = Column(String(50))
    foto = Column(String(255))
    descripcion = Column(String(255)) 
    fecha_Registro = Column(DateTime, server_default=func.now())

class Resultado(Base):
    __tablename__ = "Resultado"

    id_Resultado = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_Reporte = Column(
        Integer,
        ForeignKey("Reporte.id_Reporte"),
        nullable=False,
        unique=True,  # para que sea 1:1 con Reporte
    )
    emocion_Principal = Column(String(50))
    emocion_Secundaria = Column(String(50))
    descripcion_General = Column(String(255))
    ia_Utilizada = Column(String(100))

# Crear tablas si no existen
Base.metadata.create_all(bind=engine)

# ============================================
# 🔹 IA PROPIA (TU MODELO LSTM)
# ============================================
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')
from nltk.corpus import stopwords

stop_words = set(stopwords.words("spanish"))

def limpiar_texto(texto):
    texto = texto.lower()
    texto = re.sub(r"[^a-záéíóúñü\s]", "", texto)
    texto = " ".join([word for word in texto.split() if word not in stop_words])
    return texto

# ------------- Dataset -------------
data = {
    "texto": [
        "Me siento muy feliz con mi trabajo",
        "Estoy cansado de tanto estrés",
        "Mi equipo de trabajo es excelente",
        "No me gusta cómo nos tratan",
        "Hoy fue un día normal",
        "Estoy muy motivado por el nuevo proyecto",
        "La carga laboral es demasiado alta",
        "Estoy satisfecho con mi jefe",
        "No aguanto más este ambiente laboral",
        "Todo va bien en la empresa",
        "Estoy aburrido",
        "Nada especial hoy",
        "Me siento inspirado y con ganas de aprender",
        "Siento que no puedo con tanta responsabilidad",
        "El apoyo de mis compañeros es increíble",
        "No me siento valorado en mi trabajo",
        "Hoy no tengo ánimos para nada",
        "Estoy contento con los logros alcanzados",
        "Me frustra tener tantas tareas pendientes",
        "Disfruto colaborar en equipo",
        "La presión es demasiada y me agobia",
        "Siento que mi esfuerzo es reconocido",
        "Estoy desmotivado con los cambios recientes",
        "Hoy fue un día tranquilo y sin problemas",
        "Me siento optimista sobre el futuro del proyecto",
        "No me gusta cómo me comunicaron la noticia",
        "Estoy ansioso por cumplir los objetivos",
        "Disfruto aprender cosas nuevas cada día",
        "Me siento frustrado con las metas no cumplidas",
        "Estoy satisfecho con el ambiente laboral",
    ],
    "sentimiento": [
        "positivo", "negativo", "positivo", "negativo", "neutro",
        "positivo", "negativo", "positivo", "negativo", "positivo",
        "neutro", "neutro", "positivo", "negativo", "positivo",
        "negativo", "negativo", "positivo", "negativo", "positivo",
        "negativo", "positivo", "negativo", "neutro", "positivo",
        "negativo", "negativo", "positivo", "negativo", "positivo"
    ]
}

df = pd.DataFrame(data)
df["texto_limpio"] = df["texto"].apply(limpiar_texto)

tokenizer = Tokenizer(num_words=5000, oov_token="<OOV>")
tokenizer.fit_on_texts(df["texto_limpio"])

secuencias = tokenizer.texts_to_sequences(df["texto_limpio"])
max_len = 20
padded = pad_sequences(secuencias, maxlen=max_len)

label_map = {"negativo": 0, "neutro": 1, "positivo": 2}
df["etiqueta"] = df["sentimiento"].map(label_map)
labels = to_categorical(df["etiqueta"])

X_train, X_test, y_train, y_test = train_test_split(
    padded, labels, test_size=0.2, random_state=42, stratify=df["etiqueta"]
)

model = Sequential([
    Embedding(input_dim=5000, output_dim=64),
    LSTM(64, dropout=0.3, recurrent_dropout=0.3),
    Dense(32, activation="relu"),
    Dropout(0.3),
    Dense(3, activation="softmax"),
])

model.compile(loss="categorical_crossentropy", optimizer="adam", metrics=["accuracy"])
model.fit(X_train, y_train, epochs=10, batch_size=2, verbose=0)


def predecir_emociones_texto(payload):
    # Acepta tanto un string (texto) como un dict con campos individuales
    if isinstance(payload, str):
        texto_limpio = limpiar_texto(payload)
    else:
        texto = (
            f"{payload.get('como_se_siente_hoy','')} "
            f"{payload.get('nivel_energia','')} "
            f"{payload.get('calidad_sueno','')} "
            f"{payload.get('horas_sueno_promedio','')} "
            f"{payload.get('frecuencias_ejercicio','')} "
            f"{payload.get('descripcion','')} "
            f"{payload.get('hobby','')}"
        )
        texto_limpio = limpiar_texto(texto)

    seq = tokenizer.texts_to_sequences([texto_limpio])
    padded_seq = pad_sequences(seq, maxlen=max_len)

    pred = model.predict(padded_seq, verbose=0)[0]

    return {
        "negativo": float(pred[0]),
        "neutro": float(pred[1]),
        "positivo": float(pred[2])
    }

# ============================================
# 🔹 HELPERS PARA PARSEAR DATOS
# ============================================
def to_date(fecha_str: str):
    if not fecha_str:
        return None
    try:
        return datetime.strptime(fecha_str, "%Y-%m-%d").date()
    except ValueError:
        return None


def to_int(valor):
    try:
        return int(valor) if valor not in (None, "") else None
    except (TypeError, ValueError):
        return None

def to_float(valor):
    try:
        return float(valor) if valor not in (None, "") else None
    except (TypeError, ValueError):
        return None

# ======================================================
# 🔹 ENDPOINT 1 — GESTIONAR EMPLEADOS
# ======================================================
@app.post("/api/empleados", status_code=201)
def guardar_empleado(payload: dict = Body(...)):
    db = SessionLocal()
    try:
        employee_id = payload.get("employee_id")
        if not employee_id:
            raise HTTPException(status_code=400, detail="employee_id es obligatorio")

        # Mapear posibles nombres de campo que envíe el frontend / n8n
        nombre = (
            payload.get("nombre_completo")
            or payload.get("nombre")
            or payload.get("name")
            or payload.get("full_name")
            or payload.get("nombreCompleto")
        )

        logging.info(f"Guardar empleado payload: employee_id=%s, nombre=%s", employee_id, nombre)

        empleado = (
            db.query(Empleado)
            .filter(Empleado.documento_Identidad == employee_id)
            .first()
        )

        if not empleado:
            # Evitar insertar `NULL` en columnas NOT NULL
            if not nombre:
                raise HTTPException(status_code=400, detail="nombre_completo es obligatorio al crear un empleado")
            empleado = Empleado(
                documento_Identidad=employee_id,
                tipo_Documento=payload.get("tipo_documento", "CC"),
                nombre_Completo=nombre,
                genero=payload.get("genero"),
                empresa=payload.get("empresa"),
                cargo=payload.get("cargo"),
                fecha_Nacimiento=to_date(payload.get("fecha_nacimiento")),
                edad=to_int(payload.get("edad")),
                correo=payload.get("correo"),
                hobby=payload.get("hobby"),
            )
            db.add(empleado)
            db.commit()
            db.refresh(empleado)
            return {"status": "ok", "message": "Empleado creado exitosamente.", "documento_Identidad": empleado.documento_Identidad}
        else:
            # Opcional: actualizar datos básicos (acepta nombres alternativos)
            empleado.nombre_Completo = nombre or empleado.nombre_Completo
            empleado.genero = payload.get("genero", empleado.genero)
            empleado.empresa = payload.get("empresa", empleado.empresa)
            empleado.cargo = payload.get("cargo", empleado.cargo)
            empleado.fecha_Nacimiento = to_date(
                payload.get("fecha_nacimiento")
            ) or empleado.fecha_Nacimiento
            empleado.edad = to_int(payload.get("edad")) or empleado.edad
            empleado.correo = payload.get("correo", empleado.correo)
            empleado.hobby = payload.get("hobby", empleado.hobby)
            db.commit()
            db.refresh(empleado)
            return {"status": "ok", "message": "Empleado actualizado exitosamente.", "documento_Identidad": empleado.documento_Identidad}
    finally:
        db.close()

# ======================================================
# 🔹 ENDPOINT 2 — CREAR REPORTE
# ======================================================
@app.post("/api/reportes", status_code=201)
def guardar_reporte(payload: dict = Body(...)):
    db = SessionLocal()
    try:
        employee_id = payload.get("employee_id")
        if not employee_id:
            raise HTTPException(status_code=400, detail="employee_id es obligatorio")

        # Verificar que el empleado exista
        empleado = db.query(Empleado).filter(Empleado.documento_Identidad == employee_id).first()
        if not empleado:
            raise HTTPException(status_code=404, detail=f"Empleado con ID {employee_id} no encontrado.")

        reporte = Reporte(
            documento_Identidad=employee_id,
            nivel_Energia=to_int(payload.get("nivel_energia")),
            horas_Sueño_Promedio=to_float(payload.get("horas_sueno_promedio")),
            como_Se_Siente=payload.get("como_se_siente_hoy"),
            foto=payload.get("foto"),
            descripcion=payload.get("descripcion"),
        )
        db.add(reporte)
        db.commit()
        db.refresh(reporte)

        return {
            "status": "ok",
            "message": "Reporte guardado exitosamente.",
            "id_reporte": reporte.id_Reporte,
        }
    finally:
        db.close()


# ======================================================
# 🔹 ENDPOINT 3 — IA PROPIA (CLASIFICACIÓN DE TEXTO)
#     (solo devuelve el JSON con la predicción)
# ======================================================
@app.post("/api/clasificar")
def clasificar(payload: dict = Body(...)):
    employee_id = payload.get("employee_id", "")

    # soportar payload que envía un string en 'texto' o un dict con campos
    texto_o_payload = payload.get("texto", payload)
    emociones = predecir_emociones_texto(texto_o_payload)

    return {
        "employee_id": employee_id,
        "source": "ia_propia",
        "emotions": emociones,
    }

# ======================================================
# 🔹 ENDPOINT 4 — GUARDAR RESULTADO DE LA IA
# ======================================================
@app.post("/api/resultados", status_code=201)
def guardar_resultado(payload: dict = Body(...)):
    db = SessionLocal()
    try:
        id_reporte = payload.get("id_reporte")
        emociones = payload.get("emotions")
        ia_utilizada = payload.get("ia_utilizada")

        if not id_reporte or not emociones:
            raise HTTPException(status_code=400, detail="id_reporte y emotions son obligatorios.")

        # Verificar que el reporte exista
        reporte = db.query(Reporte).filter(Reporte.id_Reporte == id_reporte).first()
        if not reporte:
            raise HTTPException(status_code=404, detail=f"Reporte con ID {id_reporte} no encontrado.")

        resultado = Resultado(
            id_Reporte=id_reporte,
            emocion_Principal=max(emociones, key=emociones.get),
            emocion_Secundaria=sorted(emociones, key=emociones.get, reverse=True)[1],
            descripcion_General=f"Análisis de texto con modelo LSTM. Principal: {max(emociones, key=emociones.get)}.",
            ia_Utilizada=ia_utilizada,
        )
        db.add(resultado)
        db.commit()
        db.refresh(resultado)

        return {"status": "ok", "message": "Resultado guardado exitosamente.", "id_resultado": resultado.id_Resultado}
    finally:
        db.close()

# ======================================================
# 🔹 RUN
# ======================================================
# uvicorn backend:app --reload
