import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
import os
import numpy as np

print("Iniciando dashboard...")

# Colores para cada tecnología
color_palette = {
    'Hidraulica': '#1f77b4',
    'Nuclear': '#ff7f0e',
    'CicloCombinado': '#2ca02c',
    'Eolica': '#d62728',
    'SolarFotovoltaica': '#9467bd',
    'SolarTermica': '#8c564b',
    'Carbon': '#7f7f7f',
    'FuelGas': '#bcbd22',
    'TermicaRenovable': '#e377c2',
    'Cogeneracion & Resto': '#17becf',
    'Cogeneracion_PBF': '#17becf',
    'ResiduosNoRen': '#aec7e8',
    'Demanda Real': 'black',
    'Saldo Interc.': 'dodgerblue',
    'Precio': 'forestgreen'
}

# Carga de datos
DATA_DIR = "datos_esios"
PATH_INCIDENTE_DATOS = os.path.join(DATA_DIR, "df_incidente_plot_final_combinado_csv_esios.parquet")
PATH_HORARIO_FINAL = os.path.join(DATA_DIR, "df_calc_horario_final.parquet")

df_horario = None
df_incidente_plot = pd.DataFrame()

try:
    if os.path.exists(PATH_INCIDENTE_DATOS):
        df_incidente_plot = pd.read_parquet(PATH_INCIDENTE_DATOS)
        df_incidente_plot.index = pd.to_datetime(df_incidente_plot.index)
        print(f"DataFrame COMBINADO del incidente cargado. Shape: {df_incidente_plot.shape}")
    else:
        print(f"ERROR CRÍTICO: No se encontró el archivo combinado {PATH_INCIDENTE_DATOS}")

    if os.path.exists(PATH_HORARIO_FINAL):
        df_horario = pd.read_parquet(PATH_HORARIO_FINAL)
        df_horario.index = pd.to_datetime(df_horario.index)
        print(f"DataFrame horario cargado. Shape: {df_horario.shape}")
    else:
        print(f"ERROR CRÍTICO: No se encontró el archivo {PATH_HORARIO_FINAL}")
except Exception as e:
    print(f"Error cargando datos para el dashboard: {e}")

# Configuración del período de análisis
FECHA_INCIDENTE = datetime(2025, 4, 28)
inicio_zoom_incidente_dt_global = pd.Timestamp(FECHA_INCIDENTE - timedelta(days=1))
fin_zoom_incidente_dt_global = pd.Timestamp(FECHA_INCIDENTE + timedelta(hours=23, minutes=59))

if not df_incidente_plot.empty:
    temp_inicio_zoom = inicio_zoom_incidente_dt_global
    temp_fin_zoom = fin_zoom_incidente_dt_global
    
    idx_tz = df_incidente_plot.index.tz
    if idx_tz is None:
        if temp_inicio_zoom.tz is not None: temp_inicio_zoom = temp_inicio_zoom.tz_localize(None)
        if temp_fin_zoom.tz is not None: temp_fin_zoom = temp_fin_zoom.tz_localize(None)
    else:
        if temp_inicio_zoom.tz is None: temp_inicio_zoom = temp_inicio_zoom.tz_localize(idx_tz)
        if temp_fin_zoom.tz is None: temp_fin_zoom = temp_fin_zoom.tz_localize(idx_tz)
    
    df_incidente_plot = df_incidente_plot.loc[temp_inicio_zoom:temp_fin_zoom].copy()
    print(f"Datos filtrados: {len(df_incidente_plot)} filas desde {df_incidente_plot.index.min()} hasta {df_incidente_plot.index.max() if not df_incidente_plot.empty else 'N/A'}.")

cols_generacion_fino_plot = [
    'Hidraulica_MW', 'Nuclear_MW', 'CicloCombinado_MW', 'Eolica_MW',
    'SolarFotovoltaica_MW', 'SolarTermica_MW', 'Carbon_MW', 'FuelGas_MW',
    'TermicaRenovable_MW', 'CogeneracionYResiduos_MW' 
]
cols_generacion_fino_existentes = [col for col in cols_generacion_fino_plot if col in df_incidente_plot.columns and df_incidente_plot[col].notna().any()] if not df_incidente_plot.empty else []
cols_generacion_mix_evolucion_horario = [
    'Hidraulica_MW', 'Nuclear_MW', 'CicloCombinado_MW', 'Eolica_MW',
    'SolarFotovoltaica_MW', 'SolarTermica_MW', 'Carbon_MW',
    'TermicaRenovable_MW', 'Cogeneracion_PBF_MW', 
    'ResiduosNoRen_PBF_MW' 
]

app = dash.Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])
server = app.server

