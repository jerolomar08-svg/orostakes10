import os
import base64
import streamlit as st
import requests
from groq import Groq

st.set_page_config(page_title="Analista Pro - Apuestas & Combinadas", page_icon="⚡", layout="wide")
st.title("⚡ Analista Cuantitativo de Alto Valor & Combinadas (Bet365)")

FOOTBALL_API_KEY = "25dde62359034a75ba0c67c36ef47f62"

groq_key = st.secrets.get("GROQ_API_KEY") if "GROQ_API_KEY" in st.secrets else os.environ.get("GROQ_API_KEY", "")

if not groq_key:
    st.error("⚠️ La clave GROQ_API_KEY no se ha configurado en los Secrets de Streamlit.")
    st.stop()

client = Groq(api_key=groq_key.strip())

def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode('utf-8')

if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

for msg in st.session_state.mensajes:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

uploaded_file = st.file_uploader("📷 Adjunta una captura/ejemplo (boletos, partidos, estadísticas...)", type=["png", "jpg", "jpeg"])

user_input = st.chat_input("Dime algo tipo: ¿A qué le metemos hoy, loco?")

if user_input or uploaded_file:
    prompt_texto = user_input if user_input else "Mira la foto que te he subido y dime a qué le metemos o analízamela."
    
    st.session_state.mensajes.append({"role": "user", "content": prompt_texto})
    with st.chat_message("user"):
        if uploaded_file:
            st.image(uploaded_file, caption="Imagen adjunta", width=300)
        st.write(prompt_texto)

    with st.chat_message("assistant"):
        url = 'https://api.football-data.org/v4/competitions/CL/matches'
        headers = {'X-Auth-Token': FOOTBALL_API_KEY}
        
        try:
            res = requests.get(url, headers=headers, timeout=5)
            datos_partidos = str(res.json().get('matches', []))[:1500] if res.status_code == 200 else "Sin datos directos de API"
        except Exception:
            datos_partidos = "Sin datos directos de API"

        system_prompt = """
        Eres el colega del usuario, un analista deportivo cuantitativo de élite absoluto y tipster experto especializado en Bet365 (Crear Apuesta / Bet Builder). Hablas de forma totalmente natural, cercana e informal (usando expresiones típicas de un amigo como "loco", "hermano", "escúchame", "paga muy bien para lo fácil que entra", "esta cuota está inflada", etc.).

        ANÁLISIS INTERNO EXHAUSTIVO OBLIGATORIO (LO PROCESAS TODO EN TU CABEZA JUGADOR POR JUGADOR Y ENCUENTRO POR ENCUENTRO ANTES DE RESPONDER):
        1. FÚTBOL (MÓDULO TOTAL MICRO-METRIC):
           - REMATES Y TIROS A PUERTA POR JUGADOR: Analizas la media de tiros de cada atacante/extremo/mediapunta, quién prueba desde fuera del área y la línea de tiros a puerta individuales de Bet365.
           - ENFRENTAMIENTOS INDIVIDUALES (H2H JUGADOR VS JUGADOR): Lateral vs. Extremo regateador (ej. Lamine Yamal, Vinícius, Mbappé) -> probabilidades de faltas, tarjetas provocadas y fueras de juego.
           - PARADAS DE PORTERO & GOLES: Disparos concedidos por el rival, paradas esperadas del portero (xG/xS) y lectura de partido abierto (Over/Under de goles tipo +2.5, +3.5 o BTTS).
           - TARJETAS Y CÓRNERS: Perfil del árbitro asignado (promedio tarjetas/partido) + tendencia de ataque por banda para córners asiáticos.
        2. BALONCESTO (NBA / EUROLIGA):
           - Pace (ritmo de posesiones), matchups individuales defensivos por posición, player props (Puntos + Rebotes + Asistencias, Triples anotados) y desgaste/back-to-back.
        3. TENIS (ATP / WTA / CHALLENGER):
           - Adaptación a la superficie (tierra/dura/hierba), % de primer servicio, puntos ganados con 2º saque, desgaste físico en minutos acumulados y H2H histórico.

        ESTRUCTURA DE TU RESPUESTA:
        - Saludo de colega directo al grano proponiendo la jugada.
        - Explicación fluida y contundente de la LÓGICA DE DATOS MICRO (mencionando los tiros a puerta de los jugadores clave, el duelo lateral vs extremo, las paradas esperadas del portero o la tormenta de goles/córners sin soltar teórica aburrida). NO USES TABLAS EN MARKDOWN.
        - Boleto listo para Bet365 con mercados exactos de Crear Apuesta (jugador, remates a puerta, tarjetas, goles, etc.) y sus cuotas individuales.
        - Cuota Total Estimada y Stake Recomendado.
        """

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "system", "content": f"Datos de partidos actualizados: {datos_partidos}"}
        ]

        if uploaded_file:
            base64_image = encode_image(uploaded_file)
            messages.append({
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_texto},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            })
        else:
            messages.append({"role": "user", "content": prompt_texto})

        try:
            completion = client.chat.completions.create(
                model="llama-3.2-11b-vision-preview",
                messages=messages,
                temperature=0.6
            )
            respuesta = completion.choices[0].message.content
            st.write(respuesta)
            st.session_state.mensajes.append({"role": "assistant", "content": respuesta})
        except Exception as e:
            st.error(f"Error en la consulta: {e}")
