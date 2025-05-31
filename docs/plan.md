<!-- filepath: /Users/rcruz2/Library/CloudStorage/OneDrive-MAPFRE/Trabajo/Cloud/Cursor/rag_viajes/docs/plan.md -->
# Plan de desarrollo del Chatbot RAG para Viajes de la Comunidad de Madrid

## Resumen de los puntos clave del proyecto

* **Fuentes de Información:** 7 PDFs de catálogos de viajes de la Comunidad de Madrid para mayores de 55 años.
* **Complejidad de PDFs:** Información en columnas, diferencias sutiles entre catálogos, fechas variables, información de contratación/seguros al inicio.
* **Objetivo Principal del Chatbot:** Responder preguntas sobre viajes, incluyendo fechas y origen del catálogo.
* **Objetivo Secundario:** Responder sobre condiciones de contratación/cancelación.
* **Personalidad del Chatbot:** Agente de viajes, amigable pero no familiar, conciso pero detallado.
* **Coste:** Minimizar el coste, con un presupuesto de $10/mes para OpenAI.
* **Rendimiento:** No es un requisito crítico en este momento, pero la calidad del resultado sí lo es.
* **Validación:** Esencial, con Langfuse. Necesitamos definir métricas de éxito.
* **Interfaz de Usuario:** Básica, similar a un chat, con historial de conversaciones.
* **Selección de Librerías:** Primar el resultado, la capacidad de manejar PDFs complejos y el *chunking* inteligente (por página y manteniendo contexto).
* **Optimización de Búsqueda:** Considerar el almacenamiento de palabras clave junto con chunks/embeddings.

## Plan de Proyecto Detallado (Fase a Fase)

Procederemos de forma iterativa, construyendo y probando en incrementos pequeños.

### Fase 1: Configuración del Entorno y Preprocesamiento de Documentos

Esta fase es crucial para asegurar que la información de los PDFs se extrae de forma usable y que la base de datos está lista para albergarla.

#### 1.1. Configuración del Entorno y Repositorio

* **Objetivo:** Establecer la estructura del proyecto y asegurar que todas las herramientas básicas están instaladas y configuradas.
* **Hitos:**
  * Creación de un repositorio de GitHub.
  * Creación de un entorno virtual de Python.
  * Instalación de dependencias básicas (fastapi, uvicorn, pydantic, openai, supabase-py, langchain, langfuse).
  * Configuración de variables de entorno para API Keys (OpenAI, Supabase, Langfuse).

* **Acciones:**
  * Crea el repositorio en GitHub.
  * En tu IDE (VS Code o similar), abre la carpeta del proyecto.
  * Crea un entorno virtual y actívalo.
  * Crea un archivo `requirements.txt` y `config.py` (o `.env`).

* **Prompt para el Asistente de Código (para `config.py` y `requirements.txt`):**

    ```text
    "Necesito configurar un proyecto Python para un chatbot RAG. Genera un archivo `requirements.txt` que incluya las siguientes librerías: `fastapi`, `uvicorn`, `pydantic`, `openai`, `supabase-py`, `langchain`, `langfuse`. Luego, crea un archivo `config.py` (o un ejemplo de `.env`) para almacenar las API Keys de OpenAI, Supabase y Langfuse. Asegúrate de que las API Keys se carguen de forma segura."
    ```

#### 1.2. Exploración y Selección de Librerías para Conversión PDF a Markdown

* **Objetivo:** Evaluar `PyMuPDF4LLM` y `docetl` para determinar cuál maneja mejor la complejidad de tus PDFs y mantiene la estructura para el *chunking*. Es vital que identifique y marque cada página.
* **Criterios de Evaluación:**
  * Precisión en la extracción de texto y tablas.
  * Capacidad para mantener la estructura de columnas.
  * Identificación clara de los saltos de página en el Markdown.
  * Manejo de imágenes (si es relevante conservar referencias).
  * Facilidad de uso y configuración.
* **Acciones:**
  * Escribe scripts de prueba pequeños para cada librería.
  * Procesa al menos uno de los PDFs de ejemplo con ambas.
  * Inspecciona manualmente los archivos Markdown generados.