styles = {
    'h2': {'textAlign': 'center', 'color': '#34495e', 'marginBottom': '10px', 'borderBottom': '2px solid #bdc3c7', 'paddingBottom': '10px'},
    'h3': {'color': '#34495e', 'marginTop': '25px', 'marginBottom': '5px', 'borderBottom': '1px solid #eee', 'paddingBottom':'5px'},
    'paragraph': {'textAlign':'justify', 'marginBottom':'15px', 'fontSize':'0.95em', 'color': '#555', 'lineHeight':'1.6'},
    'kpi_box': {'textAlign':'left', 'marginTop':'15px', 'marginBottom':'15px', 'fontSize':'0.9em', 'padding':'15px', 'backgroundColor':'#f9f9f9', 'borderRadius':'5px', 'borderLeft': '5px solid #1f77b4'},
    'kpi_list_item': {'marginBottom': '5px'}
}

app.layout = html.Div(style={'backgroundColor': '#eef1f5', 'padding': '20px', 'fontFamily': 'Arial, sans-serif'}, children=[
    html.Div(style={'backgroundColor': '#2c3e50', 'color': 'white', 'padding': '20px', 'textAlign': 'center', 'borderRadius': '8px', 'marginBottom': '30px'}, children=[
        html.H1(children="Análisis Visual del Mix Energético Español", style={'margin': '0', 'fontSize': '2.2em'}),
        html.P(["Dinámica Previa al Incidente del ", html.Strong("28 de Abril de 2025")], style={'margin': '8px 0 0 0', 'fontSize': '1em'})
    ]),
    html.Div(style={'maxWidth': '1200px', 'margin': 'auto', 'padding': '0 15px'}, children=[
        html.P([
            "Este dashboard explora la dinámica del sistema eléctrico español en los días previos al incidente de 'cero energético' del ",
            html.Strong("28 de abril de 2025"),
            ". Se analiza la evolución histórica del mix de generación y se detalla el comportamiento del sistema durante las horas críticas, ",
            "enfocándose en la respuesta de las diferentes tecnologías, la cobertura de la demanda y los cambios abruptos (rampas) en la generación y la demanda."
        ], style={**styles['paragraph'], 'textAlign': 'center', 'maxWidth': '900px', 'margin': '0 auto 30px auto', 'fontSize': '1.05em'}),
        html.Div(style={'backgroundColor': 'white', 'padding': '25px', 'borderRadius': '8px', 'boxShadow': '0 2px 10px rgba(0,0,0,0.08)', 'marginBottom': '30px'}, children=[
            html.H2("Evolución Histórica del Mix Energético (Media Mensual %)", style=styles['h2']),
            html.P("La siguiente visualización muestra la transformación porcentual del mix energético peninsular durante los últimos 5 años. Permite identificar tendencias a largo plazo, como el crecimiento de fuentes renovables y la disminución de otras más convencionales, ofreciendo un contexto crucial para entender las condiciones previas al incidente.", style=styles['paragraph']),
            dcc.Graph(id='evolucion-mix-horario'),
            html.Div(id='kpi-evolucion-mix-texto', style=styles['kpi_box'])
        ]),
        html.Div(style={'backgroundColor': 'white', 'padding': '25px', 'borderRadius': '8px', 'boxShadow': '0 2px 10px rgba(0,0,0,0.08)', 'marginBottom': '20px'}, children=[
            html.H2(f"Perfil Detallado del Incidente ({inicio_zoom_incidente_dt_global.strftime('%d-%b-%Y')} al {fin_zoom_incidente_dt_global.strftime('%d-%b-%Y')})", style=styles['h2']),
            html.P(f"Análisis con granularidad de 15 minutos de la generación, demanda, intercambios y cobertura durante las horas críticas. El objetivo es entender la secuencia de eventos y las condiciones operativas inmediatamente previas y durante la interrupción del suministro.", style=styles['paragraph']),
            html.H3("Mix de Generación (Absoluto y Porcentual)", style=styles['h3']),
            html.P("El primer gráfico muestra la contribución absoluta (MW) de cada tecnología. El segundo normaliza la generación a 100% para visualizar las proporciones. Observe los patrones horarios y la respuesta general durante la caída de demanda del día 28 de abril alrededor de las 09:00.", style={**styles['paragraph'], 'fontStyle':'italic'}),
            dcc.Graph(id='mix-generacion-incidente'),
            dcc.Graph(id='mix-generacion-incidente-pct'),
            html.H3("Demanda, Intercambios Internacionales y Precio del Mercado", style=styles['h3']),
            html.P("Demanda Real (línea negra), Saldo de Intercambios (azul, positivo=importación) y Precio (€/MWh, verde). La línea roja punteada marca el inicio de la drástica caída de demanda. Estos datos ayudan a entender la presión sobre el sistema y su dependencia externa.", style={**styles['paragraph'], 'fontStyle':'italic'}),
            dcc.Graph(id='demanda-intercambios-precio-incidente'),
            html.Div(id='kpi-incidente-inicio-texto', style=styles['kpi_box']),
            html.H3("Análisis de Rampas (Cambios Bruscos cada 15 min)", style=styles['h3']),
            html.P("Las 'rampas' indican la magnitud del cambio en MW entre intervalos de 15 minutos. Valores altos (positivos o negativos) señalan cambios rápidos que el sistema debe gestionar, especialmente en la demanda y en fuentes variables como la eólica y solar. Estas rampas son cruciales para entender la estabilidad del sistema.", style={**styles['paragraph'], 'fontStyle':'italic'}),
            dcc.Graph(id='rampas-incidente-plot'),
            html.Div(id='kpi-rampas-maximas-texto', style=styles['kpi_box']),
            html.H3("Cobertura de la Demanda", style=styles['h3']),
            html.P("Este gráfico muestra qué porcentaje de la demanda fue cubierta por energías renovables y por energías no emisoras (renovables + nuclear). Valores por encima del 100% indican que la generación de ese tipo superó la demanda interna, lo que puede reflejar exportaciones o la necesidad de gestionar excedentes. Observe la alta cobertura previa al incidente y el efecto de la caída de demanda.", style={**styles['paragraph'], 'fontStyle':'italic'}),
            dcc.Graph(id='cobertura-incidente'),
            html.Div(id='kpi-cobertura-previa-texto', style=styles['kpi_box']),
        ]),
        html.Div(style={'backgroundColor': 'white', 'padding': '25px', 'borderRadius': '8px', 'boxShadow': '0 2px 10px rgba(0,0,0,0.08)', 'marginBottom': '20px'}, children=[
            html.H2("Conclusiones Principales y Respuesta a Preguntas Clave", style=styles['h2']),
            dcc.Markdown("""
                Este análisis visual del mix energético español, centrado en el incidente del 28 de abril de 2025, permite extraer varias conclusiones:

                *   **Perfil del Incidente:**
                    *   La **secuencia de eventos** muestra una operación con alta participación renovable en las horas previas, seguida de una **caída abrupta de la demanda** el 28 de abril alrededor de las 09:00. El mix de generación se ve afectado de forma generalizada, como se observa en la reducción de la producción de la mayoría de las fuentes.
                    *   Se observan **rampas significativas** en la generación eólica y solar en las horas previas, y una rampa negativa muy pronunciada en la demanda durante el inicio del incidente. Las fuentes gestionables como la hidráulica también muestran rampas considerables, indicando su papel en la regulación del sistema.
                *   **Condiciones de Operación Previas:**
                    *   El sistema operaba con **porcentajes de cobertura renovable y no emisora consistentemente altos** (frecuentemente >100%, llegando a picos elevados durante la caída de demanda debido al colapso del consumo) en los días y horas inmediatamente anteriores al evento. Esto indica un sistema con alta capacidad de generación limpia en ese momento.
                    *   El comportamiento del sistema muestra la complejidad de gestionar un mix con alta penetración renovable durante eventos críticos.
                *   **Análisis de Estrés:**
                    *   Los datos permiten observar la respuesta del sistema ante cambios bruscos en la demanda y la participación de diferentes tecnologías en la regulación.
                *   **Evolución Contextual:**
                    *   El mix energético español ha mostrado una **clara tendencia hacia una mayor penetración de fuentes renovables** en los últimos 5 años, con un aumento notable de la eólica y solar, y una disminución del carbón. Esto establece el contexto de un sistema en transición hacia una mayor dependencia de fuentes variables.

                Esta visualización interactiva sirve como herramienta para entender la complejidad de la gestión de un sistema eléctrico con alta penetración renovable y las dinámicas que podrían preceder a un evento crítico, facilitando la exploración de los datos para responder a preguntas clave sobre la resiliencia y la transición energética.
            """, style={**styles['paragraph'], 'textAlign':'left'})
        ])
    ])
])

