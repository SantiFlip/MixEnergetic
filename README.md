# Análisis Visual del Mix Energético Español

Dashboard interactivo que analiza la dinámica del sistema eléctrico español en los días previos al incidente del 28 de abril de 2025.

## Descripción

Este proyecto visualiza:
- Evolución histórica del mix energético (media mensual %)
- Perfil detallado del incidente con granularidad de 15 minutos
- Análisis de rampas (cambios bruscos)
- Cobertura de la demanda por fuentes renovables

## Tecnologías utilizadas

- Python
- Dash & Plotly
- Pandas & NumPy

## Instalación local

```bash
pip install -r requirements.txt
python dashboard_app.py
```

## Licencia

MIT License - Ver archivo LICENSE para más detalles.

## Datos

Los datos utilizados provienen de fuentes públicas del sistema eléctrico español y están procesados para el análisis del período específico del incidente.

## 📋 Descripción del Proyecto

Este proyecto analiza el mix energético español utilizando datos de la API e-sios de Red Eléctrica de España (REE), con un enfoque específico en la dinámica energética previa a un hipotético "incidente de cero energético" el 28 de abril de 2025.

### 🎯 Objetivos Principales

1. **Análisis Temporal:** Examinar la evolución del mix energético español (2022-2025)
2. **Análisis Comparativo:** Identificar patrones y anomalías en la generación energética
3. **Contextualización:** Analizar las condiciones previas al hipotético incidente
4. **Visualización Interactiva:** Crear un dashboard que permita explorar los datos de forma intuitiva

## 🛠️ Tecnologías Utilizadas

- **Python 3.8+**
- **Pandas** - Manipulación y análisis de datos
- **Plotly** - Visualizaciones interactivas
- **Dash** - Dashboard web interactivo
- **Requests** - Consumo de API REST
- **API e-sios** - Datos oficiales de REE

## 📁 Estructura del Proyecto

```
├── README.md
├── requirements.txt
├── config.py                    # Configuración del proyecto
├── esios_api.py                 # Módulo para API e-sios
├── 01_exploracion_datos.py      # Exploración inicial
├── env_example.txt              # Ejemplo de variables de entorno
├── data/
│   ├── raw/                     # Datos sin procesar
│   └── processed/               # Datos procesados
├── visualizations/              # Código de visualizaciones
└── dashboard/                   # Aplicación Dash
```

## 🚀 Instalación y Configuración

### 1. Clonar el repositorio
```bash
git clone [url-del-repositorio]
cd Practica2_VisualizacionDatos
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Configurar token de API
1. Solicitar token personal en [e-sios REE](https://www.esios.ree.es/es/pagina/api)
2. Crear archivo `.env` basado en `env_example.txt`
3. Agregar tu token:
```bash
ESIOS_TOKEN=tu_token_personal_aqui
```

### 4. Probar la conexión
```bash
python 01_exploracion_datos.py
```

## 📊 Datos y Variables Clave

### Fuente de Datos
- **API e-sios** de Red Eléctrica de España
- **Período:** 2022-2025 (hasta 27 de abril)
- **Granularidad:** Datos horarios
- **Actualización:** Tiempo real

### Variables Principales
- **Demanda eléctrica nacional**
- **Generación por tecnologías:**
  - Solar fotovoltaica
  - Eólica
  - Hidráulica
  - Nuclear
  - Ciclo combinado (gas)
  - Carbón
- **Precios del mercado eléctrico**
- **Intercambios internacionales**
- **Emisiones de CO2**

## 🔍 Preguntas de Investigación

### 1. Perfil del Incidente (28 de abril de 2025)
- ¿Qué condiciones meteorológicas y de demanda precedieron al incidente?
- ¿Cuál era el estado del mix energético en las 24-48 horas previas?

### 2. Análisis Comparativo
- ¿Cómo se compara el 28 de abril con fechas similares en años anteriores?
- ¿Qué tecnologías mostraron mayor variabilidad en el período?

### 3. Análisis de Estrés del Sistema
- ¿Cuáles fueron los momentos de mayor dependencia de energías no renovables?
- ¿Qué correlaciones existen entre precio, demanda y mix energético?

### 4. Evolución Contextual
- ¿Cómo ha evolucionado la penetración de renovables (2022-2025)?
- ¿Qué tendencias se observan en la estabilidad del suministro?

## 📈 Metodología

### Fase 1: Obtención y Limpieza de Datos
1. Exploración de indicadores disponibles en API e-sios
2. Extracción de datos históricos (3+ años)
3. Limpieza y preprocesamiento
4. Análisis exploratorio de datos (EDA)

### Fase 2: Análisis y Storytelling
1. Identificación de patrones y anomalías
2. Análisis comparativo temporal
3. Definición de narrativa visual
4. Diseño de estructura del dashboard

### Fase 3: Desarrollo de Visualizaciones
1. Gráficos de series temporales interactivos
2. Mapas de calor para correlaciones
3. Gráficos de área apilada para mix energético
4. Indicadores clave de rendimiento (KPIs)

### Fase 4: Dashboard Interactivo
1. Desarrollo con Dash/Plotly
2. Implementación de filtros y controles
3. Optimización de rendimiento
4. Testing y refinamiento

## 🎨 Características de la Visualización

### Interactividad
- **Filtros temporales:** Selección de períodos específicos
- **Filtros tecnológicos:** Activar/desactivar fuentes de energía
- **Zoom y pan:** Exploración detallada de períodos
- **Tooltips informativos:** Datos contextuales al hover

### Accesibilidad
- **Paleta de colores accesible** (contraste adecuado)
- **Textos descriptivos** para lectores de pantalla
- **Navegación por teclado**
- **Responsive design** para dispositivos móviles

### Diseño Visual
- **Consistencia:** Esquema de colores profesional
- **Claridad:** Jerarquía visual clara
- **Minimalismo:** Enfoque en los datos esenciales
- **Marca:** Identidad visual cohesiva

## 📋 Uso de IA en el Proyecto

Este proyecto ha sido desarrollado con asistencia de IA (Claude Sonnet) para:

### Consultas Realizadas
1. **Estructura del proyecto:** Organización de archivos y módulos
2. **Desarrollo de API:** Funciones para conectar con e-sios
3. **Análisis de datos:** Estrategias de EDA y preprocesamiento
4. **Visualización:** Mejores prácticas con Plotly/Dash

### Proceso de Revisión
- Cada sugerencia de IA fue revisada y adaptada
- El código fue probado y optimizado manualmente
- Las decisiones de diseño fueron validadas con datos reales
- La documentación fue personalizada para el proyecto específico

## 🚀 Próximos Pasos

1. **Ejecutar exploración inicial:** `python 01_exploracion_datos.py`
2. **Identificar indicadores clave** basados en resultados
3. **Desarrollar funciones de extracción completa**
4. **Crear análisis exploratorio de datos**
5. **Diseñar y desarrollar dashboard**
6. **Preparar presentación y vídeo explicativo**

## 📄 Licencia

Este proyecto está bajo licencia MIT - ver el archivo LICENSE para detalles.

## 📞 Contacto

**Santiago Tomás Nadal**  
Estudiante de Ciencia de Datos - UOC  
Proyecto de Visualización de Datos

---
*Última actualización: Diciembre 2024* 