* **Prompt para el Asistente de Código (para probar PyMuPDF4LLM):**

    ```text
    "Necesito un script Python que use `pymupdf4llm` para convertir un archivo PDF específico (por ejemplo, 'cam_25_halcon_viajes_39_mb_1.pdf') a formato Markdown. Asegúrate de que el script guarde el resultado en un archivo `.md` y que la salida Markdown preserve la estructura de tablas y marque los saltos de página si la librería lo permite."
    ```

* **Prompt para el Asistente de Código (para probar docetl):**

    ```text
    "Necesito un script Python que use `docetl` (si ya está instalado o indícame cómo instalarlo) para convertir un archivo PDF específico (por ejemplo, 'cam_25_halcon_viajes_39_mb_1.pdf') a formato Markdown. El script debe guardar el resultado en un archivo `.md` y, si es posible, debería intentar mantener la estructura de tablas y la distinción de páginas."
    ```

* **Decisión:** Una vez que hayas evaluado ambos, elige la que mejor se adapte a tus necesidades. Mi recomendación inicial, dada la complejidad de los PDFs y la necesidad de estructura, se inclina un poco más hacia **PyMuPDF4LLM** por su enfoque en LLMs y su capacidad para generar Markdown estructurado, pero la prueba es clave.

#### 1.3. Conversión de Todos los PDFs a Markdown

* **Objetivo:** Convertir los 7 PDFs a archivos Markdown limpios y estructurados.
* **Hito:** Tener 7 archivos `.md` en una carpeta específica del proyecto.
* **Acciones:**
  * Crea una función o script que itere sobre todos los PDFs en una carpeta y aplique la librería elegida para la conversión.
  * Asegúrate de nombrar los archivos Markdown de forma que se pueda identificar su origen (ej. `halcon_viajes_2025.md`, `nautalia_2025.md`). Esto será crucial para el RAG.

* **Prompt para el Asistente de Código (basado en la librería elegida, asumamos PyMuPDF4LLM):**

    ```text
    "Desarrolla un script Python que tome una lista de rutas de archivos PDF de los catálogos de viajes. Para cada PDF, debe utilizar `pymupdf4llm` para convertirlo a Markdown. Los archivos Markdown resultantes deben guardarse en una carpeta 'markdown_docs' y sus nombres deben derivar del nombre original del PDF (ej. 'catalogo_x.pdf' -> 'catalogo_x.md'). Asegúrate de manejar posibles errores durante la conversión."
    ```

### Fase 2: Desarrollo del RAG - Chunking y Embeddings

En esta fase, prepararemos los datos para el sistema RAG, dividiéndolos en trozos manejables y creando sus representaciones vectoriales.

#### 2.1. Exploración y Selección de Librerías para Chunking

* **Objetivo:** Evaluar `Chonkie` y `LangChain MarkdownHeaderTextSplitter` para determinar cuál realiza un *chunking* más inteligente, preservando el contexto y la información de la página. La capacidad de partir por página es fundamental.
* **Criterios de Evaluación:**
  * Capacidad para dividir por encabezados y mantener el contexto.
  * Preservación de la información de la página.
  * Manejo de tablas y listas.
  * Flexibilidad para definir reglas de *chunking*.
  * Facilidad de uso.
* **Acciones:**
  * Escribe scripts de prueba para cada librería.
  * Usa uno de los archivos Markdown generados en la Fase 1.
  * Inspecciona los chunks resultantes y su metadata.

* **Prompt para el Asistente de Código (para probar LangChain MarkdownHeaderTextSplitter):**

    ```text
    "Necesito un script Python que use `LangChain MarkdownHeaderTextSplitter` para dividir un archivo Markdown (por ejemplo, 'markdown_docs/halcon_viajes_2025.md'). El script debe definir una estrategia de split que intente preservar la estructura de encabezados y, si es posible, la información de página. Imprime los chunks generados y su metadata asociada para revisión."
    ```

* **Prompt para el Asistente de Código (para probar Chonkie):**

    ```text
    "Necesito un script Python para probar la librería `Chonkie` para el *chunking* de un archivo Markdown (por ejemplo, 'markdown_docs/halcon_viajes_2025.md'). Proporciona un ejemplo de cómo configurar `Chonkie` para un *chunking* inteligente que preserve la estructura y el contexto, e imprime los chunks generados para inspección."
    ```