@app.callback(Output('evolucion-mix-horario', 'figure'), [Input('evolucion-mix-horario', 'id')])
def update_evolucion_mix(_):
    if df_horario is None or df_horario.empty: return go.Figure().update_layout(title_text="Evolución Mix: Datos horarios no disponibles.", title_x=0.5)
    df_evol_mix = df_horario.copy()
    cols_gen_exist_evol = [col for col in cols_generacion_mix_evolucion_horario if col in df_evol_mix.columns and df_evol_mix[col].notna().any()]
    if not cols_gen_exist_evol: return go.Figure().update_layout(title_text="Evolución Mix: Columnas de generación insuficientes.", title_x=0.5)
    df_evol_mix[cols_gen_exist_evol] = df_evol_mix[cols_gen_exist_evol].fillna(0)
    col_total_gen_horario_actual = 'TotalGeneracion_MW' if 'TotalGeneracion_MW' in df_evol_mix.columns else ('TotalGeneracionMix_MW_Horario' if 'TotalGeneracionMix_MW_Horario' in df_evol_mix.columns else None)
    if not col_total_gen_horario_actual or col_total_gen_horario_actual not in df_evol_mix.columns:
        df_evol_mix['CalculatedTotalGen_horario'] = df_evol_mix[cols_gen_exist_evol].sum(axis=1)
        col_total_gen_horario_actual = 'CalculatedTotalGen_horario'
    df_evol_mix_filtrado = df_evol_mix[df_evol_mix[col_total_gen_horario_actual] > 0]
    if df_evol_mix_filtrado.empty: return go.Figure().update_layout(title_text="Evolución Mix: No hay datos con generación positiva.", title_x=0.5)
    df_mix_mensual = df_evol_mix_filtrado.resample('ME')[cols_gen_exist_evol + [col_total_gen_horario_actual]].mean()
    df_mix_mensual = df_mix_mensual[df_mix_mensual[col_total_gen_horario_actual].notna() & (df_mix_mensual[col_total_gen_horario_actual] > 1000)]
    if df_mix_mensual.empty: return go.Figure().update_layout(title_text="Evolución Mix: No hay datos mensuales suficientes tras filtrar.", title_x=0.5)
    fig = go.Figure()
    for col in cols_gen_exist_evol:
        nombre_tecnologia_leyenda = col.replace('_MW', '').replace('_PBF','').replace('_TReal','').replace('ResiduosNoRen','Residuos No Ren.').replace('Cogeneracion','Cogen.')
        if col_total_gen_horario_actual in df_mix_mensual.columns and not df_mix_mensual[col_total_gen_horario_actual].eq(0).all():
            total_gen_series = df_mix_mensual[col_total_gen_horario_actual]
            col_pct_evol = np.where(total_gen_series == 0, 0, (df_mix_mensual[col] / total_gen_series) * 100)
            fig.add_trace(go.Scatter(x=df_mix_mensual.index, y=col_pct_evol, mode='lines', name=nombre_tecnologia_leyenda, stackgroup='one', hoverinfo='x+y+name', line=dict(color=color_palette.get(nombre_tecnologia_leyenda))))
    fig.update_layout(xaxis_title="Mes", yaxis_title="Porcentaje de Generación (%)", yaxis_ticksuffix="%", height=500, legend_title_text='Tecnología', hovermode="x unified", legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="center", x=0.5, font=dict(size=9)))
    return fig

