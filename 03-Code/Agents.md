# Entorno agéntico Gemma 4

Este proyecto implementa un agente Python pequeño y extensible siguiendo el protocolo de instrucciones de Gemma 4.

## Arquitectura

- `gemma_protocol.py`: tokens de control, renderizado de turnos y parser de `tool_call`.
- `agent.py`: historial, ciclo modelo -> herramienta -> modelo y captura de errores de herramientas.
- `tools.py`: herramienta de ejemplo y su esquema.
- `main.py`: demostración offline con un modelo simulado.
- `tests/`: pruebas sin red ni pesos de modelo.

## Contrato de integración

Implementa `Model.generate(prompt: str) -> str` para conectar Transformers, vLLM, Ollama u otro backend. El backend debe devolver texto con el formato Gemma 4. El agente intercepta:

```text
<|tool_call>call:nombre{clave:<|"|>valor<|"|>}<tool_call|>
```

Las respuestas se reinyectan como `tool_responses`. El contenido de `<|channel>thought ... <channel|>` se mantiene fuera de la respuesta visible.

## Reglas operativas

1. Valida esquemas y permisos antes de conectar herramientas reales.
2. Mantén las credenciales fuera del código y usa variables de entorno.
3. Define límites de iteraciones, tiempo y tamaño de salida.
4. No muestres el canal de pensamiento al usuario final.
5. En conversaciones normales elimina pensamientos previos; durante un ciclo de herramientas consérvalos hasta recibir la respuesta final.

La implementación se basa en la documentación oficial: https://ai.google.dev/gemma/docs/core/prompt-formatting-gemma4?hl=es-419