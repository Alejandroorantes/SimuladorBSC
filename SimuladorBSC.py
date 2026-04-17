import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Configuración inicial
st.set_page_config(page_title="Simulador de Estrategia Alex", layout="wide")

# --- ESTILOS PERSONALIZADOS (CSS) ---
st.markdown("""
    <style>
    .main h1 { text-align: center; color: #1E3A8A; font-size: 45px !important; font-weight: bold; }
    .main h2 { color: #1E3A8A; text-align: center; }
    .main h3 { color: #1E3A8A; }
    .stInfo { background-color: #f0f2f6; border-left: 5px solid #1E3A8A; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES DE LÓGICA ESTRATÉGICA ---

def validar_coherencia_canvas_estrategia(canvas_data, est_asp, est_don, est_com, est_que):
    """
    Compara las debilidades marcadas en el Canvas contra el texto de la estrategia
    para verificar si el alumno está abordando los puntos críticos.
    """
    alertas = []
    texto_estrategia = (est_asp + est_don + est_com + est_que).lower()
    
    # Mapeo de palabras clave por categoría de debilidad
    diccionario_soluciones = {
        "procesos": ["automatización", "eficiencia", "agilidad", "optimización", "rpa", "lean", "mejora", "digitalización"],
        "recursos tecnológico": ["tecnología", "nube", "software", "plataforma", "it", "digital", "sistema", "erp", "sap"],
        "recursos humano": ["capacitación", "talento", "reskilling", "cultura", "liderazgo", "equipo", "habilidades"],
        "infraestructura": ["planta", "oficina", "instalaciones", "logística", "distribución", "almacén"],
        "propuesta de valor": ["cliente", "experiencia", "nps", "diferenciación", "innovación", "producto"],
        "socios": ["alianza", "proveedor", "colaboración", "convenio", "integración"]
    }
    
    # Identificar debilidades del Canvas
    debilidades = [k for k, v in canvas_data.items() if v['tipo'] == "Debilidad"]
    
    if not debilidades:
        return ["✅ El diagnóstico no presenta debilidades iniciales. ¡Enfoque en crecimiento!"], 100

    puntos_atendidos = 0
    for deb in debilidades:
        atendida = False
        # Buscar palabras clave de la categoría en el texto de la estrategia
        for categoria, keywords in diccionario_soluciones.items():
            if categoria in deb.lower():
                if any(kw in texto_estrategia for kw in keywords):
                    atendida = True
                    puntos_atendidos += 1
                    break
        
        if not atendida:
            alertas.append(f"⚠️ La debilidad en **{deb}** no parece estar siendo mitigada en tu estrategia.")

    score = int((puntos_atendidos / len(debilidades)) * 100)
    return alertas, score

def calcular_modificador(texto_diagnostico, accion_nombre):
    texto = texto_diagnostico.lower()
    keywords = {
        "1. Automatización Robótica (RPA/AI)": ["procesos", "eficiencia", "costos", "manual", "lento", "operación"],
        "2. Programa de Lealtad Omnicanal": ["clientes", "nps", "fidelidad", "ventas", "servicio", "mercado"],
        "3. I+D: Productos Sustentables": ["innovacion", "producto", "verde", "sustentable", "futuro", "desarrollo"],
        "4. Reskilling de Talento Digital": ["talento", "capacitacion", "gente", "personas", "habilidades", "recursos"],
        "5. Expansión de Mercados": ["crecimiento", "mercado", "global", "ventas", "nuevo", "socios"],
        "6. Smart Logistics": ["logistica", "entrega", "inventario", "cadena", "transporte", "procesos"],
        "7. Ciberseguridad": ["riesgo", "seguridad", "datos", "nube", "ataque", "recursos"]
    }
    if any(word in texto for word in keywords.get(accion_nombre, [])):
        return 1.2
    return 1.0

# --- INICIALIZACIÓN DE ESTADO ---
if 'paso' not in st.session_state:
    st.session_state.paso = 1
    st.session_state.presupuesto = 20.0
    st.session_state.historial = []
    st.session_state.ultimo_impacto = None
    st.session_state.diagnostico_texto = ""
    st.session_state.empresa = ""
    st.session_state.industria = ""
    st.session_state.datos_f1 = {}
    st.session_state.score_coherencia = 0
    st.session_state.kpis = {
        "Financiera": {"ROI": {"actual": 8.0, "ideal": 15.0}, "Margen EBITDA": {"actual": 12.0, "ideal": 18.0}},
        "Clientes": {"Satisfacción (NPS)": {"actual": 65.0, "ideal": 90.0}, "Cuota Mercado": {"actual": 15.0, "ideal": 25.0}},
        "Procesos": {"Eficiencia OEE": {"actual": 70.0, "ideal": 90.0}, "Tiempo Ciclo": {"actual": 15.0, "ideal": 8.0}},
        "Aprendizaje": {"Índice Innovación": {"actual": 3.0, "ideal": 9.0}, "Capacitación": {"actual": 20.0, "ideal": 55.0}}
    }

DECISIONES = {
    "1. Automatización Robótica (RPA/AI)": {"costo": 5.5, "impacto": {"Procesos": {"Eficiencia OEE": 12.0, "Tiempo Ciclo": -3.0}, "Financiera": {"Margen EBITDA": 2.5}}},
    "2. Programa de Lealtad Omnicanal": {"costo": 3.5, "impacto": {"Clientes": {"Satisfacción (NPS)": 18.0, "Cuota Mercado": 4.0}, "Financiera": {"Margen EBITDA": -0.5}}},
    "3. I+D: Productos Sustentables": {"costo": 6.5, "impacto": {"Aprendizaje": {"Índice Innovación": 5.0}, "Clientes": {"Cuota Mercado": 6.0}, "Financiera": {"ROI": -1.5}}},
    "4. Reskilling de Talento Digital": {"costo": 2.5, "impacto": {"Aprendizaje": {"Capacitación": 25.0, "Índice Innovación": 2.0}, "Procesos": {"Eficiencia OEE": 4.0}}},
    "5. Expansión de Mercados": {"costo": 7.5, "impacto": {"Clientes": {"Cuota Mercado": 10.0}, "Financiera": {"ROI": 4.0}, "Procesos": {"Tiempo Ciclo": 2.0}}},
    "6. Smart Logistics": {"costo": 4.0, "impacto": {"Procesos": {"Tiempo Ciclo": -4.0}, "Financiera": {"Margen EBITDA": 3.0}}},
    "7. Ciberseguridad": {"costo": 3.0, "impacto": {"Procesos": {"Eficiencia OEE": 5.0}, "Aprendizaje": {"Índice Innovación": 1.0}}}
}

# --- NAVEGACIÓN ---

# FASE 1: DIAGNÓSTICO
if st.session_state.paso == 1:
    st.markdown("<h1>Simulador de Estrategia de negocios</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Creado por: Dr. Alejandro Orantes Kestler</h3>", unsafe_allow_html=True)
    
    st.header("Fase 1: Diagnóstico Integral de Negocio")
    with st.form("diagnostico_form"):
        c1, c2 = st.columns(2)
        with c1: empresa_input = st.text_input("Nombre de la Organización:")
        with c2: industria_input = st.selectbox("Industria:", ["Agricultura","Agroindustria","Construcción","Manufactura", "Servicios", "Bancario","Alimentos","Tecnología", "Retail"])
        
        campos_canvas = ["Propuesta de Valor", "Procesos/actividades Clave1", "Procesos/Actividades Clave2", "Recursos Tecnologico Clave", "Recursos Humano Clave", "Infraestructura clave", "Socios Clave"]
        respuestas_canvas = {}
        for campo in campos_canvas:
            col_t, col_s = st.columns([3, 1])
            with col_t: txt = st.text_area(f"{campo}:", height=68)
            with col_s: tipo = st.selectbox(f"Situación:", ["Fortaleza", "Debilidad"], key=f"tipo_{campo}")
            respuestas_canvas[campo] = {"texto": txt, "tipo": tipo}
            
        st.divider()
        f_ext_a, f_ext_b = st.columns(2)
        with f_ext_a: opp = st.text_area("Oportunidades (Externo):")
        with f_ext_b: ame = st.text_area("Amenazas (Externo):")
        
        if st.form_submit_button("Siguiente"):
            if empresa_input:
                st.session_state.empresa = empresa_input
                st.session_state.industria = industria_input
                st.session_state.datos_f1 = {"Canvas": respuestas_canvas, "Oportunidades": opp, "Amenazas": ame}
                st.session_state.diagnostico_texto = " ".join([v["texto"] for v in respuestas_canvas.values()]) + f" {opp} {ame}"
                st.session_state.paso = 2
                st.rerun()
            else: st.error("Ingresa el nombre de la empresa.")

# FASE 2: ESTRATEGIA + AUDITORÍA
elif st.session_state.paso == 2:
    st.markdown("<h1>Fase 2: Estrategia Play to Win</h1>", unsafe_allow_html=True)
    with st.form("estrategia_form"):
        asp = st.text_input("¿Cuál es nuestra aspiración ganadora?")
        don = st.text_input("¿Dónde jugaremos?")
        com = st.text_input("¿Cómo ganaremos?")
        que = st.text_input("¿Qué capacidades deben estar presentes?")
        
        btn_validar = st.form_submit_button("Validar y Continuar")
        
        if btn_validar:
            alertas, score = validar_coherencia_canvas_estrategia(st.session_state.datos_f1["Canvas"], asp, don, com, que)
            st.session_state.score_coherencia = score
            st.session_state.aspiracion, st.session_state.donde, st.session_state.como, st.session_state.que = asp, don, com, que
            
            if score < 70 and len(alertas) > 0:
                st.warning(f"🔍 **Auditoría de Estrategia (Coherencia: {score}%):**")
                for a in alertas: st.write(a)
                st.info("Nota: Puedes avanzar, pero tu estrategia no aborda todas las debilidades del diagnóstico.")
            else:
                st.success(f"✅ **Estrategia Sólida (Coherencia: {score}%):** Tu plan aborda los puntos críticos.")
            
            # Pequeña pausa para que vean el mensaje antes de cambiar
            st.session_state.paso = 3
            st.rerun()

# FASE 3: SIMULADOR
elif st.session_state.paso == 3:
    st.markdown(f"<h1>Tablero de Control: {st.session_state.empresa}</h1>", unsafe_allow_html=True)
    col_vis, col_ctrl = st.columns([2, 1])

    with col_vis:
        t_matriz, t_gap = st.tabs(["📋 Matriz BSC", "📊 Análisis Gaps"])
        rows = []
        labels, vals, targets = [], [], []
        for p, kpis in st.session_state.kpis.items():
            for k, d in kpis.items():
                labels.append(k); vals.append(d['actual']); targets.append(d['ideal'])
                status = "🟢" if d['actual'] >= d['ideal'] else "🟡" if d['actual'] >= (d['ideal']*0.8) else "🔴"
                rows.append({"Estado": status, "Perspectiva": p, "KPI": k, "Actual": d['actual'], "Meta": d['ideal']})
        with t_matriz: st.table(pd.DataFrame(rows))
        with t_gap:
            fig, ax = plt.subplots(figsize=(10, 4))
            x = np.arange(len(labels))
            ax.bar(x - 0.2, vals, 0.4, label='Actual', color='#007bff')
            ax.bar(x + 0.2, targets, 0.4, label='Meta', color='#e9ecef', alpha=0.5)
            ax.set_xticks(x); ax.set_xticklabels(labels, rotation=45); ax.legend(); st.pyplot(fig)

    with col_ctrl:
        st.subheader("Inversiones")
        st.metric("Presupuesto Disponible", f"${round(st.session_state.presupuesto, 2)}M")
        seleccion = st.selectbox("Iniciativa:", list(DECISIONES.keys()))
        if st.button("Invertir", use_container_width=True):
            info = DECISIONES[seleccion]
            if st.session_state.presupuesto >= info['costo']:
                mod = calcular_modificador(st.session_state.diagnostico_texto, seleccion)
                st.session_state.presupuesto -= info['costo']
                for p, k_imp in info['impacto'].items():
                    for kn, val in k_imp.items():
                        vf = round(val * mod, 2)
                        st.session_state.kpis[p][kn]['actual'] = round(st.session_state.kpis[p][kn]['actual'] + vf, 2)
                st.session_state.historial.append({"Acción": seleccion, "Presupuesto": f"-${info['costo']}M"})
                st.rerun()
            else: st.error("Presupuesto insuficiente")
        
        st.divider()
        if st.button("📊 GENERAR REPORTE FINAL", type="primary", use_container_width=True):
            st.session_state.paso = 4
            st.rerun()

# FASE 4: REPORTE FINAL CON SCORE DE COHERENCIA
elif st.session_state.paso == 4:
    st.markdown("<h1>Reporte Estratégico Final</h1>", unsafe_allow_html=True)
    
    st.header(f"Organización: {st.session_state.empresa}")
    st.metric("Índice de Coherencia Estratégica", f"{st.session_state.score_coherencia}%")
    
    st.markdown("---")
    st.subheader("II. Diagnóstico vs Estrategia")
    c_f, c_d = st.columns(2)
    with c_f:
        st.markdown("**Capacidades a Potenciar:**")
        for k, v in st.session_state.datos_f1["Canvas"].items():
            if v['tipo'] == "Fortaleza" and v['texto']: st.success(f"**{k}:** {v['texto']}")
    with c_d:
        st.markdown("**Brechas a Cerrar:**")
        for k, v in st.session_state.datos_f1["Canvas"].items():
            if v['tipo'] == "Debilidad" and v['texto']: st.error(f"**{k}:** {v['texto']}")

    st.markdown("---")
    st.subheader("III. Evaluación del Desempeño")
    res_rows = []
    for p, kpis in st.session_state.kpis.items():
        for k, d in kpis.items(): res_rows.append({"Perspectiva": p, "KPI": k, "Resultado": d['actual'], "Meta": d['ideal']})
    st.table(pd.DataFrame(res_rows))

    st.subheader("IV. Reflexión Crítica")
    st.write(f"Tu score de coherencia fue de **{st.session_state.score_coherencia}%**.")
    st.text_area("Basado en tus resultados y el score de coherencia, ¿qué ajustes harías a la estrategia original?", height=150)
    
    if st.button("Finalizar Actividad"): st.balloons()