@app.callback(Output('mix-generacion-incidente', 'figure'),[Input('mix-generacion-incidente', 'id')])
def update_mix_generacion_fino(_):
    if df_incidente_plot.empty or not cols_generacion_fino_existentes: return go.Figure().update_layout(title_text="Mix Generación Incidente: Datos no disponibles", title_x=0.5)
    fig = go.Figure()
    df_plot_gen = df_incidente_plot[cols_generacion_fino_existentes].fillna(0)
    for col in cols_generacion_fino_existentes:
        nombre_leyenda = col.replace('_MW','').replace('YResto_TReal',' & Resto').replace('FuelGas','Fuel/Gas')
        fig.add_trace(go.Scatter(x=df_plot_gen.index, y=df_plot_gen[col], hoverinfo='x+y+name', mode='lines', name=nombre_leyenda, stackgroup='one', line=dict(color=color_palette.get(nombre_leyenda))))
    fig.update_layout(title_text=None, xaxis_title="Fecha y Hora", yaxis_title="Generación (MW)", legend_title_text='Tecnología', hovermode="x unified", height=500, legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="center", x=0.5, font=dict(size=9)))
    return fig

@app.callback(Output('mix-generacion-incidente-pct', 'figure'),[Input('mix-generacion-incidente-pct', 'id')])
def update_mix_generacion_fino_pct_simple(_):
    if df_incidente_plot.empty or not cols_generacion_fino_existentes: return go.Figure().update_layout(title_text="Mix Generación (%): Datos no disponibles", title_x=0.5)
    fig_pct = go.Figure()
    df_plot_gen = df_incidente_plot[cols_generacion_fino_existentes].fillna(0) 
    for col in cols_generacion_fino_existentes:
        nombre_leyenda = col.replace('_MW','').replace('YResto_TReal',' & Resto').replace('FuelGas','Fuel/Gas')
        fig_pct.add_trace(go.Scatter(x=df_plot_gen.index, y=df_plot_gen[col], hoverinfo='x+y+name', mode='lines', name=nombre_leyenda, stackgroup='one', line=dict(color=color_palette.get(nombre_leyenda))))
    fig_pct.update_layout(title_text=None, xaxis_title="Fecha y Hora", yaxis_title="Porcentaje de Generación (%)", yaxis_ticksuffix="%", legend_title_text='Tecnología', hovermode="x unified", height=500, legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="center", x=0.5, font=dict(size=9)))
    return fig_pct

