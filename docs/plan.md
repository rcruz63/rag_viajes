# Plan de desarrollo del Chatbot RAG para Viajes de la Comunidad de Madrid

## Resumen de los puntos clave del proyecto

* Fuentes de Información: 7 PDFs de catálogos de viajes de la Comunidad de Madrid para mayores de 55 años.
* Complejidad de PDFs: Información en columnas, diferencias sutiles entre catálogos, fechas variables, información de contratación/seguros al inicio.
* Objetivo Principal del Chatbot: Responder preguntas sobre viajes, incluyendo fechas y origen del catálogo.
* Objetivo Secundario: Responder sobre condiciones de contratación/cancelación.
* Personalidad del Chatbot: Agente de viajes, amigable pero no familiar, conciso pero detallado.
* Coste: Minimizar el coste, con un presupuesto de $10/mes para OpenAI.
* Rendimiento: No es un requisito crítico en este momento, pero la calidad del resultado sí lo es.
* Validación: Esencial, con Langfuse. Necesitamos definir métricas de éxito.
* Interfaz de Usuario: Básica, similar a un chat, con historial de conversaciones.
* Selección de Librerías: Primar el resultado, la capacidad de manejar PDFs complejos y el *chunking* inteligente (por página y manteniendo contexto).
* Optimización de Búsqueda: Considerar el almacenamiento de palabras clave junto con chunks/embeddings.
* Testing: Implementar pruebas unitarias y de integración desde el inicio, con `pytest` y `httpx.AsyncClient`.
* Iteración: Construir y probar en incrementos pequeños, asegurando que cada fase se valida antes de pasar a la siguiente.
* Documentación: Mantener documentación clara y actualizada en el repositorio de GitHub.
* Repositorio: Crear un repositorio en GitHub para el proyecto, con una estructura clara y archivos de configuración.
* Configuración del Entorno: Usar un entorno virtual de Python, con un archivo `requirements.txt` para las dependencias.
* API Keys: Configurar las API Keys de OpenAI, Supabase y Langfuse de forma segura, usando un archivo `.env` o `config.py`.
* CLI: Implementar un CLI básico con `click` para facilitar la interacción durante el desarrollo y pruebas.
* Pruebas de Conversión PDF a Markdown: Evaluar y seleccionar la mejor librería para convertir PDFs a Markdown, asegurando que se mantenga la estructura y se identifiquen las páginas.
* Chunking y Embeddings: Evaluar y seleccionar la mejor librería para el *chunking* de Markdown, asegurando que se mantenga el contexto y se identifiquen las páginas. Generar embeddings con OpenAI, utilizando una caché para evitar cálculos repetidos.
* Almacenamiento en Supabase: Crear una tabla para almacenar los chunks y sus embeddings, asegurando que se maneje correctamente la caché.
* Búsqueda Vectorial: Implementar una función de búsqueda vectorial en Supabase para recuperar los chunks más relevantes basados en la similitud coseno del embedding de la consulta del usuario.
* Generación de Respuestas: Combinar la búsqueda de chunks con un LLM de OpenAI para generar respuestas coherentes y relevantes.
* API REST del Chatbot: Configurar una API REST básica con FastAPI y Uvicorn, integrando la lógica del RAG y permitiendo la persistencia del historial de chat.
* Persistencia del Chat: Almacenar el historial de chat en Supabase, permitiendo la recuperación de conversaciones pasadas.
* Validación y Monitoreo: Implementar Langfuse para validar las respuestas del chatbot y monitorear su rendimiento, asegurando que se cumplan las métricas de éxito definidas.

## Plan de Proyecto Detallado (Fase a Fase)

Procederemos de forma iterativa, construyendo y probando en incrementos pequeños.

### Fase 1: Configuración del Entorno y Preprocesamiento de Documentos

Esta fase es crucial para asegurar que la información de los PDFs se extrae de forma usable y que la base de datos está lista para albergarla.

#### 1.1. Configuración del Entorno y Repositorio

