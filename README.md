# Jarvis

Asistente de voz personal que se ejecuta en local en Windows. Entiende órdenes en lenguaje natural, decide qué acción ejecutar y responde hablando.

## Qué hace hoy

- Transcribe tu voz a texto
- Un LLM decide qué acción ejecutar (function calling), con un prompt fijo oculto al usuario
- Abre aplicaciones y juegos buscándolos automáticamente: Steam, Menú Inicio y escaneo de discos
- Responde con voz sintética

## Arquitectura

Capas independientes que se comunican mediante interfaces (`Command`, `CommandResult`, `Action`, `LLMClient`, `Transcriber`, `Speaker`):

- `core/`: modelos de datos compartidos
- `audio/`: micrófono, voz a texto y texto a voz
- `brain/`: prompt fijo y router que traduce texto en un `Command`
- `actions/`: una clase por acción ejecutable, más el registro que las conecta
- `integrations/`: clientes de servicios externos (LLM)

Cambiar de proveedor de LLM, de motor de voz o añadir una acción nueva no requiere tocar el resto del sistema.

## Instalación

1. `python -m venv venv` y activar el entorno virtual
2. `pip install -r requirements.txt`
3. Copiar `.env.example` a `.env` y añadir `GEMINI_API_KEY`
4. `python src/playground.py`

## Tests

`pytest`

## Roadmap

- [x] Router con function calling
- [x] Voz de entrada y de salida
- [x] Apertura automática de apps y juegos
- [ ] Palabra de activación
- [ ] Control de Spotify
- [ ] Correo con confirmación
- [ ] Visión de pantalla
- [ ] Auditoría de seguridad