@app.callback(Output('demanda-intercambios-precio-incidente', 'figure'),[Input('demanda-intercambios-precio-incidente', 'id')])
def update_demanda_interc_precio_fino(_):
    if df_incidente_plot.empty: return go.Figure().update_layout(title_text="Demanda/Intercambios/Precio: Datos no disponibles", title_x=0.5)
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    if 'DemandaReal_MW' in df_incidente_plot.columns:
        fig.add_trace(go.Scatter(x=df_incidente_plot.index, y=df_incidente_plot['DemandaReal_MW'], name="Demanda Real", line=dict(color=color_palette.get('Demanda Real')),hoverinfo='x+y+name'), secondary_y=False)
    if 'SaldoIntercambios_MW' in df_incidente_plot.columns:
        fig.add_trace(go.Scatter(x=df_incidente_plot.index, y=df_incidente_plot['SaldoIntercambios_MW'], name="Saldo Interc.", line=dict(color=color_palette.get('Saldo Interc.'), dash='dash'),hoverinfo='x+y+name'), secondary_y=True)
    
    ts_incidente_inicio_vline = pd.Timestamp('2025-04-28 12:30:00')
    idx_tz = df_incidente_plot.index.tz
    if idx_tz is not None and ts_incidente_inicio_vline.tz is None: ts_incidente_inicio_vline = ts_incidente_inicio_vline.tz_localize(idx_tz)
    elif idx_tz is None and ts_incidente_inicio_vline.tz is not None: ts_incidente_inicio_vline = ts_incidente_inicio_vline.tz_localize(None)
    
    try: fig.add_vline(x=ts_incidente_inicio_vline, line_dash="dot", line_color="red", annotation_text="Caída Demanda", annotation_position="top left", annotation_font_size=10, annotation_font_color="red")
    except: 
        try: fig.add_vline(x=ts_incidente_inicio_vline, line_dash="dot", line_color="red")
        except Exception as e_vline: print(f"Error añadiendo línea vertical: {e_vline}")

    fig.update_layout(title_text=None, xaxis_title="Fecha y Hora", height=500, hovermode="x unified", legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="center", x=0.5, font=dict(size=10)))
    fig.update_yaxes(title_text="Demanda Real (MW)", secondary_y=False, showgrid=False, color=color_palette.get('Demanda Real'))
    
    y2_range_final, y2_title = None, ""
    if 'SaldoIntercambios_MW' in df_incidente_plot.columns and df_incidente_plot['SaldoIntercambios_MW'].notna().any():
        max_abs_saldo = max(abs(df_incidente_plot['SaldoIntercambios_MW'].min()), abs(df_incidente_plot['SaldoIntercambios_MW'].max())) * 1.2 if df_incidente_plot['SaldoIntercambios_MW'].abs().max() >0 else 1000
        y2_range_final = [-max_abs_saldo, max_abs_saldo]
        y2_title += "Saldo Interc. (MW)"
    if 'PrecioMercado_EUR_MWh' in df_incidente_plot.columns and df_incidente_plot['PrecioMercado_EUR_MWh'].notna().any():
        fig.add_trace(go.Scatter(x=df_incidente_plot.index, y=df_incidente_plot['PrecioMercado_EUR_MWh'], name="Precio", line=dict(color=color_palette.get('Precio'), dash='dot'),hoverinfo='x+y+name'), secondary_y=True)
        if y2_title: y2_title += " / "
        y2_title += "Precio (€/MWh)"
        precio_min = df_incidente_plot['PrecioMercado_EUR_MWh'].min() if pd.notna(df_incidente_plot['PrecioMercado_EUR_MWh'].min()) else 0
        precio_max = df_incidente_plot['PrecioMercado_EUR_MWh'].max() if pd.notna(df_incidente_plot['PrecioMercado_EUR_MWh'].max()) else 100 
        if y2_range_final is None: y2_range_final = [min(0,precio_min * 0.9 if precio_min > 0 else precio_min * 1.1 -1), precio_max * 1.1 if precio_max > 0 else precio_max * 0.9 + 1]
        else: y2_range_final = [min(y2_range_final[0], precio_min * 0.9 if precio_min > 0 else precio_min * 1.1 -1), max(y2_range_final[1], precio_max * 1.1 if precio_max > 0 else precio_max * 0.9 +1 )]
    
    y2_color = 'purple'
    if "Saldo" in y2_title and "Precio" not in y2_title: y2_color = color_palette.get('Saldo Interc.')
    elif "Precio" in y2_title and "Saldo" not in y2_title: y2_color = color_palette.get('Precio')

    fig.update_yaxes(title_text=y2_title if y2_title else "Eje Secundario", secondary_y=True, range=y2_range_final, showgrid=True, gridwidth=0.5, gridcolor='#f0f0f0', color=y2_color)
    return fig

@app.callback(Output('rampas-incidente-plot', 'figure'),[Input('rampas-incidente-plot', 'id')])
def update_rampas_fino(_):
    if df_incidente_plot.empty: return go.Figure().update_layout(title_text="Rampas: Datos no disponibles", title_x=0.5)
    fig_rampas = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.08, subplot_titles=("Rampa Demanda Real", "Rampa Eólica", "Rampa Solar FV"))
    df_rampas_plot = df_incidente_plot.copy()
    max_rampas_info = []
    rampa_cols_map = {'DemandaReal_MW': 'Demanda', 'Eolica_MW': 'Eólica', 'SolarFotovoltaica_MW': 'Solar FV'}
    
    for i, (col_orig, label) in enumerate(rampa_cols_map.items()):
        if col_orig in df_rampas_plot.columns:
            rampa_col_name = f'Rampa_{label.replace(" ","_")}'
            df_rampas_plot[rampa_col_name] = df_rampas_plot[col_orig].diff()
            line_color = color_palette.get(label, 'grey')
            fig_rampas.add_trace(go.Scatter(x=df_rampas_plot.index, y=df_rampas_plot[rampa_col_name], name=f"Rampa {label}", line=dict(color=line_color), hoverinfo='x+y+name'), row=i+1, col=1)
            if df_rampas_plot[rampa_col_name].notna().any():
                idx_max_abs = df_rampas_plot[rampa_col_name].abs().idxmax()
                if pd.notna(idx_max_abs):
                    val_max_rampa = df_rampas_plot.loc[idx_max_abs, rampa_col_name]
                    if pd.notna(val_max_rampa):
                        fig_rampas.add_annotation(x=idx_max_abs, y=val_max_rampa, text=f"Max: {val_max_rampa:.0f}", showarrow=True, arrowhead=1, row=i+1, col=1, font=dict(size=9), ax=20, ay=-20 if val_max_rampa > 0 else 20)
    
    fig_rampas.update_layout(title_text=None, height=600, showlegend=False, hovermode="x unified")
    for i in range(1,4): fig_rampas.update_yaxes(title_text="MW/15min", row=i, col=1)
    return fig_rampas

