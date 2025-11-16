# 🖥️ Simulador de Interbloqueos 🖥️

![build](https://img.shields.io/badge/build-passing-brightgreen)
![python](https://img.shields.io/badge/Python-3.10+-blue)
![gui](https://img.shields.io/badge/GUI-Tkinter%20%2B%20ttkbootstrap-7952B3)
![graph](https://img.shields.io/badge/Grafos-NetworkX-orange)
![plots](https://img.shields.io/badge/Visualización-Matplotlib-blueviolet)
![status](https://img.shields.io/badge/Estado-Estable-success)
![os](https://img.shields.io/badge/Compatible-Windows%20%7C%20Linux%20%7C%20macOS-informational)

---

## 📚 Tabla de Contenidos  
- 🔄 [Interbloqueos (Deadlocks)](#-interbloqueos-deadlocks)
  - 🧩 [¿Cómo ocurre un interbloqueo?](#-cómo-ocurre-un-interbloqueo)
  - ⚠️ [Consecuencias](#️-consecuencias-de-un-interbloqueo)
  - 🔍 [Ejemplo típico](#-ejemplo-típico-de-deadlock)
  - 🧠 [Métodos generales de manejo](#-métodos-para-manejar-interbloqueos-visión-general)
- 📘 [Descripción](#-descripción)
  - 🎯 [Objetivo del Simulador](#-objetivo-del-simulador)
  - 🔍 [¿Qué hace este simulador?](#-qué-hace-este-simulador)
  - 🎮 [Experiencia de uso](#-experiencia-de-uso)
  - 👨‍🏫 [¿Para quién está pensado?](#‍-para-quién-está-pensado)
- 🛠️ [Tecnologías Utilizadas](#️-tecnologías-utilizadas)
- ✨ [Características Principales](#-características-principales)
- 🧠 [Algoritmos Implementados](#-algoritmos-implementados)
- 🖥️ [Requisitos del Sistema](#️-requisitos-del-sistema)
- 📥 [Instalación](#-instalación)
- ▶️ [Uso del Sistema](#️-uso-del-sistema)
- 📂 [Estructura del Proyecto](#-estructura-del-proyecto)


---

## 🔄 Interbloqueos (Deadlocks)

Un **interbloqueo** es una situación en la que dos o más procesos no pueden continuar su ejecución porque cada uno espera recursos que están siendo retenidos por otros procesos del mismo conjunto.  
Esto provoca una **espera indefinida**, dejando al sistema parcial o totalmente detenido.

Los interbloqueos son uno de los problemas más críticos en sistemas operativos, bases de datos, sistemas distribuidos y cualquier entorno con concurrencia y recursos compartidos.

---

### 🧩 ¿Cómo ocurre un interbloqueo?

Para que un interbloqueo pueda existir, deben cumplirse *simultáneamente* las siguientes **cuatro condiciones necesarias**:

#### 1️⃣ Mutua exclusión  
Al menos un recurso debe estar en un estado *no compartible*, es decir, solo puede ser usado por un proceso a la vez.  
Ejemplo: una impresora o un semáforo binario.

#### 2️⃣ Retención y espera  
Un proceso debe estar reteniendo recursos mientras espera adquirir otros adicionales.

#### 3️⃣ No expropiación  
Los recursos no pueden ser arrebatados por el sistema; solo pueden liberarse voluntariamente cuando el proceso termina o los libera.

#### 4️⃣ Espera circular  
Debe existir una cadena de procesos donde cada uno espera un recurso que está ocupado por el siguiente, formando un ciclo cerrado.

> Si estas cuatro condiciones se cumplen al mismo tiempo, **el deadlock es inevitable**.

---

### ⚠️ Consecuencias de un interbloqueo

- Procesos quedan bloqueados permanentemente.  
- Pérdida de rendimiento del sistema.  
- Recursos retenidos indefinidamente.  
- Posible compromiso de estabilidad del sistema operativo.  
- En sistemas críticos, puede causar fallas mayores o paros completos.

---

### 🔍 Ejemplo típico de deadlock

Imagina dos procesos:

- **P1** tiene el recurso **R1** y pide **R2**  
- **P2** tiene el recurso **R2** y pide **R1**

Ninguno puede avanzar, ya que ambos esperan un recurso que está siendo retenido por el otro.  
Esto genera una **espera circular**, uno de los pilares del interbloqueo.

---

### 🧠 Métodos para manejar interbloqueos (visión general)

(En secciones posteriores se explican a detalle, pero aquí va el resumen lógico)

- **Prevención:** impedir que se cumpla una de las 4 condiciones.  
- **Evitación:** asignar recursos solo si se mantiene un estado seguro.  
- **Detección y recuperación:** permitir el deadlock, detectarlo y resolverlo.  
- **Ignorar:** aceptarlo como improbable y no manejarlo (estrategia real usada en Unix).

---

Los interbloqueos representan uno de los temas más importantes dentro del estudio de sistemas operativos, y comprender cómo se producen es fundamental para interpretar correctamente el funcionamiento del simulador.

---

## 📘 Descripción

El **Simulador de Interbloqueos** es una herramienta interactiva desarrollada en Python que permite estudiar, visualizar y comprender de manera práctica cómo ocurren los *deadlocks* en sistemas operativos y cómo diferentes políticas pueden prevenirlos, evitarlos o detectarlos.

Diseñado con fines educativos, este simulador facilita el aprendizaje de los conceptos esenciales de **concurrencia**, **asignación de recursos** y **gestión de procesos**, permitiendo observar en tiempo real el comportamiento del sistema ante escenarios que normalmente solo se ven en teoría.

---

### 🎯 Objetivo del Simulador

El propósito principal es ofrecer una plataforma visual y dinámica que permita:

- Comprender las **condiciones que provocan un interbloqueo**.  
- Analizar cómo funcionan las **políticas clásicas de manejo de deadlocks**.  
- Observar de forma gráfica la interacción entre **procesos y recursos**.  
- Experimentar con **solicitudes, asignaciones, bloqueos y estados seguros**.  
- Facilitar prácticas de laboratorio y presentaciones académicas.

---

### 🔍 ¿Qué hace este simulador?

El sistema genera escenarios donde múltiples procesos compiten por recursos limitados.  
A partir de esta situación, el simulador permite:

- Mostrar cómo se generan asignaciones y solicitudes.  
- Detectar ciclos que pueden llevar a un interbloqueo.  
- Identificar estados seguros e inseguros.  
- Ejecutar diferentes enfoques para manejar el deadlock:
  - Prevención  
  - Evitación (Algoritmo del Banquero)  
  - Detección y recuperación  
  - Ignorar el problema  

Cada simulación se representa mediante:

- Tablas dinámicas de asignación, necesidad y disponibilidad.  
- Grafos interactivos que muestran la relación procesos ↔ recursos.  
- Señales visuales que indican bloqueos o estados válidos.  
- Una bitácora que explica cada acción del sistema paso a paso.  

---

### 🎮 Experiencia de uso

El simulador fue diseñado pensando en la claridad y facilidad de uso:

- Interfaz moderna con **Tkinter + ttkbootstrap**.  
- Visualización gráfica con **NetworkX + Matplotlib**.  
- Animaciones del algoritmo del banquero y estados seguros.  
- Escenarios totalmente configurables o generados al azar.  
- Explicaciones visuales ideales para estudiantes de Sistemas Operativos.

---

### 👨‍🏫 ¿Para quién está pensado?

- Estudiantes que cursan **Sistemas Operativos**, **Concurrencia** o **Computación avanzada**.  
- Docentes que necesitan una herramienta visual para explicar deadlocks.  
- Personas que deseen entender cómo un sistema operativo administra recursos.  
- Equipos de proyectos académicos que requieren simulaciones claras y demostrativas.

---

El simulador convierte un tema complejo en una experiencia visual, sencilla y completamente interactiva, permitiendo comprender de forma profunda cómo se producen y manejan los interbloqueos en un sistema real.

---

## 🛠️ Tecnologías Utilizadas

Este proyecto combina herramientas modernas de Python con librerías especializadas en visualización, interfaces gráficas y manejo de grafos. Cada componente fue elegido para garantizar una experiencia clara, interactiva y completamente funcional en cualquier plataforma.

---

### 🐍 Lenguaje de programación

- **Python 3.10+**  
  Utilizado por su simplicidad, potencia y enfoque educativo. Permite crear simulaciones complejas con un código legible y modular.

---

### 🎨 Interfaz gráfica (GUI)

- **Tkinter**  
  Biblioteca estándar de Python para interfaces gráficas. Utilizada para construir ventanas, botones, paneles y elementos interactivos.

- **ttkbootstrap**  
  Un framework visual basado en *bootstrap themes* para Tkinter.  
  Proporciona:
  - Estilos modernos  
  - Temas oscuros y claros  
  - Widgets más refinados  
  - Mejor experiencia visual  

---

### 📊 Visualización y graficación

- **NetworkX**  
  Librería especializada en:
  - Construcción de grafos  
  - Detección de ciclos  
  - Relaciones proceso ↔ recurso  
  - Modelado del grafo de asignación  

  Fundamental para representar visualmente estados de deadlock.

- **Matplotlib**  
  Usada para:
  - Renderizar el grafo generado por NetworkX  
  - Dibujar nodos, aristas y ciclos  
  - Mostrar diagramas dentro de la propia interfaz Tkinter  

---

### 🧩 Bibliotecas estándar de Python

Estas se utilizan para funciones complementarias:

- `random` → generación de escenarios y matrices aleatorias.  
- `time` → control de animaciones, temporizadores y pausas breves.  
- `os` → manejo de rutas y recursos internos.  
- `subprocess` → ejecución de scripts auxiliares (si es requerido).  
- `datetime` → registro de eventos en bitácora.  
- `tkinter.messagebox` → alertas, errores y confirmaciones.  
- `tkinter.ttk` → widgets estilizados para tablas y formularios.

---

### 🧱 Arquitectura general del proyecto

El simulador utiliza una estructura modular que separa:

- **UI:** componentes gráficos.  
- **Lógica de simulación:** algoritmos del sistema operativo.  
- **Visualización:** grafo, matrices y animaciones.  
- **Datos:** configuraciones y escenarios.

Esto permite un mantenimiento sencillo, pruebas claras y la posibilidad de incorporar nuevas políticas de manejo de interbloqueos en el futuro.

---

Estas tecnologías, combinadas, permiten que el simulador sea totalmente interactivo, visual y multiplataforma, ideal para prácticas académicas y demostraciones en clase.

---

## ✨ Características Principales

El **Simulador de Interbloqueos** está diseñado para ofrecer una experiencia completa, visual y educativa sobre el manejo de deadlocks en sistemas operativos. A continuación, se detallan sus principales características:

---

### 🔄 Simulación Completa de Recursos y Procesos
- Representación visual de **procesos**, **recursos** y **solicitudes**.  
- Actualización dinámica de asignaciones, liberaciones y estados internos.  
- Permite observar cómo se forma una espera circular o un estado inseguro.

---

### 🧠 Implementación de Políticas Reales del Sistema Operativo
Incluye los cuatro enfoques clásicos para manejar interbloqueos:

- **Prevención** → evita que se cumplan las condiciones que causan el deadlock.  
- **Evitación** → implementa el **Algoritmo del Banquero** para mantener al sistema en un estado seguro.  
- **Detección** → identifica ciclos en el grafo de asignación.  
- **Ignorar** → estrategia utilizada por sistemas donde el deadlock es improbable.

---

### 🧩 Simulador del Algoritmo del Banquero
- Evaluación completa de solicitudes.  
- Cálculo automático de matrices: **Asignación**, **Demanda Máxima**, **Necesidad**, **Disponibles**.  
- Secuencia segura mostrada con animación.  
- Indicadores visuales para estados seguros e inseguros.  
- Ejemplos automáticos para prácticas y demostraciones.

---

### 📊 Visualización Gráfica con NetworkX
- Generación de grafos que representan:  
  - Solicitudes de recursos  
  - Asignaciones activas  
  - Ciclos de espera  
- Detección visual de deadlocks mediante colores y trazos.  
- Renderizado integrado con Matplotlib dentro de la aplicación.

---

### 🎨 Interfaz Moderna y Amigable
- Construida con **Tkinter + ttkbootstrap**.  
- Temas visuales modernos (oscuro, claro, flat, etc.).  
- Distribución limpia con paneles laterales, tablas, botones e indicadores.  
- Perfecta para presentaciones académicas y clases prácticas.

---

### 📝 Bitácora en Tiempo Real
- Registro detallado de:
  - Solicitudes de procesos  
  - Aprobaciones y rechazos  
  - Cambios en matrices  
  - Estados seguros e inseguros  
- Ideal para análisis paso a paso y explicación de resultados.

---

### 🎛️ Escenarios Personalizables
- Selección de número de procesos y recursos.  
- Escenarios generados automáticamente o creados manualmente.  
- Matrices aleatorias garantizando un estado inicial seguro (para el banquero).

---

### 🧱 Arquitectura Modular
El proyecto está estructurado en módulos independientes:

- `simuladores/` → lógica de cada política  
- `ui/` → interfaz gráfica  
- `data/` → configuraciones y datos auxiliares  
- `main.py` → ejecutor principal

Esto facilita mantenimiento, mejoras y extensión del proyecto.

---

### 💻 Multiplataforma
Funciona correctamente en:
- Windows  
- Linux  
- macOS  

Sin requerir configuraciones adicionales más allá de las dependencias del proyecto.

---

Estas características convierten al simulador en una herramienta robusta y visualmente poderosa para comprender a fondo el manejo de interbloqueos en sistemas operativos.

---

## 🧠 Algoritmos Implementados

El simulador incorpora los cuatro enfoques clásicos utilizados por los sistemas operativos para manejar los interbloqueos. Cada algoritmo está implementado de forma visual y práctica, permitiendo observar su comportamiento en tiempo real.

---

### 🔹 1. Prevención de Interbloqueos

La prevención se basa en **evitar que una de las cuatro condiciones necesarias** para el deadlock pueda ocurrir.  
El simulador permite experimentar cómo la ausencia de estas condiciones modifica el comportamiento del sistema.

Ejemplos de prevención:
- No permitir **retención y espera**.  
- Forzar **expropiación** de recursos.  
- Romper la **espera circular** mediante ordenamiento de recursos.

Este enfoque evita el interbloqueo por diseño, pero puede reducir la utilización de recursos.

---

### 🔹 2. Evitación — Algoritmo del Banquero

Implementado completamente en el proyecto, este algoritmo analiza cada solicitud y determina si es seguro otorgarla.

El algoritmo:
- Evalúa la matriz de **Asignación**, **Demanda Máxima**, **Necesidad** y **Recursos Disponibles**.  
- Solo concede la solicitud si el sistema **permanece en un estado seguro**.  
- Calcula una **secuencia segura** donde todos los procesos pueden finalizar.

El simulador muestra:
- La animación de la secuencia segura.  
- Matrices actualizadas en tiempo real.  
- Indicadores de aceptación o rechazo de solicitudes.

---

### 🔹 3. Detección de Interbloqueos

Este enfoque permite que el deadlock ocurra y luego lo detecta mediante:

- Análisis del **grafo de asignación** con NetworkX.  
- Búsqueda de **ciclos dirigidos** que representan una espera circular.  
- Indicadores visuales que resaltan los nodos implicados.  
- Registro en la bitácora del momento exacto en que el sistema entra en deadlock.

Este método es útil cuando los bloqueos son poco frecuentes.

---

### 🔹 4. Ignorar el Problema

También conocido como **Ostrich Algorithm**, este enfoque simplemente **no maneja** los interbloqueos.

Se utiliza en:
- Sistemas donde el deadlock es extremadamente improbable.  
- Sistemas donde el costo de manejarlo supera el riesgo de que ocurra.

El simulador permite visualizar el comportamiento del sistema cuando se ignora por completo la gestión de deadlocks, ideal para comparar este enfoque con los demás.

---

Estos cuatro algoritmos permiten comprender todas las estrategias reales que utiliza un sistema operativo moderno para evitar que la concurrencia de procesos provoque bloqueos permanentes.


---

## 🖥️ Requisitos del Sistema

El **Simulador de Interbloqueos** está diseñado para funcionar en la mayoría de sistemas modernos con requisitos mínimos. A continuación se detallan los requisitos necesarios tanto a nivel de software como de hardware.

---

### 🔹 Requisitos de Software

- **Python 3.10 o superior**  
  Es indispensable contar con una versión reciente para garantizar compatibilidad con las librerías utilizadas.

- **Librerías externas (incluidas en `requirements.txt`):**
  - `ttkbootstrap` → interfaz gráfica moderna basada en Tkinter.  
  - `networkx` → manejo y análisis de grafos para detección de ciclos.  
  - `matplotlib` → visualización del grafo dentro del simulador.  

- **Librerías estándar de Python (ya incluidas por defecto):**
  - `tkinter` y `tkinter.ttk`
  - `random`
  - `time`
  - `os`
  - `subprocess`
  - `datetime`

No se requiere instalar nada adicional si ya se cuenta con Python correctamente configurado.

---

### 🔹 Requisitos de Hardware

El simulador es ligero y no requiere equipo especializado.

- **CPU:** 2 núcleos (mínimo recomendado)  
- **RAM:** 4 GB o más  
- **Almacenamiento:** Al menos 200 MB libres  
- **Tarjeta gráfica:** Cualquiera compatible con Matplotlib (todas las integradas modernas funcionan)

---

### 🔹 Compatibilidad del Sistema Operativo

El proyecto funciona de manera estable en:

- 🪟 **Windows 10 / Windows 11**  
- 🐧 **Linux (Ubuntu, Debian, Fedora, Manjaro, etc.)**  
- 🍏 **macOS (requiere Tcl/Tk actualizado para Tkinter)**

No se necesita configuración adicional más allá de instalar Python y las dependencias del proyecto.

---

### 🔹 Opcional: Recomendaciones

Para una mejor experiencia:

- Utilizar temas de ttkbootstrap compatibles con tu sistema.  
- Ejecutar el proyecto desde VS Code, PyCharm o un terminal con soporte UTF-8 para emojis.  
- Activar un entorno virtual para manejar dependencias de forma ordenada.  

---

El simulador está optimizado para ser accesible, funcional y multiplataforma, permitiendo que cualquier usuario pueda ejecutarlo sin configuraciones avanzadas.


---

## 📥 Instalación

### 1️⃣ Clonar el repositorio
```bash
git clone https://github.com/FredyGus/Simulador-Interbloqueos.git
```

### 2️⃣ Entrar al directorio
```bash
cd Simulador-Interbloqueos
```

### 3️⃣ Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4️⃣ Ejecutar el sistema
```bash
python main.py
```
---

## ▶️ Uso del Sistema

Una vez instalado el proyecto, puedes iniciar el simulador para comenzar a trabajar con los diferentes algoritmos de manejo de interbloqueos. La interfaz es intuitiva y está diseñada para guiar al usuario durante todo el proceso.

---

### 🔹 1. Iniciar el simulador

Ejecutá:

```bash
python main.py
```

### 🔹 2. Menú principal

- Prevención
- Evitación (Algoritmo del Banquero)
- Detección de Interbloqueos
- Ignorar el Problema
Selecciona uno para comenzar la simulación.

### 🔹 3. Configuración del escenario

Dependiendo de la simulación elegida, podrás:
- Seleccionar cantidad de procesos
- Seleccionar cantidad de recursos
- Definir valores manualmente o generar escenarios aleatorios
- Visualizar matrices iniciales (asignación, necesidad, demanda máxima)
El simulador se adapta al enfoque que hayas elegido.

### 🔹 4. Simulación de solicitudes y asignaciones

Dentro de cada modo podrás:
- Seleccionar un proceso
- Ingresar una solicitud de recursos
- Enviar la solicitud para que el simulador:
  - La evalúe
  - La acepte
  - O la rechace
El sistema responde en tiempo real mostrando:
- Cambios en las matrices
- Mensajes explicativos
- Estados seguros o inseguros

### 🔹 5. Visualización del grafo

Al utilizar modos como Detección o Ignorar, el sistema genera un grafo con:
- Nodos que representan procesos y recursos
- Flechas de solicitud
- Flechas de asignación
- Indicadores visuales de ciclos o bloqueos
Esta representación es ideal para comprender cómo se forma un deadlock.

### 🔹 6. Uso del Algoritmo del Banquero

En este modo podrás:
- Ver las matrices:
  - Asignación ( Allocation )
  - Demanda Máxima ( Max )
  - Necesidad ( Need )
  - Disponibles ( Available )
- Enviar solicitudes del proceso seleccionado
- Analizar si el sistema se mantiene en estado seguro
- Observar la secuencia segura animada cuando existe
- Ver rechazos cuando la solicitud crea un estado inseguro

### 🔹 7. Bitácora en tiempo real

Cada acción importante queda registrada:
- Solicitudes de recursos
- Asignaciones realizadas
- Liberaciones
- Detección de ciclos
- Cambios de estado
Esto permite analizar el comportamiento del sistema paso a paso, ideal para presentaciones o tareas académicas.

### 🔹 8. Reiniciar simulación

En cualquier momento podés reiniciar el escenario para:
- Generar nuevas matrices
- Cambiar el número de procesos o recursos
- Probar diferentes conjuntos de solicitudes
- Comparar el comportamiento entre algoritmos

### 🟢 En resumen

El simulador te permite:
- Ver cómo ocurren los interbloqueos
- Comprobar cómo cada enfoque los maneja de forma distinta
- Entender las decisiones del sistema mediante tablas, grafos y bitácoras
- Experimentar libremente con diferentes configuraciones y escenarios

---

## 📂 Estructura del proyecto
```plaintext
Simulador-Interbloqueos/
├── data
│   ├── logs_deteccion
│   └── logs_prevencion
├── simuladores
│   ├── simulador_banquero.py
│   ├── simulador_deteccion.py
│   └── simulador_prevencion.py
├── ui
│   ├── __init__.py
│   └── ui_main.py
├── main.py
├── README.md
└── requirements.txt
```