* **Decisión:** **LangChain MarkdownHeaderTextSplitter** a menudo es muy efectivo para Markdown, especialmente si los PDFs se convierten bien a Markdown estructurado con encabezados. La mención de `Chonkie` en el *roadmap* sugiere que podría tener capacidades avanzadas, pero para Markdown estructurado, LangChain es un contendiente fuerte. La clave será ver cómo manejan las tablas y las listas.

#### 2.2. Generación de Chunks y Metadata Enriquecida

* **Objetivo:** Crear chunks significativos a partir de los archivos Markdown, asegurando que cada chunk tenga metadatos como el *origen del catálogo* (nombre del archivo PDF original) y el *número de página* (si el preprocesamiento lo permitió).
* **Hitos:** Una lista de objetos `Document` (o similar) con `page_content` y `metadata` enriquecida, lista para ser convertida a embeddings.
* **Acciones:**
  * Crea un script que lea todos los archivos Markdown.
  * Aplica la librería de *chunking* seleccionada.
  * Para cada chunk, añade metadatos como `source_catalogue` (ej. 'Halcon Viajes 2025') y `page_number`.
  * **Importante:** Considera la posibilidad de extraer palabras clave relevantes de cada chunk en esta etapa y añadirlas a la metadata o en un campo separado para futura optimización de búsqueda.

* **Prompt para el Asistente de Código (basado en la librería de chunking elegida, asumamos LangChain Splitter):**

    ```text
    "Desarrolla un script Python que procese todos los archivos Markdown de la carpeta 'markdown_docs'. Para cada archivo, utiliza el `MarkdownHeaderTextSplitter` de LangChain para crear chunks. Asegúrate de que cada chunk tenga una metadata que incluya `source_catalogue` (derivado del nombre del archivo Markdown) y `page_number` (si el splitter puede extraerlo o si lo agregamos manualmente al Markdown en la fase 1). Además, implementa una lógica para extraer algunas palabras clave principales de cada chunk (puedes usar un modelo de OpenAI o simple TF-IDF para esto) y añadirlas a la metadata del chunk bajo la clave `keywords`. Imprime los primeros 5 chunks con su metadata para verificar."
    ```

#### 2.3. Generación de Embeddings con OpenAI

* **Objetivo:** Convertir cada chunk en un vector de embedding utilizando el modelo `text-embedding-3-small` de OpenAI, priorizando el coste.
* **Hito:** Una lista de tuplas `(chunk_texto, embedding, metadata)`.
* **Acciones:**
  * Crea una función para generar embeddings a partir de una lista de textos.
  * Aplica esta función a todos los `page_content` de tus chunks.
  * Considera la agrupación de llamadas a la API de OpenAI para eficiencia (enviando varios textos en una sola solicitud si la API lo permite).

* **Prompt para el Asistente de Código:**

    ```text
    "Necesito un script Python que tome una lista de objetos de chunk (donde cada objeto tiene un atributo `page_content` con el texto y `metadata`). Utilizando la API de OpenAI (con el modelo `text-embedding-3-small`), genera el embedding para el `page_content` de cada chunk. Incluye la API Key de OpenAI desde `config.py`. Muestra cómo procesar una pequeña muestra de chunks y sus embeddings resultantes."
    ```

##### 2.3.1 Caching de Embeddings (por hash del chunk)

Después de generar los chunks (Fase 2.2), para cada chunk:

a. Calcula un hash de su page_content.
b. Consulta Supabase (en una tabla de caché o directamente en chunks_catalogos si puedes agregar la columna chunk_hash) para ver si ya existe un embedding para ese hash.
c. Si existe, recupera el embedding y el id asociado.
d. Si no existe, genera el embedding con OpenAI y luego lo inserta en Supabase junto con el hash

> Consideración: ¿Dónde almacenar el hash? Podría ser una columna adicional en `chunks_catalogos` (`chunk_hash` TEXT) o una tabla separada `embedding_cache` (`hash` TEXT PRIMARY KEY, `embedding` VECTOR). Dado que el embedding está intrínsecamente ligado al chunk, añadir una columna `chunk_hash` a `chunks_catalogos` tiene más sentido y simplifica la lógica.

* **Prompt para el Asistente de Código (para la lógica de caching en la generación de embeddings):**

