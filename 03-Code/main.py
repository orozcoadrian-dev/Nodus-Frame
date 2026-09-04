"""CLI offline de demostración; conecta aquí tu backend de inferencia Gemma."""

from agent import Agent, Tool
from tools import WEATHER_TOOL


class DemoModel:
    """Model stub para validar el bucle sin descargar pesos."""

    def __init__(self) -> None:
        self.used_tool = False

    def generate(self, prompt: str) -> str:
        if not self.used_tool:
            self.used_tool = True
            return '<|tool_call>call:get_weather{city:<|"|>Madrid<|"|>}<tool_call|>'
        return "El clima en Madrid es soleado y hay 18 C."


def main() -> None:
    tool = Tool(**WEATHER_TOOL)
    agent = Agent(DemoModel(), "Eres un asistente útil. Usa herramientas cuando sea necesario.", [tool])
    print(agent.run("Que tiempo hace en Madrid?"))


if __name__ == "__main__":
    main()