@app.callback(Output('cobertura-incidente', 'figure'),[Input('cobertura-incidente', 'id')])
def update_cobertura_fino(_):
    cols_cobertura_plot = []
    if 'CoberturaRenovable_pct' in df_incidente_plot.columns: cols_cobertura_plot.append('CoberturaRenovable_pct')
    if 'CoberturaNoEmisora_pct' in df_incidente_plot.columns: cols_cobertura_plot.append('CoberturaNoEmisora_pct')
    if df_incidente_plot.empty or not cols_cobertura_plot: return go.Figure().update_layout(title_text="Cobertura: Datos no disponibles", title_x=0.5)
    fig = go.Figure()
    max_val_cobertura = 0 
    for col in cols_cobertura_plot:
        fig.add_trace(go.Scatter(x=df_incidente_plot.index, y=df_incidente_plot[col], mode='lines', name=col.replace('_pct',' (%)'), hovertemplate='<b>%{x}</b><br>' + col.replace('_pct',' (%)') + ': %{y:.1f}%<extra></extra>'))
        if df_incidente_plot[col].notna().any():
            current_max = df_incidente_plot[col].max()
            if pd.notna(current_max) and np.isfinite(current_max): max_val_cobertura = max(max_val_cobertura, current_max)
    fig.add_hline(y=100, line_dash="dash", line_color="grey", annotation_text="100% Cobertura", annotation_position="bottom right")
    
    ts_pico_cob_anot = pd.Timestamp('2025-04-28 10:00:00') 
    idx_tz = df_incidente_plot.index.tz
    if idx_tz is not None and ts_pico_cob_anot.tz is None: ts_pico_cob_anot = ts_pico_cob_anot.tz_localize(idx_tz)
    elif idx_tz is None and ts_pico_cob_anot.tz is not None: ts_pico_cob_anot = ts_pico_cob_anot.tz_localize(None)

    if not df_incidente_plot.empty and cols_cobertura_plot and ts_pico_cob_anot >= df_incidente_plot.index.min() and ts_pico_cob_anot <= df_incidente_plot.index.max():
        idx_pico_cob_real = df_incidente_plot.index.asof(ts_pico_cob_anot)
        if pd.notna(idx_pico_cob_real) and idx_pico_cob_real in df_incidente_plot.index:
            valor_pico_en_ts = df_incidente_plot.loc[idx_pico_cob_real, cols_cobertura_plot[0]] if cols_cobertura_plot[0] in df_incidente_plot.columns else np.nan
            if pd.notna(valor_pico_en_ts) and valor_pico_en_ts > 150:
                 fig.add_annotation(x=idx_pico_cob_real, y=valor_pico_en_ts, text=f"Pico cobertura >{int(valor_pico_en_ts / 50) * 50}%<br>(Demanda baja)", showarrow=True, arrowhead=1, ax=-40, ay=-50, font=dict(size=10),bgcolor="rgba(255,255,255,0.7)")
    
    final_y_max = 120 
    if max_val_cobertura > 0 and np.isfinite(max_val_cobertura): final_y_max = max(120, max_val_cobertura * 1.05)
    fig.update_layout(title_text=None, xaxis_title="Fecha y Hora", yaxis_title="Cobertura (%)", hovermode="x unified", height=450, yaxis_ticksuffix="%", legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="center", x=0.5, font=dict(size=10)), yaxis_range=[0, final_y_max])
    return fig