```text
"Modifica el script de generación de embeddings (Fase 2.3). Antes de llamar a la API de OpenAI para generar un embedding para un chunk, calcula un hash SHA256 del `page_content` del chunk. Consulta la tabla `chunks_catalogos` de Supabase para ver si ya existe un registro con ese `chunk_hash` y un `embedding` no nulo. Si existe, recupera el `embedding` existente. Si no, genera el embedding con `text-embedding-3-small` de OpenAI y luego insértalo o actualízalo en la tabla `chunks_catalogos` junto con el `chunk_hash`. Asegúrate de que la tabla `chunks_catalogos` tenga una columna `chunk_hash` de tipo TEXT."
```

#### 2.4. Almacenamiento de Embeddings y Chunks en Supabase

* **Objetivo:** Almacenar los embeddings, el texto original del chunk y toda la metadata enriquecida en una tabla de Supabase (PostgreSQL con pgvector).
* **Hitos:**
  * Creación de la tabla `chunks_catalogos` en Supabase.
  * Carga exitosa de todos los datos.
* **Acciones:**
  * Define el esquema de la tabla `chunks_catalogos` en Supabase (id, content, embedding vector, source_catalogue, page_number, keywords, etc.).
  * Escribe el script para conectar a Supabase e insertar los datos.

* **Prompt para el Asistente de Código (para Supabase y pgvector):**

    ```text
    "Genera un script Python que se conecte a Supabase utilizando la API Key y URL de `config.py`. Define una función para crear una tabla llamada `chunks_catalogos` con las siguientes columnas: `id` (serial primary key), `content` (text), `embedding` (vector con la dimensión adecuada para text-embedding-3-small, que es 1536), `source_catalogue` (text), `page_number` (integer), `keywords` (text array o text). Luego, implementa una función para insertar una lista de chunks (cada uno con su texto, embedding y metadata) en esta tabla. Asegúrate de manejar la inserción de forma eficiente (por ejemplo, en lotes)."
    ```

#### Fase 3: Desarrollo del RAG - Recuperación y Generación

Ahora construiremos la lógica central del sistema RAG.

#### 3.1. Función de Búsqueda Vectorial en Supabase

* **Objetivo:** Implementar la lógica para buscar los *k* chunks más relevantes en Supabase basándose en la similitud coseno del embedding de la consulta del usuario.
* **Hito:** Una función que recibe una consulta y devuelve los chunks más relevantes (texto y metadata).
* **Acciones:**
  * Crea una función que tome el texto de la consulta del usuario.
  * Genere el embedding de la consulta con OpenAI.
  * Realice la búsqueda vectorial en la tabla `chunks_catalogos` de Supabase usando `pgvector`.
  * Devuelva los `k` chunks más cercanos.
  * **Optimización:** Considera cómo podríamos usar las `keywords` si las incluimos en la metadata para un filtro híbrido (vectorial + palabras clave).

* **Prompt para el Asistente de Código:**

    ```text
    "Necesito una función Python llamada `search_relevant_chunks(query: str, top_k: int = 5)` que:
    1.  Tome una `query` (pregunta del usuario) como entrada.
    2.  Genere el embedding de la `query` utilizando el modelo `text-embedding-3-small` de OpenAI (usando la API Key de `config.py`).
    3.  Realice una búsqueda de similitud de coseno en la tabla `chunks_catalogos` de Supabase, recuperando los `top_k` chunks más similares al embedding de la consulta.
    4.  Devuelva los `content`, `source_catalogue` y `page_number` de los chunks recuperados.
    ```

#### 3.2. Integración del RAG y Generación de Respuesta con OpenAI

* **Objetivo:** Combinar la búsqueda de chunks con un LLM de OpenAI para generar respuestas coherentes y relevantes.
* **Hito:** Una función `generate_rag_response(query: str)` que toma una pregunta y devuelve una respuesta.
* **Acciones:**
  * Crea la función `generate_rag_response`.
  * Dentro de ella, llama a `search_relevant_chunks`.
  * Construye un prompt efectivo para el LLM (por ejemplo, `gpt-4o-mini` o `gpt-4` si el presupuesto lo permite, pero priorizando `gpt-4o-mini` para el coste). El prompt debe instruir al LLM a usar la información proporcionada (chunks) para responder a la pregunta del usuario.

