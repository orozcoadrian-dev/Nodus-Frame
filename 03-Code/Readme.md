# Entorno agéntico para Gemma 4

Base Python sin dependencias externas para experimentar con agentes que usan herramientas conforme al formato de Gemma 4.

## Ejecutar

Desde esta carpeta:

```powershell
python main.py
python -m unittest discover -s tests -v
```

La demo es completamente offline: `DemoModel` simula primero una llamada a clima y luego una respuesta final. Para usar un modelo real, crea una clase con `generate(prompt)` y pásala al constructor de `Agent`.

## Piezas principales

`Agent` recibe un historial, un prompt de sistema, herramientas tipadas y un modelo. `gemma_protocol.py` genera los turnos:

```text
<|turn>system
...
<turn|>
<|turn>user
...
<turn|>
```

También soporta `<|think|>`, `<|tool>`, `<|tool_call>`, `<|tool_response>` y el delimitador de cadenas `<|"|>` documentados para Gemma 4.

## Añadir una herramienta

```python
from agent import Agent, Tool

tool = Tool(
    name="buscar",
    description="Busca información autorizada.",
    parameters={"type": "object", "properties": {"query": {"type": "string"}}},
    function=mi_funcion,
)
agent = Agent(model, "Asistente útil y preciso.", [tool])
respuesta = agent.run("...")
```

Antes de producción, añade autenticación, allowlists, validación estricta de argumentos, timeouts y observabilidad. Este es un runtime base, no un sandbox de seguridad.

Consulta también [Agents.md](Agents.md) para el contrato operativo y las decisiones de arquitectura.