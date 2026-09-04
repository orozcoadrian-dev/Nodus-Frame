import unittest

from agent import Agent, Tool
from gemma_protocol import Message, parse_tool_calls, render_prompt


class ScriptedModel:
    def __init__(self) -> None:
        self.responses = [
            '<|channel>thought necesito consultar<channel|><|tool_call>call:add{left:2,right:3}<tool_call|>',
            "El resultado es 5.",
        ]

    def generate(self, prompt: str) -> str:
        return self.responses.pop(0)


class AgentTests(unittest.TestCase):
    def test_parses_gemma_tool_call(self) -> None:
        calls = parse_tool_calls('<|tool_call>call:search{query:<|"|>a,b<|"|>,limit:2}<tool_call|>')
        self.assertEqual(calls[0].name, "search")
        self.assertEqual(calls[0].arguments, {"query": "a,b", "limit": 2})

    def test_executes_tool_and_hides_thought(self) -> None:
        tool = Tool("add", "Suma dos enteros", {}, lambda left, right: left + right)
        result = Agent(ScriptedModel(), "Sé útil.", [tool], thinking=True).run("Suma 2 y 3")
        self.assertEqual(result, "El resultado es 5.")

    def test_renders_system_and_user_turns(self) -> None:
        prompt = render_prompt([Message("system", "Hola"), Message("user", "Mundo")])
        self.assertIn("<|turn>system\nHola<turn|>", prompt)
        self.assertIn("<|turn>user\nMundo<turn|>", prompt)


if __name__ == "__main__":
    unittest.main()