* **Prompt para el Asistente de Código (para la función de generación de respuesta):**

    ```text
    "Crea una función Python `generate_rag_response(query: str)` que implemente la lógica RAG:
    1.  Llama a la función `search_relevant_chunks(query, top_k=5)` para obtener los chunks más relevantes.
    2.  Construye un prompt para el modelo de chat de OpenAI (`gpt-4o-mini`). El prompt debe:
        * Instruir al modelo para que actúe como un 'agente de viajes amigable pero conciso y detallado'.
        * Indicarle que solo utilice la información proporcionada en los 'Contextos' para responder.
        * Añadir los `content` de los chunks recuperados, indicando su `source_catalogue` y `page_number` como "Contexto [nombre_catalogo, página_numero]: [contenido_chunk]".
        * Incluir la pregunta del usuario.
        * Instruir al modelo a mencionar de qué catálogo proviene la información cuando sea relevante, especialmente para fechas o disponibilidad.
    3.  Realiza la llamada a la API de OpenAI y devuelve la respuesta generada."
    ```

#### Fase 4: Desarrollo del Chatbot (API REST) y Persistencia

Aquí construiremos la interfaz del chatbot y su capacidad de recordar conversaciones.

#### 4.1. Esqueleto de la API con FastAPI y Uvicorn

* **Objetivo:** Configurar una API REST básica para el chatbot.
* **Hito:** Un servidor FastAPI funcional con un endpoint `/chat` y un endpoint `/health`.
* **Acciones:**
  * Crea el archivo `main.py` para la aplicación FastAPI.
  * Define un modelo Pydantic para las solicitudes de chat.
  * Implementa un endpoint `/chat` que reciba la pregunta del usuario y devuelva una respuesta dummy (por ahora).
  * Configura Uvicorn para ejecutar la aplicación.

* **Prompt para el Asistente de Código:**

    ```text
    "Genera un esqueleto de aplicación FastAPI en `main.py`. Incluye:
    1.  Un modelo Pydantic `ChatMessage` con campos `user_id: str` y `message: str`.
    2.  Un endpoint POST `/chat` que acepte un `ChatMessage` como entrada. Por ahora, este endpoint debería devolver una respuesta fija como '¡Hola! Recibí tu mensaje: [mensaje del usuario]'.
    3.  Un endpoint GET `/health` que devuelva `{'status': 'ok'}`.
    4.  Instrucciones para ejecutar la aplicación con Uvicorn."
    ```

#### 4.2. Integración del RAG en la API

* **Objetivo:** Conectar la lógica del RAG con el endpoint de la API.
* **Hito:** El endpoint `/chat` devuelve respuestas generadas por el sistema RAG.
* **Acciones:**
  * Importa la función `generate_rag_response` en `main.py`.
  * Modifica el endpoint `/chat` para que llame a esta función.

* **Prompt para el Asistente de Código (refinando el endpoint `/chat`):**

    ```text
    "Modifica el endpoint POST `/chat` en `main.py` para que, en lugar de una respuesta fija, utilice la función `generate_rag_response` (que asume que ya está importada). La función debe tomar `chat_message.message` como la consulta. La respuesta del endpoint debe ser el texto generado por el RAG."
    ```

#### 4.3. Persistencia del Chat con Supabase

* **Objetivo:** Almacenar el historial de chat de los usuarios en Supabase.
* **Hitos:**
  * Creación de la tabla `chat_history` en Supabase.
  * Cada interacción del usuario se guarda.
  * Implementación de la funcionalidad para recuperar chats pasados.
* **Acciones:**
  * Define el esquema de la tabla `chat_history` (id, user_id, timestamp, user_message, bot_response, etc.).
  * Crea funciones para guardar y recuperar el historial de un usuario.
  * Integra estas funciones en el endpoint `/chat` y un nuevo endpoint `/chat_history/{user_id}`.

