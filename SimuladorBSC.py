import ipywidgets as widgets
from IPython.display import display, clear_output, HTML
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import copy # Import copy module for deep copy

class SimuladorCompleto:
    def __init__(self):
        self.output = widgets.Output()
        self.summary_output = widgets.Output() # NEW: Dedicated output for summary
        self.presupuesto = 20.0
        self.estrategia_definida = {}
        self.current_view_type = "tabla" # New attribute to keep track of the current view

        # Configuración inicial de KPIs (Estado Base)
        self.kpis = {
            "Financiera": {
                "ROI": {"actual": 8.0, "min": 7.0, "medio": 10.0, "ideal": 15.0, "unit": "%"},
                "Margen EBITDA": {"actual": 12.0, "min": 10.0, "medio": 14.0, "ideal": 18.0, "unit": "%"}
            },
            "Clientes": {
                "Satisfacción (NPS)": {"actual": 65.0, "min": 60.0, "medio": 75.0, "ideal": 90.0, "unit": "pts"},
                "Cuota Mercado": {"actual": 15.0, "min": 14.0, "medio": 18.0, "ideal": 25.0, "unit": "%"}
            },
            "Procesos": {
                "Eficiencia OEE": {"actual": 70.0, "min": 68.0, "medio": 80.0, "ideal": 90.0, "unit": "%"},
                "Tiempo Ciclo": {"actual": 15.0, "min": 16.0, "medio": 12.0, "ideal": 8.0, "unit": "días"}
            },
            "Aprendizaje": {
                "Índice Innovación": {"actual": 3.0, "min": 2.0, "medio": 5.0, "ideal": 9.0, "unit": "proy"},
                "Capacitación": {"actual": 20.0, "min": 15.0, "medio": 35.0, "ideal": 55.0, "unit": "hrs"}
            }
        }
        self.initial_kpis = copy.deepcopy(self.kpis) # Store initial state for reset
        self.iniciar_diagnostico()

    def iniciar_diagnostico(self):
        with self.output:
            clear_output()
            display(HTML("<h1 style='color:#1a237e;'>Fase 1: Diagnóstico y Análisis</h1>"))

            # Formulario de Diagnóstico
            self.in_empresa = widgets.Text(description="Empresa:", placeholder="Nombre")
            self.in_industria = widgets.Dropdown(options=['Manufactura/CPG', 'Servicios', 'Tecnología', 'Retail'], description="Industria:")
            self.in_canvas = widgets.Textarea(description="Canvas (VP):", placeholder="Propuesta de valor clave")
            self.in_porter = widgets.Textarea(description="Cadena Valor:", placeholder="Fortalezas y debilidades en procesos")
            self.in_foda = widgets.Textarea(description="FODA/PESTEL:", placeholder="Variables críticas del entorno")

            btn_play_to_win = widgets.Button(description="Siguiente: Play to Win", button_style="primary")
            btn_play_to_win.on_click(self.fase_play_to_win)

            display(widgets.VBox([self.in_empresa, self.in_industria, self.in_canvas, self.in_porter, self.in_foda, btn_play_to_win]))

    def fase_play_to_win(self, b):
        with self.output:
            clear_output()
            display(HTML("<h1 style='color:#1a237e;'>Fase 2: Play to Win (Estrategia)</h1>"))

            self.in_donde = widgets.Text(description="¿Dónde jugar?", placeholder="Mercado, Clientes, Canales")
            self.in_como = widgets.Text(description="¿Cómo ganar?", placeholder="Ventaja competitiva (Diferenciación/Costos)")
            self.in_capacidades = widgets.Textarea(description="Capacidades:", placeholder="¿Qué sistemas y talento requerimos?")
            self.in_gestion = widgets.Textarea(description="Gestión:", placeholder="¿Qué sistemas de medición requerimos?")

            btn_finalizar = widgets.Button(description="Generar Estrategia y BSC", button_style="success")
            btn_finalizar.on_click(self.inicializar_simulador)

            display(widgets.VBox([self.in_donde, self.in_como, self.in_capacidades, self.in_gestion, btn_finalizar]))

    def inicializar_simulador(self, b):
        self.estrategia_definida = {
            "nombre": self.in_empresa.value,
            "como": self.in_como.value,
            "donde": self.in_donde.value
        }
        self.mostrar_interfaz_control()

    def mostrar_interfaz_control(self):
        with self.output:
            clear_output()
            display(HTML(f"<h2>Tablero de Control Estratégico: {self.estrategia_definida['nombre']}</h2>"))
            display(HTML(f"<b>Estrategia:</b> Ganaremos en {self.estrategia_definida['donde']} mediante {self.estrategia_definida['como']}</b>"))

            # Selector de Vistas
            self.btn_tabla = widgets.Button(description="📋 Matriz BSC", button_style="info")
            self.btn_barras = widgets.Button(description="📊 Barras (Gap)", button_style="info")
            self.btn_radar = widgets.Button(description="🕸 Radar (Balance)", button_style="info")
            self.btn_reset = widgets.Button(description="🔄 Resetear Decisiones", button_style="danger") # New Reset Button

            self.btn_tabla.on_click(lambda x: self.set_view_and_render("tabla"))
            self.btn_barras.on_click(lambda x: self.set_view_and_render("barras"))
            self.btn_radar.on_click(lambda x: self.set_view_and_render("radar"))
            self.btn_reset.on_click(self.reset_decisiones) # Link reset button

            display(widgets.HBox([self.btn_tabla, self.btn_barras, self.btn_radar, self.btn_reset])) # Add reset button to display

            # NEW: Display the summary output widget
            display(HTML("<h3>Resumen de Impacto de Decisiones</h3>"))
            display(self.summary_output)

            self.cont_visual = widgets.Output()
            display(self.cont_visual)

            # Panel de Decisiones (8 opciones de simulación)
            self.mostrar_panel_decisiones()
            self.render_contenido(self.current_view_type) # Render the initial or last active view

    def set_view_and_render(self, view_type):
        self.current_view_type = view_type
        self.render_contenido(view_type)

    def render_contenido(self, tipo):
        with self.cont_visual:
            clear_output()
            if tipo == "tabla":
                data = []
                for p, kpis in self.kpis.items():
                    for k, d in kpis.items():
                        data.append({"Perspectiva": p, "KPI": k, "Mínimo": d['min'], "Medio": d['medio'], "Ideal": d['ideal'], "Actual": f"<b>{d['actual']}</b>", "Unidad": d['unit']})
                display(HTML(pd.DataFrame(data).to_html(escape=False, index=False)))
            elif tipo == "barras":
                self.plot_barras()
            elif tipo == "radar":
                self.plot_radar()

    def plot_barras(self):
        labels, vals, targets = [], [], []
        for p in self.kpis:
            for k, d in self.kpis[p].items():
                labels.append(k)
                vals.append(d['actual'])
                targets.append(d['ideal'])

        x = np.arange(len(labels))
        width = 0.4

        plt.figure(figsize=(12, 6))
        plt.bar(x - width/2, vals, width, label='Actual', color='skyblue')
        plt.bar(x + width/2, targets, width, label='Ideal', color='lightcoral', alpha=0.7)

        plt.ylabel('Valor')
        plt.title('Comparación de KPIs: Actual vs. Ideal')
        plt.xticks(x, labels, rotation=45, ha='right')
        plt.legend()
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.show()

    def mostrar_panel_decisiones(self):
        # Use the global DECISIONES variable (assuming it's loaded elsewhere)
        global DECISIONES # Declare global to access it

        with self.output:
            display(HTML("<h3>Panel de Decisiones Estratégicas</h3>"))

            # Corrected: Display names, return IDs
            decision_options = {d['nombre']: d_id for d_id, d in DECISIONES.items()}
            self.decision_dropdown = widgets.Dropdown(
                options=decision_options,
                description='Seleccionar Decisión:'
            )
            self.btn_aplicar_decision = widgets.Button(description="Aplicar Decisión", button_style="warning")
            self.btn_aplicar_decision.on_click(self.aplicar_decision)

            display(widgets.VBox([self.decision_dropdown, self.btn_aplicar_decision]))

    def aplicar_decision(self, b):
        global DECISIONES # Declare global to access it

        selected_decision_id = self.decision_dropdown.value
        decision_info = DECISIONES[selected_decision_id]

        # Capture KPIs state before applying decision
        kpis_snapshot_before_decision = copy.deepcopy(self.kpis)

        # NEW: Display decision info and summary in dedicated output
        with self.summary_output:
            clear_output() # Clear previous summary
            display(HTML(f"<h4>Decisión Aplicada: {decision_info['nombre']}</h4>"))
            display(HTML(f"<p>{decision_info['descripcion']}</p>"))
            display(HTML(f"<p><b>Costo:</b> ${decision_info['costo']}M</p>"))

        with self.cont_visual: # Only update the main visualization widget
            # Simulate impact on KPIs
            for kpi_category, impacts in decision_info['impacto'].items():
                for kpi_name, impact_value in impacts.items():
                    if kpi_category in self.kpis and kpi_name in self.kpis[kpi_category]:
                        self.kpis[kpi_category][kpi_name]['actual'] += impact_value
                        # The individual impact lines are now handled by the summary

            # Display the impact summary in summary_output (already handled above)
            # but we still need to generate it, so it can be passed to the summary_output
            with self.summary_output:
                display(self.generar_resumen_impacto(kpis_snapshot_before_decision, self.kpis, decision_info))

            # Re-render the current BSC view to show changes
            self.render_contenido(self.current_view_type)

    def reset_decisiones(self, b):
        # Reset KPIs to their initial state
        self.kpis = copy.deepcopy(self.initial_kpis)
        with self.output:
            clear_output(wait=True)
            # Also clear the summary output
            with self.summary_output:
                clear_output()
            display(HTML("<h3>KPIs reseteados a su estado inicial.</h3>"))
            self.mostrar_interfaz_control()

    def plot_radar(self):
        # Prepare data for radar chart
        categories = []
        actual_values = []
        ideal_values = []

        for p, kpis in self.kpis.items():
            for k, d in kpis.items():
                categories.append(k)
                actual_values.append(d['actual'])
                ideal_values.append(d['ideal'])

        num_vars = len(categories)

        # Calculate angle for each axis
        angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()

        # The plot is circular, so we need to "complete the loop"
        actual_values = actual_values + actual_values[:1]
        ideal_values = ideal_values + ideal_values[:1]
        angles = angles + angles[:1]

        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
        ax.fill(angles, ideal_values, color='red', alpha=0.25, label='Ideal')
        ax.plot(angles, ideal_values, color='red', linewidth=2)
        ax.fill(angles, actual_values, color='blue', alpha=0.25, label='Actual')
        ax.plot(angles, actual_values, color='blue', linewidth=2)

        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)

        # Draw axis lines for each angle and label
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories)

        # Determine appropriate r-limits and ticks dynamically
        all_values = np.array(actual_values[:-1] + ideal_values[:-1])
        r_min = 0
        r_max = all_values.max() * 1.2
        if r_max == 0: r_max = 100

        ax.set_rlabel_position(0)
        ticks = np.linspace(r_min, r_max, 5)
        ax.set_yticks(ticks)
        ax.set_yticklabels([f'{tick:.0f}' for tick in ticks], color="gray", size=7)
        ax.set_ylim(r_min, r_max)

        ax.set_title('Balance de KPIs (Actual vs. Ideal)', va='bottom')
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
        plt.tight_layout()
        plt.show()

    def generar_resumen_impacto(self, kpis_before_decision, kpis_after_decision, decision_info):
        """
        Genera un resumen del impacto de la decisión en los KPIs.
        Compara el estado de los KPIs antes y después de la decisión.
        """
        summary_data = []
        for p, kpis in kpis_after_decision.items():
            for k, d_after in kpis.items():
                d_before = kpis_before_decision[p][k]
                diff = d_after['actual'] - d_before['actual']
                if diff != 0:
                    summary_data.append({
                        "Perspectiva": p,
                        "KPI": k,
                        "Valor Anterior": f"{d_before['actual']:.1f}{d_before['unit']}",
                        "Valor Actual": f"{d_after['actual']:.1f}{d_after['unit']}",
                        "Impacto": f"{'+' if diff > 0 else ''}{diff:.1f}{d_after['unit']}"
                    })

        if not summary_data:
            return HTML(f"<p>La decisión <b>{decision_info['nombre']}</b> no tuvo un impacto significativo directo en los KPIs.</p>")

        summary_df = pd.DataFrame(summary_data)
        html_summary = f"""
        <h4 style='color:#3f51b5;'>Resumen de Impacto de la Decisión: {decision_info['nombre']}</h4>
        <p>Costo de la decisión: <b>${decision_info['costo']}M</b></p>
        {summary_df.to_html(escape=False, index=False)}
        """
        return HTML(html_summary)
# SimuladorBSC