* **Objetivo:** Establecer la estructura del proyecto y asegurar que todas las herramientas básicas están instaladas y configuradas.
* **Hitos:**
  * Creación de un repositorio de GitHub. Es este repositorio: [RAG Viajes](https://github.com/rcruz63/rag_viajes)
  * Creación de un entorno virtual de Python. Estamos usando `uv` para gestiornar el entorno virtual.
  * Instalación de dependencias básicas (fastapi, uvicorn, pydantic, openai, supabase, langchain, langfuse, click, pytest, python-dotenv).
  * Configuración de variables de entorno para API Keys (OpenAI, Supabase, Langfuse).
* **Acciones:**
  * Crea el repositorio en GitHub.
  * En tu IDE (VS Code o similar), abre la carpeta del proyecto.
  * Crea un entorno virtual y actívalo.
  * Crea un archivo `requirements.txt`, `config.py` (o `.env`) y `cli.py`.

* **Prompt para el Asistente de Código (para `requirements.txt`, `config.py` y `cli.py`):**

    ```text
    "Necesito configurar un proyecto Python para un chatbot RAG. Genera un archivo `requirements.txt` que incluya las siguientes librerías: `fastapi`, `uvicorn`, `pydantic`, `openai`, `supabase`, `langchain`, `langfuse`, `click`, `pytest`, `python-dotenv`. Luego, crea un archivo `config.py` para cargar de forma segura las API Keys de OpenAI, Supabase y Langfuse desde un archivo `.env`. Finalmente, crea un esqueleto inicial para un `cli.py` usando `click` con un comando simple como `hello`."
    ```

* **Prompt para el Asistente de Código (para `test_config.py`):**

    ```text
    "Genera un archivo `test_config.py` usando `pytest` para verificar que las variables de entorno para las API Keys de OpenAI, Supabase y Langfuse se cargan correctamente desde `config.py`. Las pruebas deben asegurar que estas variables existen y no están vacías."
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

* **Prompt para el Asistente de Código (para probar PyMuPDF4LLM en `cli.py`):**

    ```text
    "Añade un comando `convert-pdf-pymu` al `cli.py` que tome una ruta de archivo PDF como argumento. Este comando debe usar `pymupdf4llm` para convertir el PDF a Markdown. El Markdown resultante debe guardarse en un archivo `.md` en una carpeta temporal y se debe imprimir un mensaje de éxito. Asegúrate de que el script pueda manejar la ruta del PDF. y que la salida Markdown preserve la estructura de tablas y marque los saltos de página si la librería lo permite."
    ```

* **Prompt para el Asistente de Código (para probar docetl en `cli.py`):**

    ```text
    "Añade un comando `convert-pdf-docetl` al `cli.py` que tome una ruta de archivo PDF como argumento. Este comando debe usar `docetl` (asume que ya está instalado o indícame cómo instalarlo) para convertir el PDF a Markdown. El Markdown resultante debe guardarse en un archivo `.md` en una carpeta temporal, si es posible, debería intentar mantener la estructura de tablas y la distinción de páginas. Se debe imprimir un mensaje de éxito."
    ```

* **Prompt para el Asistente de Código (para `test_pdf_conversion.py`):**

    ```text
    "Crea un archivo `test_pdf_conversion.py` usando `pytest`. Incluye dos pruebas unitarias:
    1.  Una que pruebe la función de conversión de PDF a Markdown con `pymupdf4llm` (simulando la conversión de un PDF pequeño y verificando que el archivo Markdown se crea y no está vacío).
    2.  Una que pruebe la función de conversión con `docetl` de manera similar.
    Asegúrate de limpiar los archivos temporales generados después de cada prueba. Para las pruebas, puedes usar un PDF de prueba muy pequeño o simular la existencia del archivo."
    ```

* **Decisión:** Una vez que hayas evaluado ambos, elige la que mejor se adapte a tus necesidades. Mi recomendación inicial, dada la complejidad de los PDFs y la necesidad de estructura, se inclina un poco más hacia **PyMuPDF4LLM** por su enfoque en LLMs y su capacidad para generar Markdown estructurado, pero la prueba es clave.

#### 1.3. Conversión de Todos los PDFs a Markdown

* **Objetivo:** Convertir los 7 PDFs a archivos Markdown limpios y estructurados.
* **Hito:** Tener 7 archivos `.md` en una carpeta específica del proyecto (ej. `data/markdown_docs`).
* **Acciones:**
  * Crea una función o script que itere sobre todos los PDFs en una carpeta y aplique la librería elegida para la conversión.
  * Asegúrate de nombrar los archivos Markdown de forma que se pueda identificar su origen (ej. `halcon_viajes_2025.md`, `nautalia_2025.md`). Esto será crucial para el RAG.

* **Prompt para el Asistente de Código (para el comando CLI y la función de conversión global):**

    ```text
    "Añade un comando `convert-all-pdfs` al `cli.py`. Este comando debe:
    1.  Tomar una ruta de entrada de PDFs y una ruta de salida para los Markdown.
    2.  Utilizar la librería de conversión de PDF a Markdown previamente seleccionada (asumimos `pymupdf4llm`).
    3.  Iterar sobre todos los archivos PDF en la carpeta de entrada.
    4.  Convertir cada PDF a Markdown, guardándolo en la carpeta de salida con el mismo nombre de archivo pero extensión `.md`.
    5.  Manejar posibles errores durante la conversión e informar al usuario.
    6.  Incluir una función Python reutilizable que realice esta conversión para que el CLI la llame."
    ```

* **Prompt para el Asistente de Código (para `test_full_conversion.py`):**

    ```text
    "Genera un archivo `test_full_conversion.py` usando `pytest`. Crea una prueba que simule la conversión de múltiples PDFs de ejemplo (puedes crear archivos PDF pequeños o stubs en tu directorio de pruebas). La prueba debe:
    1.  Verificar que se generan archivos Markdown para cada PDF de entrada.
    2.  Asegurarse de que los archivos Markdown no estén vacíos.
    3.  Confirmar que los nombres de los archivos Markdown son correctos.
    Asegúrate de limpiar los archivos temporales o directorios creados después de la ejecución de la prueba."
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

* **Prompt para el Asistente de Código (para probar LangChain MarkdownHeaderTextSplitter en `cli.py` y una función):**

    ```text
    "Añade un comando `test-chunking-langchain` al `cli.py` que tome una ruta a un archivo Markdown como argumento. Este comando debe usar `LangChain MarkdownHeaderTextSplitter` para dividir el archivo. El script debe definir una estrategia de split que intente preservar la estructura de encabezados y, si es posible, la información de página. Imprime los primeros 5 chunks generados y su metadata asociada para revisión. Crea una función Python separada para esta lógica de chunking que el CLI pueda llamar."
    ```

* **Prompt para el Asistente de Código (para probar Chonkie en `cli.py` y una función):**

    ```text
    "Añade un comando `test-chunking-chonkie` al `cli.py` que tome una ruta a un archivo Markdown como argumento. Este comando debe usar `Chonkie` para el *chunking* del archivo. Proporciona un ejemplo de cómo configurar `Chonkie` para un *chunking* inteligente que preserve la estructura y el contexto, e imprime los primeros 5 chunks generados para inspección. Crea una función Python separada para esta lógica de chunking que el CLI pueda llamar."
    ```

* **Prompt para el Asistente de Código (para `test_chunking_libraries.py`):**

    ```text
    "Genera un archivo `test_chunking_libraries.py` usando `pytest`. Incluye pruebas unitarias para las funciones de *chunking* de LangChain y Chonkie. Para cada una:
    1.  Crea un string Markdown de prueba con encabezados y contenido tabular/columnar.
    2.  Verifica que el número de chunks generados es el esperado.
    3.  Asegúrate de que los chunks contengan metadatos relevantes (si la librería los genera).
    4.  Comprueba que el contenido de los chunks es plausible y que no hay información crítica truncada."
    ```

* **Decisión:** **LangChain MarkdownHeaderTextSplitter** a menudo es muy efectivo para Markdown, especialmente si los PDFs se convierten bien a Markdown estructurado con encabezados. La mención de `Chonkie` en el *roadmap* sugiere que podría tener capacidades avanzadas, pero para Markdown estructurado, LangChain es un contendiente fuerte. La clave será ver cómo manejan las tablas y las listas.

#### 2.2. Generación de Chunks y Metadata Enriquecida

* **Objetivo:** Crear chunks significativos a partir de los archivos Markdown, asegurando que cada chunk tenga metadatos como el *origen del catálogo* (nombre del archivo PDF original) y el *número de página* (si el preprocesamiento lo permitió), y un hash de su contenido.
* **Hitos:** Una lista de objetos `Document` (o similar) con `page_content` y `metadata` enriquecida, lista para ser convertida a embeddings.
* **Acciones:**
  * Crea un script que lea todos los archivos Markdown.
  * Aplica la librería de *chunking* seleccionada.
  * Para cada chunk, añade metadatos como `source_catalogue` (ej. 'Halcon Viajes 2025') y `page_number`.
  * Calcula un hash SHA256 del `page_content` de cada chunk y añádelo a la metadata como `chunk_hash`.
  * **Importante:** Considera la posibilidad de extraer palabras clave relevantes de cada chunk en esta etapa y añadirlas a la metadata o en un campo separado para futura optimización de búsqueda.

* **Prompt para el Asistente de Código (para el comando CLI y la función de procesamiento de chunks):**

    ```text
    "Añade un comando `process-chunks` al `cli.py` que tome una ruta a la carpeta de archivos Markdown. Este comando debe:
    1.  Leer todos los archivos Markdown de la carpeta.
    2.  Utilizar la función de chunking seleccionada (asume que ya está implementada y es importable).
    3.  Para cada chunk generado, calcular un hash SHA256 de su `page_content` y añadirlo a la metadata como `chunk_hash`.
    4.  Añadir `source_catalogue` (derivado del nombre del archivo Markdown) y `page_number` (si es posible) a la metadata del chunk.
    5.  Implementar una función auxiliar para extraer palabras clave principales de cada chunk (puedes usar un enfoque simple como extracción de las N palabras más frecuentes después de limpieza de stopwords, o un mock) y añadirlas a la metadata como `keywords` (lista de strings).
    6.  Imprimir los primeros 5 chunks procesados con su metadata completa para verificación.
    7.  La lógica principal debe estar encapsulada en una función reutilizable que el CLI pueda llamar."
    ```

* **Prompt para el Asistente de Código (para `test_chunk_processing.py`):**

    ```text
    "Genera un archivo `test_chunk_processing.py` usando `pytest`. Incluye pruebas unitarias para la función que procesa los chunks:
    1.  Verifica que los metadatos `source_catalogue`, `page_number` y `chunk_hash` se añaden correctamente a cada chunk.
    2.  Asegúrate de que las `keywords` se extraen y se añaden a la metadata de forma esperada.
    3.  Prueba con un chunk de ejemplo para asegurarte de que el hash SHA256 se calcula correctamente."
    ```

#### 2.3. Generación de Embeddings con OpenAI (con Caching)

* **Objetivo:** Convertir cada chunk en un vector de embedding utilizando el modelo `text-embedding-3-small` de OpenAI, aprovechando una caché para evitar cálculos repetidos.
* **Hito:** Una lista de tuplas `(chunk_texto, embedding, metadata)` donde los embeddings se han obtenido de la caché o de la API de OpenAI.
* **Acciones:**
  * Crea una función `get_or_generate_embedding(chunk_content: str, chunk_hash: str)` que:
    * Consulta Supabase para ver si el `chunk_hash` ya existe y tiene un `embedding` asociado en la tabla `chunks_catalogos`.
  * Si existe, recupera el `embedding` y lo devuelve.
  * Si no, genera el embedding con `text-embedding-3-small` de OpenAI y lo devuelve. Este embedding se utilizará en la siguiente etapa para la inserción/actualización en Supabase.
  * Esta función será llamada antes de la inserción/actualización final en Supabase.

* **Prompt para el Asistente de Código (para la función de obtención/generación de embedding y CLI):**

    ```text
    "Crea una función Python `get_or_generate_embedding(chunk_content: str, chunk_hash: str, supabase_client)` que:
    1.  Reciba el contenido del chunk, su hash y una instancia del cliente de Supabase.
    2.  Consulte la tabla `chunks_catalogos` en Supabase para buscar el `chunk_hash`.
    3.  Si encuentra el hash con un embedding, lo devuelve.
    4.  Si no, llama a la API de OpenAI con el modelo `text-embedding-3-small` para generar el embedding.
    5.  Devuelve el embedding generado.
    Integra esta función en un nuevo comando `generate-embeddings` en `cli.py` que procese un conjunto de chunks (quizás un archivo Markdown de prueba o los que ya generaste) y demuestre cómo se usa la caché. Este comando no necesita insertar en Supabase, solo demostrar la generación y el uso de la caché."
    ```

* **Prompt para el Asistente de Código (para `test_embedding_generation.py`):**

    ```text
    "Genera un archivo `test_embedding_generation.py` usando `pytest`. Incluye pruebas unitarias para la función `get_or_generate_embedding`:
    1.  Mockea las llamadas a Supabase para simular un escenario donde el embedding ya existe en caché y verifica que la API de OpenAI no se llama.
    2.  Mockea las llamadas a Supabase y OpenAI para simular un escenario donde el embedding no está en caché y verifica que la API de OpenAI se llama y devuelve un embedding.
    3.  Asegúrate de que el modelo `text-embedding-3-small` se especifica en las llamadas a OpenAI."
    ```

#### 2.4. Almacenamiento de Embeddings y Chunks en Supabase

* **Objetivo:** Almacenar los embeddings, el texto original del chunk y toda la metadata enriquecida (incluyendo el hash) en una tabla de Supabase (PostgreSQL con pgvector).
* **Hitos:**
  * Creación de la tabla `chunks_catalogos` en Supabase con la columna `chunk_hash`.
  * Carga exitosa de todos los datos, utilizando la lógica de caché.
* **Acciones:**
  * Define el esquema de la tabla `chunks_catalogos` en Supabase (id, content, embedding vector, source_catalogue, page_number, chunk_hash, keywords, etc.). Asegúrate de que `chunk_hash` sea único y se pueda usar como clave para el caching.
  * Escribe el script para conectar a Supabase e insertar los datos, utilizando la función `get_or_generate_embedding` antes de cada inserción/actualización.

* **Prompt para el Asistente de Código (para la configuración de la tabla Supabase y el comando CLI de carga):**

    ```text
    "Genera un script Python que se conecte a Supabase utilizando la API Key y URL de `config.py`. Define:
    1.  Una función `create_chunks_table(supabase_client)` para crear la tabla `chunks_catalogos` con las siguientes columnas: `id` (serial primary key), `content` (text), `embedding` (vector con la dimensión de `text-embedding-3-small`, que es 1536), `source_catalogue` (text), `page_number` (integer), `chunk_hash` (text UNIQUE, INDEXED), `keywords` (text[]).
    2.  Una función `upsert_chunks_to_supabase(chunks: list, supabase_client)` que inserte o actualice una lista de chunks procesados (cada uno con su texto, hash y metadata) en esta tabla. Dentro de esta función, para cada chunk, usa `get_or_generate_embedding` para obtener el embedding antes de la operación de upsert. Asegúrate de manejar la operación de forma eficiente (por ejemplo, en lotes).
    3.  Añade un comando `upload-chunks-to-db` al `cli.py` que orqueste el procesamiento de los archivos Markdown y la subida de los chunks a Supabase."
    ```

* **Prompt para el Asistente de Código (para `test_supabase_upload.py`):**

    ```text
    "Genera un archivo `test_supabase_upload.py` usando `pytest`. Mockea las interacciones con Supabase para probar la función `upsert_chunks_to_supabase`:
    1.  Verifica que la función intenta realizar una operación `upsert` (inserción o actualización) con el número correcto de chunks.
    2.  Asegúrate de que los datos formateados para la operación en Supabase son correctos (ej. el `embedding` es un array, `chunk_hash` está presente y es único).
    3.  Simula escenarios de éxito y fracaso de la operación."
    ```

### Fase 3: Desarrollo del RAG - Recuperación y Generación

Ahora construiremos la lógica central del sistema RAG.

#### 3.1. Función de Búsqueda Vectorial en Supabase

* **Objetivo:** Implementar la lógica para buscar los *k* chunks más relevantes en Supabase basándose en la similitud coseno del embedding de la consulta del usuario.
* **Hito:** Una función que recibe una consulta y devuelve los chunks más relevantes (texto y metadata).
* **Acciones:**
  * Crea una función que tome el texto de la consulta del usuario.
  * Genere el embedding de la consulta con `text-embedding-3-small` de OpenAI.
  * Realice la búsqueda vectorial en la tabla `chunks_catalogos` de Supabase usando `pgvector`.
  * Devuelva los `k` chunks más cercanos.
  * **Optimización:** Considera cómo podríamos usar las `keywords` si las incluimos en la metadata para un filtro híbrido (vectorial + palabras clave).

* **Prompt para el Asistente de Código (para la función de búsqueda y CLI):**

    ```text
    "Crea una función Python llamada `search_relevant_chunks(query: str, top_k: int = 5, supabase_client)` que:
    1.  Tome una `query` (pregunta del usuario) como entrada.
    2.  Genere el embedding de la `query` utilizando el modelo `text-embedding-3-small` de OpenAI (usando la API Key de `config.py`).
    3.  Realice una búsqueda de similitud de coseno en la tabla `chunks_catalogos` de Supabase, recuperando los `top_k` chunks más similares al embedding de la consulta.
    4.  Devuelva los `content`, `source_catalogue`, `page_number` y `keywords` de los chunks recuperados.
    5.  Añade un comando `search-chunks` al `cli.py` que tome una consulta como argumento y use esta función para mostrar los resultados."
    ```

* **Prompt para el Asistente de Código (para `test_search_chunks.py`):**

    ```text
    "Genera un archivo `test_search_chunks.py` usando `pytest`. Mockea las interacciones con Supabase y OpenAI para probar la función `search_relevant_chunks`:
    1.  Mockea la generación de embeddings de la consulta.
    2.  Mockea la respuesta de Supabase con un conjunto predefinido de chunks simulados.
    3.  Verifica que la función devuelve el número correcto de chunks y que los datos recuperados tienen el formato esperado (incluyendo `source_catalogue`, `page_number`, `keywords`).
    4.  Prueba el caso en que no se encuentran chunks."
    ```

#### 3.2. Integración del RAG y Generación de Respuesta con OpenAI

* **Objetivo:** Combinar la búsqueda de chunks con un LLM de OpenAI para generar respuestas coherentes y relevantes.
* **Hito:** Una función `generate_rag_response(query: str)` que toma una pregunta y devuelve una respuesta.
* **Acciones:**
  * Crea la función `generate_rag_response`.
  * Dentro de ella, llama a `search_relevant_chunks`.
  * Construye un prompt efectivo para el LLM (`gpt-4o-mini`). El prompt debe instruir al LLM a usar la información proporcionada (chunks) para responder a la pregunta del usuario.

* **Prompt para el Asistente de Código (para la función de generación de respuesta y CLI):**

    ```text
    "Crea una función Python `generate_rag_response(query: str, supabase_client)` que implemente la lógica RAG:
    1.  Llama a la función `search_relevant_chunks(query, top_k=5, supabase_client)` para obtener los chunks más relevantes.
    2.  Construye un prompt para el modelo de chat de OpenAI (`gpt-4o-mini`). El prompt debe:
        * Instruir al modelo para que actúe como un 'agente de viajes amigable pero conciso y detallado'.
        * Indicarle que solo utilice la información proporcionada en los 'Contextos' para responder.
        * Añadir los `content` de los chunks recuperados, indicando su `source_catalogue` y `page_number` como 'Contexto [nombre_catalogo, página_numero]: [contenido_chunk]'.
        * Incluir la pregunta del usuario.
        * Instruir al modelo a mencionar de qué catálogo proviene la información cuando sea relevante, especialmente para fechas o disponibilidad.
    3.  Realiza la llamada a la API de OpenAI y devuelve la respuesta generada.
    Añade un comando `chat` al `cli.py` que permita al usuario ingresar una pregunta y ver la respuesta generada por el RAG."
    ```

* **Prompt para el Asistente de Código (para `test_rag_response.py`):**

    ```text
    "Genera un archivo `test_rag_response.py` usando `pytest`. Mockea las dependencias (Supabase y OpenAI) para probar la función `generate_rag_response`:
    1.  Mockea `search_relevant_chunks` para que devuelva un conjunto predefinido de chunks relevantes con su metadata.
    2.  Mockea la llamada a la API de OpenAI para `gpt-4o-mini` y define una respuesta simulada.
    3.  Verifica que la función `generate_rag_response` construya el prompt correctamente (examinando el mock de la llamada a OpenAI).
    4.  Asegúrate de que la función devuelve la respuesta esperada."
    ```

### Fase 4: Desarrollo del Chatbot (API REST) y Persistencia

Aquí construiremos la interfaz del chatbot y su capacidad de recordar conversaciones.

#### 4.1. Esqueleto de la API con FastAPI y Uvicorn

* **Objetivo:** Configurar una API REST básica para el chatbot.
* **Hito:** Un servidor FastAPI funcional con un endpoint `/chat` y un endpoint `/health`.
* **Acciones:**
  * Crea el archivo `main.py` para la aplicación FastAPI.
  * Define un modelo Pydantic para las solicitudes de chat.
  * Implementa un endpoint `/chat` que reciba la pregunta del usuario y devuelva una respuesta dummy (por ahora).
  * Configura Uvicorn para ejecutar la aplicación.

* **Prompt para el Asistente de Código (para `main.py`):**

    ```text
    "Genera un esqueleto de aplicación FastAPI en `main.py`. Incluye:
    1.  Configuración inicial de FastAPI.
    2.  Un modelo Pydantic `ChatMessage` con campos `user_id: str` y `message: str`.
    3.  Un endpoint POST `/chat` que acepte un `ChatMessage` como entrada. Por ahora, este endpoint debería devolver una respuesta fija como '¡Hola! Recibí tu mensaje: [mensaje del usuario]'.
    4.  Un endpoint GET `/health` que devuelva `{'status': 'ok'}`.
    5.  Instrucciones para ejecutar la aplicación con Uvicorn (por ejemplo, `uvicorn main:app --reload`)."
    ```

* **Prompt para el Asistente de Código (para `test_api_skeleton.py`):**

    ```text
    "Genera un archivo `test_api_skeleton.py` usando `pytest` y `httpx.AsyncClient` para probar el esqueleto de la API FastAPI:
    1.  Prueba el endpoint GET `/health` para asegurar que devuelve `{'status': 'ok'}` y un código de estado 200.
    2.  Prueba el endpoint POST `/chat` con un `ChatMessage` de prueba y verifica que devuelve la respuesta dummy esperada y un código de estado 200."
    ```

#### 4.2. Integración del RAG en la API

* **Objetivo:** Conectar la lógica del RAG con el endpoint de la API.
* **Hito:** El endpoint `/chat` devuelve respuestas generadas por el sistema RAG.
* **Acciones:**
  * Importa la función `generate_rag_response` en `main.py`.
  * Modifica el endpoint `/chat` para que llame a esta función.

* **Prompt para el Asistente de Código (refinando el endpoint `/chat` en `main.py`):**

    ```text
    "Modifica el endpoint POST `/chat` en `main.py` para que, en lugar de una respuesta fija, utilice la función `generate_rag_response` (que asume que ya está importada y puede recibir una instancia de Supabase client). La función debe tomar `chat_message.message` como la consulta. La respuesta del endpoint debe ser el texto generado por el RAG. Asegúrate de pasar el cliente de Supabase a la función `generate_rag_response`."
    ```

* **Prompt para el Asistente de Código (para `test_rag_api_integration.py`):**

    ```text
    "Genera un archivo `test_rag_api_integration.py` usando `pytest` y `httpx.AsyncClient`. Mockea las funciones internas (`generate_rag_response` y las interacciones con Supabase/OpenAI si es necesario) para probar el endpoint `/chat` después de integrar el RAG:
    1.  Verifica que al enviar un mensaje, la API llama a `generate_rag_response` con el mensaje correcto.
    2.  Asegúrate de que la respuesta de la API es la misma que la respuesta mockeada de `generate_rag_response`."
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

* **Prompt para el Asistente de Código (para la persistencia en Supabase y endpoints en `main.py`):**

    ```text
    "Necesito implementar la persistencia del chat en Supabase dentro de `main.py`.
    1.  Crea una función `create_chat_history_table(supabase_client)` para crear la tabla `chat_history` con las siguientes columnas: `id` (serial primary key), `user_id` (text), `timestamp` (timestamp with time zone, default now()), `user_message` (text), `bot_response` (text).
    2.  Crea una función `save_chat_interaction(user_id: str, user_message: str, bot_response: str, supabase_client)` que inserte una nueva fila en la tabla `chat_history`.
    3.  Crea una función `get_user_chat_history(user_id: str, supabase_client)` que recupere todas las interacciones para un `user_id` dado, ordenadas por `timestamp`.
    4.  Integra `save_chat_interaction` en el endpoint `/chat` de FastAPI después de generar la respuesta RAG.
    5.  Crea un nuevo endpoint GET `/chat_history/{user_id}` que utilice `get_user_chat_history` para devolver el historial de chat de un usuario."
    ```

* **Prompt para el Asistente de Código (para `test_chat_persistence.py`):**

    ```text
    "Genera un archivo `test_chat_persistence.py` usando `pytest` y `httpx.AsyncClient`. Mockea las interacciones con Supabase para probar la persistencia del chat:
    1.  Prueba el endpoint POST `/chat` para verificar que `save_chat_interaction` se llama con los datos correctos.
    2.  Prueba el endpoint GET `/chat_history/{user_id}` para asegurar que `get_user_chat_history` se llama y que la API devuelve el historial esperado (simulando una respuesta de Supabase)."
    ```

### Fase 5: Validación del Sistema con Langfuse y Testing

Esta fase es crucial para garantizar la calidad y el rendimiento del chatbot. Aunque ya hemos introducido pruebas unitarias, aquí nos centraremos en la integración y evaluación de la calidad del RAG.

#### 5.1. Integración de Langfuse

* **Objetivo:** Trazar todas las interacciones del RAG y del chatbot en Langfuse para monitorización y depuración.
* **Hito:** Se ven trazas en el dashboard de Langfuse para cada consulta.
* **Acciones:**
  * Inicializa Langfuse en tu aplicación FastAPI.
  * Envuelve las llamadas a OpenAI (embeddings y LLM) y la búsqueda en Supabase con trazas de Langfuse.
  * Captura la pregunta del usuario, los chunks recuperados y la respuesta final del LLM.

* **Prompt para el Asistente de Código (para la integración de Langfuse en `main.py` y funciones RAG):**

    ```text
    "Integra Langfuse en la aplicación FastAPI (`main.py`) y en las funciones RAG (como `get_or_generate_embedding`, `search_relevant_chunks`, `generate_rag_response`).
    1.  Inicializa el cliente Langfuse en `main.py` (usando las API Keys de `config.py`).
    2.  Añade trazabilidad a la función `generate_rag_response` para capturar la `query` del usuario, los `chunks` recuperados (incluyendo su `source_catalogue` y `page_number`), la llamada al LLM (input, output) y la respuesta final.
    3.  Asegúrate de que cada 'step' (ej. 'embedding_generation', 'vector_search', 'llm_call') se registre con sus respectivos inputs y outputs en Langfuse. Para `get_or_generate_embedding` y `search_relevant_chunks`, los registros de Langfuse deben ser \"spans\" hijos de la traza principal de la consulta RAG."
    ```

* **Prompt para el Asistente de Código (para `test_langfuse_integration.py`):**

    ```text
    "Genera un archivo `test_langfuse_integration.py` usando `pytest`. Mockea el cliente de Langfuse para verificar que las funciones RAG y los endpoints de la API están enviando los datos de trazabilidad esperados a Langfuse:
    1.  Verifica que se crea una traza principal para cada llamada al endpoint `/chat`.
    2.  Asegúrate de que se crean spans para la generación de embeddings, la búsqueda vectorial y la llamada al LLM, y que estos spans contienen los datos correctos (inputs, outputs, nombres de modelos, etc.)."
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
      * Un evaluador humano (tú mismo o un colega) interactúa con el chatbot y califica cada respuesta según las métricas de éxito definidas (ej. escala de 1 a 5, o Sí/No).
      * Utiliza las trazas de Langfuse para entender por qué una respuesta fue buena o mala (ej. chunks incorrectos, LLM no interpretó bien el contexto).
      * **Identificación de "Buen" o "Mal" resultado:** Un "buen" resultado es una respuesta **relevante, precisa, que utiliza la información del catálogo identificando el origen si es necesario, y con el tono adecuado**. Un "mal" resultado es una respuesta irrelevante, incorrecta, que alucina, no usa el contexto, o no identifica el catálogo cuando es crucial.

#### 5.3. Implementación de Pruebas Adicionales (de Integración y End-to-End)

* **Objetivo:** Extender la cobertura de pruebas para flujos más complejos.
* **Hito:** Pruebas de integración para el RAG y la API.

* **Prompt para el Asistente de Código (para `test_e2e_rag.py`):**

    ```text
    "Genera un archivo `test_e2e_rag.py` usando `pytest` que simule un flujo completo de RAG de extremo a extremo (desde la consulta hasta la respuesta final). Utiliza mocks estratégicos para las APIs externas (Supabase y OpenAI) para controlar el comportamiento y asegurar la determinismo.
    1.  Simula un escenario donde se proporciona una consulta y los chunks relevantes simulados.
    2.  Mockea la respuesta del LLM para esa consulta y esos chunks.
    3.  Verifica que la respuesta final del RAG sea la esperada.
    4.  Crea un test para un caso donde no se encuentran chunks relevantes y verifica la respuesta del LLM."
    ```

### Fase 6: Contenerización y Despliegue (Google GCP)

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

    ```dockerfile
    FROM python:3.10-slim-buster

    WORKDIR /app

    COPY requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt

    COPY . .

    EXPOSE 8000

    CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
    ```

#### 6.2. Despliegue en Google Cloud Platform (GCP)

* **Objetivo:** Desplegar el chatbot en GCP. Consideraremos **Cloud Run** por su simplicidad y modelo de coste por uso, que encaja con tu presupuesto.
* **Hito:** El chatbot accesible a través de una URL pública en GCP.
* **Acciones:**
  * **Google Cloud Run:**
    * Asegúrate de que la cuenta de GCP esté configurada y tengas permisos.
    * Construye la imagen Docker localmente y súbela a Google Container Registry (GCR) o Artifact Registry.
    * Crea un nuevo servicio en Cloud Run, especificando la imagen y las variables de entorno (API Keys de OpenAI, Supabase, Langfuse).

* **Prompt para el Asistente de Código (instrucciones para GCP Cloud Run):**

    ```text
    # 1. Configurar tu proyecto de GCP (si no lo has hecho ya)
    # Reemplaza 'your-gcp-project-id' con el ID de tu proyecto real
    gcloud config set project your-gcp-project-id

    # 2. Habilitar las APIs necesarias (solo la primera vez)
    gcloud services enable artifactregistry.googleapis.com cloudrun.googleapis.com

    # 3. Configurar el repositorio de Artifact Registry
    # Reemplaza 'your-region' (ej. europe-west1) y 'your-repo-name' (ej. chatbot-repo)
    gcloud artifacts repositories create your-repo-name --repository-format=docker --location=your-region --description="Docker repository for chatbot"

    # 4. Configurar Docker para autenticarse en Artifact Registry
    gcloud auth configure-docker your-region-docker.pkg.dev

    # 5. Construir la imagen Docker de la aplicación actual localmente
    docker build -t your-region-docker.pkg.dev/your-gcp-project-id/your-repo-name/chatbot-viajes-madrid:latest .

    # 6. Subir la imagen a Google Artifact Registry
    docker push your-region-docker.pkg.dev/your-gcp-project-id/your-repo-name/chatbot-viajes-madrid:latest

    # 7. Desplegar la imagen en Google Cloud Run
    # Reemplaza los valores de las variables de entorno con tus API Keys reales
    gcloud run deploy chatbot-viajes-madrid \
      --image your-region-docker.pkg.dev/your-gcp-project-id/your-repo-name/chatbot-viajes-madrid:latest \
      --platform managed \
      --region your-region \
      --allow-unauthenticated \
      --set-env-vars OPENAI_API_KEY=$OPENAI_API_KEY,SUPABASE_URL=$SUPABASE_URL,SUPABASE_KEY=$SUPABASE_KEY,LANGFUSE_PUBLIC_KEY=$LANGFUSE_PUBLIC_KEY,LANGFUSE_SECRET_KEY=$LANGFUSE_SECRET_KEY
    ```

### Consideraciones Adicionales durante el Desarrollo

* **Manejo de Errores:** Siempre piensa en cómo manejar errores (API no disponible, formato incorrecto, etc.). Implementa `try-except` blocks.
* **Logs:** Asegúrate de que tu aplicación genere logs útiles en los puntos clave del flujo.
* **Seguridad:** No expongas tus API Keys directamente en el código. Usa variables de entorno (ya cubierto).
* **Iteración:** Después de cada fase de prueba, revisa y refina. El proceso RAG a menudo requiere ajustes finos en el *chunking*, el *prompting* y la estrategia de búsqueda.
* **Documentación:** Mantén una buena documentación interna (comentarios en el código, READMEs, etc.) a medida que avanzas.

### Apéndice A: Gestión de la Base de Datos (Supabase)

Este apéndice detalla la estructura de las tablas necesarias en Supabase (PostgreSQL) para el proyecto del chatbot RAG. Se identifican los campos clave, sus tipos de datos, y los índices recomendados para optimizar el rendimiento de las consultas.

Para la gestión de Supabase, asumimos la utilización de la extensión `pgvector` para el almacenamiento y búsqueda de embeddings vectoriales.

#### A.1. Tabla `chunks_catalogos`

Esta tabla almacenará los fragmentos (chunks) de texto extraídos de los catálogos PDF, junto con sus embeddings vectoriales y metadatos relevantes para la búsqueda y contextualización.

* **Propósito**: Almacenar los chunks de los documentos, sus embeddings y metadatos para la recuperación contextual.
* **Campos**:
  * `id`: `SERIAL PRIMARY KEY` - Identificador único autoincremental para cada chunk.
  * `content`: `TEXT NOT NULL` - El texto original del chunk.
  * `embedding`: `VECTOR(1536) NOT NULL` - El vector de embedding generado por `text-embedding-3-small` de OpenAI (dimensión 1536).
  * `source_catalogue`: `TEXT NOT NULL` - Nombre del archivo del catálogo PDF del que proviene el chunk (ej. 'halcon_viajes_2025.pdf').
  * `page_number`: `INTEGER` - El número de página del PDF original de donde se extrajo el chunk (puede ser nulo si no se puede determinar).
  * `chunk_hash`: `TEXT UNIQUE NOT NULL` - Un hash SHA256 del `content` del chunk, utilizado para el caching de embeddings y asegurar la unicidad del contenido.
  * `keywords`: `TEXT[]` - Un array de palabras clave relevantes para el chunk, para posibles búsquedas híbridas o filtrado adicional.
  * `created_at`: `TIMESTAMP WITH TIME ZONE DEFAULT NOW()` - Marca de tiempo de creación del registro.

* **Índices**:
  * `chunks_catalogos_embedding_idx`: Índice para la columna `embedding` usando `ivfflat` o `hnsw` para optimizar la búsqueda de similitud vectorial. Se recomienda un índice `ivfflat` para empezar.
  * `chunks_catalogos_chunk_hash_idx`: Índice único en `chunk_hash` para optimizar las búsquedas de caché.
  * `chunks_catalogos_source_catalogue_idx`: Índice en `source_catalogue` para permitir búsquedas y filtrados rápidos por catálogo.

* **Prompt para Generación de la Tabla `chunks_catalogos` en Supabase SQL Editor**:

    ```text
    "Necesito el código SQL para crear la tabla `chunks_catalogos` en mi base de datos Supabase. La tabla debe tener las siguientes columnas: `id` (SERIAL PRIMARY KEY), `content` (TEXT NOT NULL), `embedding` (VECTOR(1536) NOT NULL), `source_catalogue` (TEXT NOT NULL), `page_number` (INTEGER), `chunk_hash` (TEXT UNIQUE NOT NULL), `keywords` (TEXT[]), y `created_at` (TIMESTAMP WITH TIME ZONE DEFAULT NOW()). Además, necesito el código para crear un índice `ivfflat` en la columna `embedding` (con `lists = 100` como punto de partida, ajusta según el volumen de datos) y un índice único en `chunk_hash`. También, incluye un índice en `source_catalogue`."
    ```

    **Código SQL resultante (ejemplo basado en el prompt):**

    ```sql
    -- Habilitar la extensión pgvector si aún no está habilitada
    -- Esta extensión se activa desde el panel de Supabase: Database -> Extensions
    -- CREATE EXTENSION IF NOT EXISTS vector;

    CREATE TABLE chunks_catalogos (
        id BIGSERIAL PRIMARY KEY,
        content TEXT NOT NULL,
        embedding VECTOR(1536) NOT NULL,
        source_catalogue TEXT NOT NULL,
        page_number INTEGER,
        chunk_hash TEXT UNIQUE NOT NULL,
        keywords TEXT[],
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );

    -- Creación del índice ivfflat para la columna embedding
    -- El número de `lists` debe ser aproximadamente `sqrt(num_rows)` o `num_rows / 1000`
    -- Ajusta `lists` según el tamaño esperado de tu tabla. Para 100k chunks, 300-500 lists podría ser un buen inicio.
    CREATE INDEX ON chunks_catalogos USING ivfflat (embedding vector_l2_ops) WITH (lists = 100);

    -- Índice único para el hash del chunk (para la caché y evitar duplicados)
    CREATE UNIQUE INDEX ON chunks_catalogos (chunk_hash);

    -- Índice para búsquedas y filtrados por catálogo de origen
    CREATE INDEX ON chunks_catalogos (source_catalogue);
    ```

#### A.2. Tabla `chat_history`

Esta tabla almacenará el historial de conversaciones entre los usuarios y el chatbot, permitiendo la persistencia de los chats y la recuperación de conversaciones pasadas.

* **Propósito**: Persistir el historial de conversaciones del chatbot para cada usuario.
* **Campos**:
  * `id`: `SERIAL PRIMARY KEY` - Identificador único autoincremental para cada interacción de chat.
  * `user_id`: `TEXT NOT NULL` - Identificador del usuario (ej. un ID de sesión, o un ID de usuario si se implementa autenticación).
  * `timestamp`: `TIMESTAMP WITH TIME ZONE DEFAULT NOW()` - Marca de tiempo de la interacción.
  * `user_message`: `TEXT NOT NULL` - El mensaje enviado por el usuario.
  * `bot_response`: `TEXT NOT NULL` - La respuesta generada por el chatbot.
  * `relevant_chunks_ids`: `BIGINT[]` - (Opcional, pero recomendado para Langfuse y depuración) Un array de IDs de los chunks de `chunks_catalogos` que fueron considerados relevantes para esta interacción. Esto ayuda a depurar y entender el origen de las respuestas.
  * `langfuse_trace_id`: `TEXT` - (Opcional, pero recomendado para Langfuse) ID de la traza de Langfuse asociada a esta interacción, para facilitar la vinculación entre el historial de chat y los datos de trazabilidad.

* **Índices**:
  * `chat_history_user_id_idx`: Índice en `user_id` para optimizar la recuperación del historial de chat de un usuario específico.
  * `chat_history_timestamp_idx`: Índice en `timestamp` para optimizar la ordenación por fecha del historial.

* **Prompt para Generación de la Tabla `chat_history` en Supabase SQL Editor**:

    ```text
    "Necesito el código SQL para crear la tabla `chat_history` en mi base de datos Supabase. La tabla debe tener las siguientes columnas: `id` (SERIAL PRIMARY KEY), `user_id` (TEXT NOT NULL), `timestamp` (TIMESTAMP WITH TIME ZONE DEFAULT NOW()), `user_message` (TEXT NOT NULL), `bot_response` (TEXT NOT NULL), `relevant_chunks_ids` (BIGINT[] para almacenar los IDs de los chunks usados, opcional) y `langfuse_trace_id` (TEXT para el ID de traza de Langfuse, opcional). Además, necesito el código para crear índices en `user_id` y `timestamp`."
    ```

    **Código SQL resultante (ejemplo basado en el prompt):**

    ```sql
    CREATE TABLE chat_history (
        id BIGSERIAL PRIMARY KEY,
        user_id TEXT NOT NULL,
        timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        user_message TEXT NOT NULL,
        bot_response TEXT NOT NULL,
        relevant_chunks_ids BIGINT[], -- Array de IDs de chunks relevantes
        langfuse_trace_id TEXT       -- ID de la traza de Langfuse
    );

    -- Índice para optimizar la recuperación del historial por usuario
    CREATE INDEX ON chat_history (user_id);

    -- Índice para optimizar la ordenación del historial por fecha/hora
    CREATE INDEX ON chat_history (timestamp);
    ```

¡Por supuesto! Es una excelente pregunta y un detalle técnico importante. La interacción con `pgvector` tiene sus particularidades tanto en la base de datos como en el código de tu aplicación.

Aquí tienes un apéndice específico sobre el uso de `pgvector` con Supabase, incluyendo la activación, librerías Python y consideraciones de configuración.

### Apéndice B: Uso de `pgvector` con Supabase

Este apéndice cubre los detalles específicos para la configuración y el uso de la extensión `pgvector` en Supabase, así como las implicaciones para el desarrollo en Python.

#### B.1. ¿Qué es `pgvector`?

`pgvector` es una extensión de PostgreSQL que permite almacenar y realizar operaciones de similitud eficientes en vectores de alta dimensión directamente dentro de tu base de datos PostgreSQL. Es fundamental para implementar un vector store donde se guardan los embeddings generados por los modelos de lenguaje (como `text-embedding-3-small`).

#### B.2. Configuración en Supabase (Lado del Servidor de Base de Datos)

Para utilizar `pgvector` con tu proyecto Supabase, debes habilitar la extensión. Esto **no se hace con código SQL directamente en tu aplicación**, sino a través del panel de control de Supabase.

1. **Acceder al Panel de Supabase**: Inicia sesión en tu cuenta de Supabase y selecciona tu proyecto.
2. **Navegar a Extensiones**: En el menú lateral, ve a la sección "Database" y luego selecciona "Extensions".
3. **Habilitar `pgvector`**: Busca `pgvector` en la lista de extensiones disponibles y haz clic en "Enable Extension".

    * **Importante**: Una vez habilitada, la extensión estará disponible para todas las bases de datos dentro de tu proyecto Supabase. No necesitas ejecutar `CREATE EXTENSION IF NOT EXISTS vector;` desde tu código de aplicación; la habilitación desde el panel de Supabase ya lo hace. Sin embargo, incluirlo en tus scripts de migración o creación inicial de tablas (como en el Apéndice A) es una buena práctica para la portabilidad, aunque en Supabase es un paso manual inicial.

#### B.3. Tipos de Datos de Vectores en PostgreSQL

Una vez habilitada, `pgvector` añade un nuevo tipo de dato a PostgreSQL: `VECTOR(dimensión)`.

* `VECTOR(1536)`: Esto especifica una columna que almacenará vectores flotantes con 1536 dimensiones. Es crucial que la dimensión coincida con la salida del modelo de embeddings que estás utilizando (`text-embedding-3-small` produce 1536 dimensiones).

#### B.4. Índices para Búsqueda de Similitud

Para que la búsqueda vectorial sea eficiente en grandes volúmenes de datos, es esencial crear índices específicos para la columna `embedding`. `pgvector` soporta dos tipos principales de índices para búsqueda aproximada de vecinos más cercanos (ANN):

* **`IVFFlat`**:
  * **Uso**: Es un buen punto de partida para la mayoría de los casos. Divide el espacio vectorial en clústeres.
  * **Parámetro `lists`**: Es el número de clústeres (listas) que se crearán. Afecta el rendimiento y la precisión.
    * Un valor más alto aumenta la precisión de búsqueda pero ralentiza la creación del índice y la búsqueda (más clústeres que revisar).
    * Un valor más bajo reduce la precisión pero acelera la búsqueda.
    * **Recomendación**: Para una tabla con `N` filas, un valor inicial de `lists` de `sqrt(N)` o `N / 1000` (para tablas muy grandes) es un buen punto de partida. Puedes ajustarlo experimentalmente.
  * **Parámetro `probes` (en la consulta)**: Es el número de clústeres a inspeccionar durante una búsqueda. Afecta la precisión. Un valor más alto significa mayor precisión a costa de una búsqueda más lenta. Esto se especifica en la consulta, no en la creación del índice.

* **`HNSW` (Hierarchical Navigable Small World)**:
  * **Uso**: Generalmente más rápido y preciso que `ivfflat` para muchos casos de uso, especialmente en conjuntos de datos dinámicos (donde hay muchas inserciones/actualizaciones). Sin embargo, consume más memoria y el tiempo de construcción del índice puede ser mayor.
  * **Parámetros**: `m` (número de vecinos salientes) y `ef_construction` (tamaño de la lista de vecinos más cercanos durante la construcción).
  * **Recomendación**: Si `ivfflat` no satisface tus necesidades de rendimiento/precisión, considera `hnsw`.

**Ejemplo de Creación de Índice (reiterado del Apéndice A)**:

```sql
-- Para ivfflat
CREATE INDEX ON chunks_catalogos USING ivfflat (embedding vector_l2_ops) WITH (lists = 100);

-- Para hnsw (si decides usarlo más adelante y tu versión de pgvector lo soporta y te es viable)
-- CREATE INDEX ON chunks_catalogos USING hnsw (embedding vector_l2_ops) WITH (m = 16, ef_construction = 64);
```

#### B.5. Uso de `pgvector` en Python (Lado de la Aplicación)

Desde tu aplicación Python, interactuarás con `pgvector` a través de la librería `supabase` (que a su vez utiliza un cliente PostgreSQL como `psycopg2` o `asyncpg` internamente).

1. **Instalación de Librerías**:
   * Ya las tienes en tu `requirements.txt`: `supabase`
   * `supabase` maneja la serialización/deserialización de los objetos `VECTOR` automáticamente con PostgreSQL, siempre y cuando la extensión esté habilitada y la columna esté definida correctamente. No necesitas una librería `pgvector` separada en Python.

2. **Envío de Embeddings a Supabase**:
    Cuando insertas datos en la tabla `chunks_catalogos`, simplemente pasas una lista o un array de floats (Python list, NumPy array) para la columna `embedding`. La librería `supabase` se encargará de convertirlo al formato `VECTOR` de PostgreSQL.

    ```python
    # Ejemplo conceptual de inserción
    from supabase import create_client, Client
    import numpy as np # Si usas numpy para los embeddings

    # Asume que supabase_client ya está inicializado desde config.py
    # supabase_client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    # ... (obtener chunks_con_embeddings de la fase de procesamiento) ...

    # chunk_data = {
    #     "content": "Contenido del chunk de prueba.",
    #     "embedding": np.array([0.1, 0.2, ..., 0.9]), # Un array de 1536 floats
    #     "source_catalogue": "catalogo_x.pdf",
    #     "page_number": 1,
    #     "chunk_hash": "abcdef12345...",
    #     "keywords": ["viaje", "madrid"]
    # }

    # data, count = supabase_client.table('chunks_catalogos').insert(chunk_data).execute()
    ```

3. **Realización de Búsquedas de Similitud Vectorial**:
    Las consultas de similitud se realizan utilizando operadores específicos de `pgvector`. Los más comunes son:
    * `L2 distance` (distancia euclidiana): `<->`
    * `cosine distance` (distancia coseno): `<=>`
    * `inner product` (producto interno): `<#>` (más negativo es más similar)

    Para búsquedas de similitud (donde un valor más bajo indica mayor similitud), usarás `<->` para distancia euclidiana o `<=>` para distancia coseno. Los embeddings de OpenAI suelen ser normalizados (magnitud 1), por lo que la distancia coseno y la distancia euclidiana (L2) están estrechamente relacionadas, y a menudo `<->` es suficiente.

    ```python
    # Ejemplo conceptual de búsqueda
    from supabase import create_client, Client
    import numpy as np

    # Asume que supabase_client ya está inicializado
    # y que query_embedding es el vector de la consulta del usuario

    # query_embedding = np.array([...]) # Embedding de la pregunta del usuario

    # Realizar la búsqueda de similitud L2 y limitar a top_k resultados
    # La operación `<->` devuelve la distancia euclidiana. Cuanto menor, más similar.
    # Usamos .order() y .limit() para obtener los top_k más cercanos.
    response = supabase_client.table('chunks_catalogos') \
        .select('content, source_catalogue, page_number, keywords') \
        .order('embedding <-> ' + str(list(query_embedding)), desc=False) \
        .limit(top_k) \
        .execute()

    # Los resultados estarán en response.data
    # data = response.data
    ```

    **Nota sobre la sintaxis de la consulta**: En la búsqueda de similitud, la forma más común es `ORDER BY <vector_column> <-> <query_vector> LIMIT K`. Al usar `supabase`, debes asegurarte de que el `query_vector` se serialice correctamente a una cadena que PostgreSQL pueda interpretar como un array de números. `str(list(query_embedding))` es una forma común de hacerlo si `query_embedding` es un array de NumPy.

#### B.6. Consideraciones de Coste y Rendimiento

* **Coste**: El almacenamiento de vectores en Supabase consume espacio en disco, lo que se contabiliza en tu plan de Supabase. La búsqueda vectorial indexada es eficiente en términos de CPU de la base de datos, pero las operaciones a gran escala pueden requerir planes más robustos de Supabase.
* **Rendimiento**:
  * El tamaño de los embeddings (1536 dimensiones) es estándar, pero impacta la memoria y el rendimiento.
  * Asegúrate de que tus índices (`ivfflat` o `hnsw`) estén correctamente configurados y ajustados (`lists`, `probes`, `m`, `ef_construction`) para el tamaño de tu dataset y los requisitos de latencia.
  * Las consultas que combinan filtros SQL tradicionales (ej. `WHERE source_catalogue = 'catalogo_X'`) con búsqueda vectorial (`ORDER BY embedding <-> ...`) pueden ser más complejas de optimizar y a veces requieren estrategias de índice compuesto o post-filtrado.

Este apéndice debería darte una comprensión sólida de cómo interactuar con `pgvector` en el contexto de Supabase para tu proyecto.
