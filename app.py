
import streamlit as st
import requests
from groq import Groq

st.set_page_config(page_title="Analista Pro - Apuestas & Combinadas", page_icon="⚡", layout="wide")
st.title("⚡ Analista Cuantitativo de Alto Valor & Combinadas")

FOOTBALL_API_KEY = "25dde62359034a75ba0c67c36ef47f62"
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")

client = Groq(api_key=GROQ_API_KEY)

if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

for msg in st.session_state.mensajes:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

user_input = st.chat_input("Pídeme una combinada de cuota alta, análisis de tenis, baloncesto, fútbol o partidos del día...")

if user_input:
    st.session_state.mensajes.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        url = 'https://api.football-data.org/v4/competitions/CL/matches'
        headers = {'X-Auth-Token': FOOTBALL_API_KEY}
        
        try:
            res = requests.get(url, headers=headers, timeout=5)
            datos_partidos = str(res.json().get('matches', []))[:1500] if res.status_code == 200 else "Sin datos directos de API en este instante"
        except Exception:
            datos_partidos = "Sin datos directos de API en este instante"

        system_prompt = """
        Eres un Analista Deportivo Cuantitativo de elite y Tipster Experto especializado en DETECCIÓN DE VALOR, CUOTAS ALTAS (20.00 - 30.00+) Y APUESTAS COMBINADAS en Bet365 y casas globales.

        Tu objetivo es realizar un análisis TÁCTICO, ESTADÍSTICO Y PSICOLÓGICO EXHAUSTIVO en Fútbol, Baloncesto y Tenis para REDUCIR EL RIESGO AL MÍNIMO.

        1. FÚTBOL (Ligas Nacionales, Champions League, Europa League, Conference):
           - TÁCTICA Y MÍSTER: Planteamiento táctico del entrenador, cómo ajusta en liga vs. competiciones europeas, rotaciones previas/posteriores y planteamiento local/visitante.
           - MERCADOS MICRO OBLIGATORIOS: Tarjetas (árbitro asignado + promedio de faltas), Córners (ataques por banda + tendencia defensiva), Remates y Remates a puerta por jugador, Goles (BTTS, Over/Under, en cualquier momento), Paradas de portero y Fueras de juego.

        2. BALONCESTO (NBA, Euroliga, Liga Endesa):
           - RITMO Y EFICIENCIA: Pace (posesiones esperadas), ratings ofensivos/defensivos y fatiga/rotaciones (Back-to-back, viajes).
           - PLAYER PROPS & MATCHUPS: Puntos, Rebotes, Asistencias, Triples anotados/intentados, Robos, Tapones, Pérdidas y cómo defiende el rival esa posición específica.

        3. TENIS (ATP, WTA, Challenger):
           - SUPERFICIE Y MÉTRICAS: Especialización en arcilla, dura o hierba. % de primer servicio, puntos ganados con 1º y 2º saque, ases, dobles faltas y break points convertidos/salvados.
           - HISTORIAL Y PSICOLOGÍA: Desgaste físico (minutos en pista a 3 o 5 sets), balance H2H y rendimiento en tie-breaks.

        INTERACCIÓN Y DEBATE:
        - Si el usuario te rebate una selección o propone un cambio (ej. quitar un gol y poner paradas de portero), evalúa la diferencia exacta en cuota, probabilidad real y reducción de riesgo, recalculando la combinada al instante.

        ESTRUCTURA OBLIGATORIA DE RESPUESTA:
        1. Desglose Técnico y Táctico del Choque (Métricas clave, árbitro, superficie/pace, bajas).
        2. Análisis Selección por Selección (Mercado exacto tipo Bet365, cuota estimada y % de confianza).
        3. CONCLUSIÓN FINAL Y COMBINADA DEFINITIVA:
           - La Combinada Principal (Cuota Total Objetivo ej. 20.00 - 30.00+).
           - Opción de Reducción de Riesgo / Alternativa Cubierta.
           - Recomendación estricta de Stake (1/10 a 10/10).
        """

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "system", "content": f"Datos en tiempo real: {datos_partidos}"},
                {"role": "user", "content": user_input}
            ],
            temperature=0.4
        )

        respuesta = completion.choices[0].message.content
        st.write(respuesta)
        st.session_state.mensajes.append({"role": "assistant", "content": respuesta})