@app.callback(Output('kpi-evolucion-mix-texto', 'children'), [Input('evolucion-mix-horario', 'figure')])
def update_kpi_evolucion_mix(_):
    if df_horario is None or df_horario.empty: return html.P("KPIs de evolución no disponibles.", style=styles['kpi_list_item'])
    kpi_evol_texts = [html.Strong("Tendencias Destacadas del Mix (Últimos 5 Años):", style={'display':'block', 'marginBottom':'5px'})]
    if not df_horario.empty:
        primer_año = df_horario.index.min().year
        ultimo_año = df_horario.index.max().year
        if primer_año < ultimo_año :
            df_anual_avg = df_horario.resample('YE').mean(numeric_only=True)
            cols_a_comparar = {'Eolica_MW': 'Eólica', 'SolarFotovoltaica_MW': 'Solar FV', 'Carbon_MW': 'Carbón', 'CicloCombinado_MW': 'Ciclo Combinado'}
            for col, label in cols_a_comparar.items():
                if col in df_anual_avg.columns and not df_anual_avg[col].isnull().all():
                    val_inicio = df_anual_avg[col].iloc[0]
                    val_fin = df_anual_avg[col].iloc[-1]
                    if pd.notna(val_inicio) and pd.notna(val_fin) and val_inicio > 0.1 : 
                        cambio_pct = ((val_fin - val_inicio) / val_inicio) * 100
                        tendencia = "aumentado" if cambio_pct > 5 else ("disminuido" if cambio_pct < -5 else "mantenido estable, con un cambio del")
                        kpi_evol_texts.append(html.Li(f"La generación media de {label} ha {tendencia} ~{abs(cambio_pct):.0f}% entre {primer_año} y {ultimo_año}.", style=styles['kpi_list_item']))
                    elif pd.notna(val_fin):
                         kpi_evol_texts.append(html.Li(f"Generación media de {label} en {ultimo_año}: {val_fin:.0f} MW.", style=styles['kpi_list_item']))
    return html.Ul(kpi_evol_texts, style={'listStyleType': 'disc', 'paddingLeft':'20px'}) if len(kpi_evol_texts) > 1 else html.P("No se pudieron generar KPIs de evolución del mix.", style=styles['kpi_list_item'])

@app.callback(Output('kpi-incidente-inicio-texto', 'children'), [Input('demanda-intercambios-precio-incidente', 'figure')])
def update_kpi_incidente_inicio(_):
    if df_incidente_plot.empty: return html.P("KPIs del incidente no disponibles.", style=styles['kpi_list_item'])
    ts_eval = pd.Timestamp('2025-04-28 08:45:00')
    idx_tz = df_incidente_plot.index.tz
    if idx_tz is not None and ts_eval.tz is None: ts_eval = ts_eval.tz_localize(idx_tz)
    elif idx_tz is None and ts_eval.tz is not None: ts_eval = ts_eval.tz_localize(None)
    
    kpi_elements = [html.Strong(f"Condiciones a las {ts_eval.strftime('%d-%b %H:%M')} (previo al evento):", style={'display':'block', 'marginBottom':'5px'})]
    
    if ts_eval in df_incidente_plot.index:
        data_at_ts = df_incidente_plot.loc[ts_eval]
        if 'DemandaReal_MW' in data_at_ts and pd.notna(data_at_ts['DemandaReal_MW']): kpi_elements.append(html.Li(f"Demanda: {data_at_ts['DemandaReal_MW']:.0f} MW", style=styles['kpi_list_item']))
        if 'SaldoIntercambios_MW' in data_at_ts and pd.notna(data_at_ts['SaldoIntercambios_MW']):
            saldo_val = data_at_ts['SaldoIntercambios_MW']
            tipo_saldo = "Importación" if saldo_val > 0 else ("Exportación" if saldo_val < 0 else "Nulo")
            kpi_elements.append(html.Li(f"Saldo Interc.: {abs(saldo_val):.0f} MW ({tipo_saldo})", style=styles['kpi_list_item']))
        if 'TotalGeneracion_MW' in df_incidente_plot.columns and 'TotalGeneracion_MW' in data_at_ts and pd.notna(data_at_ts['TotalGeneracion_MW']):
            kpi_elements.append(html.Li(f"Gen. Total: {data_at_ts['TotalGeneracion_MW']:.0f} MW", style=styles['kpi_list_item']))
        if 'PrecioMercado_EUR_MWh' in data_at_ts and pd.notna(data_at_ts['PrecioMercado_EUR_MWh']):
            kpi_elements.append(html.Li(f"Precio Mercado: {data_at_ts['PrecioMercado_EUR_MWh']:.2f} €/MWh", style=styles['kpi_list_item']))
    else:
        kpi_elements.append(html.Li("Datos no disponibles para el momento exacto.", style=styles['kpi_list_item']))
    return html.Ul(kpi_elements, style={'listStyleType': 'disc', 'paddingLeft':'20px'}) if len(kpi_elements) > 1 else html.P("Datos para KPIs del incidente no disponibles.", style=styles['kpi_list_item'])