* **Prompt para el Asistente de Código (para la persistencia en Supabase):**

    ```text
    "Necesito implementar la persistencia del chat en Supabase.
    1.  Primero, genera una función `create_chat_history_table(supabase_client)` para crear la tabla `chat_history` con las siguientes columnas: `id` (serial primary key), `user_id` (text), `timestamp` (timestamp with time zone, default now()), `user_message` (text), `bot_response` (text).
    2.  Luego, crea una función `save_chat_interaction(user_id: str, user_message: str, bot_response: str)` que inserte una nueva fila en la tabla `chat_history`.
    3.  Finalmente, crea una función `get_user_chat_history(user_id: str)` que recupere todas las interacciones para un `user_id` dado, ordenadas por `timestamp`.
    4.  Integra `save_chat_interaction` en el endpoint `/chat` de FastAPI después de generar la respuesta.
    5.  Crea un nuevo endpoint GET `/chat_history/{user_id}` que utilice `get_user_chat_history` para devolver el historial de chat de un usuario."
    ```

#### Fase 5: Validación del Sistema con Langfuse y Testing

Esta fase es crucial para garantizar la calidad y el rendimiento del chatbot.

#### 5.1. Integración de Langfuse

* **Objetivo:** Trazar todas las interacciones del RAG y del chatbot en Langfuse para monitorización y depuración.
* **Hito:** Se ven trazas en el dashboard de Langfuse para cada consulta.
* **Acciones:**
  * Inicializa Langfuse en tu aplicación FastAPI.
  * Envuelve las llamadas a OpenAI (embeddings y LLM) y la búsqueda en Supabase con trazas de Langfuse.
  * Captura la pregunta del usuario, los chunks recuperados y la respuesta final del LLM.

* **Prompt para el Asistente de Código:**

    ```text
    "Integra Langfuse en la aplicación FastAPI y las funciones RAG.
    1.  Modifica `main.py` para inicializar el cliente Langfuse (asegúrate de que las API Keys de Langfuse estén en `config.py`).
    2.  Añade trazabilidad a la función `generate_rag_response` para capturar la `query` del usuario, los `chunks` recuperados (incluyendo su `source_catalogue` y `page_number`), la llamada al LLM (input, output) y la respuesta final.
    3.  Asegúrate de que cada 'step' (ej. 'embedding_generation', 'vector__search', 'llm_call') se registre con sus respectivos inputs y outputs en Langfuse."
    ```

#### 5.2. Definición de Métricas de Éxito y Plan de Validación

* **Objetivo:** Establecer cómo se medirá el éxito del chatbot y cómo se realizarán las pruebas.
* **Acciones:**
  * **Métricas de Éxito:**
    * **Relevancia:** ¿La respuesta aborda la pregunta del usuario?
    * **Precisión:** ¿La información en la respuesta es correcta y se basa en los catálogos? (No debe alucinar).
    * **Exhaustividad:** ¿La respuesta cubre todos los aspectos relevantes de la pregunta (especialmente para fechas y catálogos)?
    * **Origen Identificado:** ¿El chatbot es capaz de identificar de qué catálogo y página proviene la información relevante, cuando se le pide o es fundamental para la pregunta?
    * **Tono:** ¿El tono es amigable pero conciso y profesional?
  * **Plan de Validación:**
    * **Pruebas Unitarias:** Para funciones de preprocesamiento, chunking, generación de embeddings y búsqueda en Supabase.
    * **Pruebas de Integración:** Para el flujo completo del RAG (consulta -> embeddings -> búsqueda -> LLM -> respuesta).
    * **Pruebas Manuales / Evaluación Humana:** Esto es crucial para un chatbot.
      * Crea un conjunto de preguntas representativas (simples, complejas, con fechas, comparativas, sobre condiciones).
      * Un evaluador humano (tú mismo o un colega) interactúa con el chatbot y califica cada respuesta según las métricas de éxito definidas (ej. escala de 1 a 5).
      * Utiliza las trazas de Langfuse para entender por qué una respuesta fue buena o mala (ej. chunks incorrectos, LLM no interpretó bien el contexto).
      * **Identificación de "Buen" o "Mal" resultado:** Un "buen" resultado es una respuesta **relevante, precisa, que utiliza la información del catálogo identificando el origen si es necesario, y con el tono adecuado**. Un "mal" resultado es una respuesta irrelevante, incorrecta, que alucina, no usa el contexto, o no identifica el catálogo cuando es crucial.

#### 5.3. Implementación de Pruebas (Esqueleto)