@app.callback(Output('kpi-rampas-maximas-texto', 'children'),[Input('rampas-incidente-plot', 'figure')])
def update_kpi_rampas(_):
    if df_incidente_plot.empty: return html.P("KPIs de rampas no disponibles.", style=styles['kpi_list_item'])
    textos_rampas_html = [html.Strong("Mayores Rampas (MW/15min) en Periodo de Incidente:", style={'display':'block', 'marginBottom':'5px'})]
    cols_para_rampas = {'DemandaReal_MW': 'Demanda', 'Eolica_MW': 'Eólica', 'SolarFotovoltaica_MW': 'Solar FV', 'CicloCombinado_MW':'Ciclo Comb.', 'Hidraulica_MW':'Hidráulica'}
    for col, label in cols_para_rampas.items():
        if col in df_incidente_plot.columns:
            rampa_serie = df_incidente_plot[col].diff()
            if rampa_serie.notna().any():
                idx_max_abs = rampa_serie.abs().idxmax()
                if pd.notna(idx_max_abs): 
                    val_max_rampa = rampa_serie.loc[idx_max_abs]
                    if pd.notna(val_max_rampa):
                        textos_rampas_html.append(html.Li(f"{label}: {val_max_rampa:.0f} MW (el {idx_max_abs.strftime('%d-%b %H:%M')})", style=styles['kpi_list_item']))
    return html.Ul(textos_rampas_html, style={'listStyleType': 'disc', 'paddingLeft':'20px'}) if len(textos_rampas_html) > 1 else html.P("No se calcularon KPIs de rampas.", style=styles['kpi_list_item'])

@app.callback(Output('kpi-cobertura-previa-texto', 'children'),[Input('cobertura-incidente', 'figure')])
def update_kpi_cobertura_previa(_):
    if df_incidente_plot.empty: return html.P("KPIs de cobertura no disponibles.", style=styles['kpi_list_item'])
    ts_eval_cob = pd.Timestamp('2025-04-28 08:45:00')
    idx_tz = df_incidente_plot.index.tz
    if idx_tz is not None and ts_eval_cob.tz is None: ts_eval_cob = ts_eval_cob.tz_localize(idx_tz)
    elif idx_tz is None and ts_eval_cob.tz is not None: ts_eval_cob = ts_eval_cob.tz_localize(None)
    
    kpi_cob_texts = [html.Strong(f"Condiciones de Cobertura ({ts_eval_cob.strftime('%d-%b %H:%M')} - Previo al Evento):", style={'display':'block', 'marginBottom':'5px'})]
    
    if ts_eval_cob in df_incidente_plot.index:
        data_at_ts_cob = df_incidente_plot.loc[ts_eval_cob]
        if 'CoberturaRenovable_pct' in data_at_ts_cob and pd.notna(data_at_ts_cob['CoberturaRenovable_pct']):
            kpi_cob_texts.append(html.Li(f"Cobertura Renovable: {data_at_ts_cob['CoberturaRenovable_pct']:.1f}%", style=styles['kpi_list_item']))
        if 'CoberturaNoEmisora_pct' in data_at_ts_cob and pd.notna(data_at_ts_cob['CoberturaNoEmisora_pct']):
            kpi_cob_texts.append(html.Li(f"Cobertura No Emisora: {data_at_ts_cob['CoberturaNoEmisora_pct']:.1f}%", style=styles['kpi_list_item']))
    else: 
        idx_mas_cercano_cob = df_incidente_plot.index.asof(ts_eval_cob)
        if pd.notna(idx_mas_cercano_cob) and idx_mas_cercano_cob in df_incidente_plot.index:
            data_at_ts_cob = df_incidente_plot.loc[idx_mas_cercano_cob]
            kpi_cob_texts = [html.Strong(f"Condiciones de Cobertura ({idx_mas_cercano_cob.strftime('%d-%b %H:%M')} - Previo al Evento):", style={'display':'block', 'marginBottom':'5px'})]
            if 'CoberturaRenovable_pct' in data_at_ts_cob and pd.notna(data_at_ts_cob['CoberturaRenovable_pct']):
                kpi_cob_texts.append(html.Li(f"Cobertura Renovable: {data_at_ts_cob['CoberturaRenovable_pct']:.1f}%", style=styles['kpi_list_item']))
            if 'CoberturaNoEmisora_pct' in data_at_ts_cob and pd.notna(data_at_ts_cob['CoberturaNoEmisora_pct']):
                kpi_cob_texts.append(html.Li(f"Cobertura No Emisora: {data_at_ts_cob['CoberturaNoEmisora_pct']:.1f}%", style=styles['kpi_list_item']))
        else:
            kpi_cob_texts.append(html.Li("Datos no disponibles para el momento exacto.", style=styles['kpi_list_item']))
            
    return html.Ul(kpi_cob_texts, style={'listStyleType': 'disc', 'paddingLeft':'20px'}) if len(kpi_cob_texts) > 1 else html.P("Datos de cobertura previa no disponibles.", style=styles['kpi_list_item'])

if __name__ == '__main__':
    data_loaded_correctly = True
    if df_incidente_plot.empty:
        print("ERROR CRÍTICO: df_incidente_plot está vacío.")
        data_loaded_correctly = False
    if df_horario is None or df_horario.empty:
        print("ERROR CRÍTICO: df_horario no se cargó.")
        data_loaded_correctly = False
    
    if data_loaded_correctly:
        print("Iniciando servidor Dash...")
        app.run(debug=True)
    else:
        print("El dashboard no puede iniciarse debido a la falta de datos críticos.")

server = app.server