* **Objetivo:** Empezar a escribir pruebas para los componentes críticos.
* **Hito:** Archivos de prueba básicos en su lugar.

* **Prompt para el Asistente de Código (para esqueleto de pruebas):**

    ```text
    "Genera un esqueleto de archivo de pruebas `test_rag.py` usando `pytest`. Incluye ejemplos de cómo escribir pruebas unitarias para:
    1.  La función de conversión de PDF a Markdown (verificando que se genera un archivo).
    2.  La función de *chunking* (verificando el número de chunks y la presencia de metadatos esperados).
    3.  La función de búsqueda vectorial en Supabase (simulando un embedding de consulta y verificando que devuelve un formato esperado, o incluso mocks si no se quiere golpear la DB en cada test).
    También, sugiere cómo podríamos empezar a testear la función `generate_rag_response` (quizás mockeando la llamada a OpenAI y los chunks recuperados)."
    ```

#### Fase 6: Contenerización y Despliegue (Google GCP)

Finalmente, prepararemos la aplicación para su despliegue.

#### 6.1. Creación del Dockerfile

* **Objetivo:** Contenerizar la aplicación FastAPI.
* **Hito:** Un `Dockerfile` funcional que construye una imagen.
* **Acciones:**
  * Crea un `Dockerfile` que use una imagen base de Python.
  * Copia los archivos del proyecto.
  * Instala las dependencias.
  * Expone el puerto.
  * Define el comando para ejecutar la aplicación con Uvicorn.

* **Prompt para el Asistente de Código:**

    ```text
    "Genera un `Dockerfile` para una aplicación FastAPI en Python 3.9 (o la versión que estés usando). El Dockerfile debe:
    1.  Usar una imagen base oficial de Python.
    2.  Copiar el `requirements.txt` e instalar las dependencias.
    3.  Copiar el resto de la aplicación.
    4.  Exponer el puerto 8000.
    5.  Definir el comando para ejecutar la aplicación `main.py` con Uvicorn, escuchando en todas las interfaces (`0.0.0.0`)."
    ```

#### 6.2. Despliegue en Google Cloud Platform (GCP)

* **Objetivo:** Desplegar el chatbot en GCP. Podríamos considerar **Cloud Run** por su simplicidad y modelo de coste por uso, que encaja con tu presupuesto.
* **Hito:** El chatbot accesible a través de una URL pública en GCP.
* **Acciones:**
  * **Google Cloud Run:**
    * Asegúrate de que la cuenta de GCP esté configurada y tengas permisos.
    * Construye la imagen Docker localmente y súbela a Google Container Registry (GCR) o Artifact Registry.
    * Crea un nuevo servicio en Cloud Run, especificando la imagen y las variables de entorno (API Keys de OpenAI, Supabase, Langfuse).

* **Prompt para el Asistente de Código (instrucciones para GCP Cloud Run):**

    ```text
    "Proporciona los comandos de `gcloud` necesarios para:
    1.  Construir una imagen Docker de la aplicación actual.
    2.  Etiquetar la imagen para Google Container Registry (GCR) o Artifact Registry.
    3.  Subir la imagen al registro.
    4.  Desplegar la imagen en Google Cloud Run, especificando un nombre de servicio, la región, permitiendo el acceso no autenticado, y configurando variables de entorno para `OPENAI_API_KEY`, `SUPABASE_URL`, `SUPABASE_KEY`, `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY` (asumiendo que los valores se obtienen de tu entorno local)."
    ```

### Consideraciones Adicionales durante el Desarrollo:

* **Manejo de Errores:** Siempre piensa en cómo manejar errores (API no disponible, formato incorrecto, etc.).
* **Logs:** Asegúrate de que tu aplicación genere logs útiles.
* **Seguridad:** No expongas tus API Keys directamente en el código. Usa variables de entorno.
* **Iteración:** Después de cada fase de prueba, revisa y refina. El proceso RAG a menudo requiere ajustes finos en el *chunking*, el *prompting* y la estrategia de búsqueda.

Este plan te proporciona una hoja de ruta detallada. Recuerda, la clave es la iteración. ¡Estoy aquí para ayudarte en cada paso! ¿Estás listo para comenzar con la Fase 1: Configuración del Entorno y Preprocesamiento de Documentos?
