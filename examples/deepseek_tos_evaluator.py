import json
import os

from openai import OpenAI

from skillware.core.env import load_env_file
from skillware.core.loader import SkillLoader

load_env_file()

bundle = SkillLoader.load_skill("compliance/tos_evaluator")
print(f"Loaded Skill: {bundle['manifest']['name']}")

TOSEvaluatorSkill = bundle["module"].TOSEvaluatorSkill
tos_skill = TOSEvaluatorSkill()

deepseek_tool = SkillLoader.to_deepseek_tool(bundle)
tool_name = deepseek_tool["function"]["name"]
print(f"DeepSeek tool name: {tool_name}")

client = OpenAI(
    api_key=os.environ.get("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)

user_query = (
    "Before an agent crawls https://hackernoon.com/tagged/ai for research, "
    "check whether that appears allowed."
)
print(f"User: {user_query}")

messages = [
    {"role": "system", "content": bundle["instructions"]},
    {"role": "user", "content": user_query},
]

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=messages,
    tools=[deepseek_tool],
)

while response.choices[0].message.tool_calls:
    assistant_message = response.choices[0].message
    tool_call = assistant_message.tool_calls[0]

    if tool_call.function.name != tool_name:
        print(f"Unexpected tool: {tool_call.function.name}")
        break

    fn_args = json.loads(tool_call.function.arguments)
    print(f"DeepSeek requested tool: {tool_call.function.name}")
    print(f"Input: {fn_args}")

    result = tos_skill.execute(fn_args)
    print(json.dumps(result, indent=2))

    messages.append(assistant_message)
    messages.append(
        {
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(result),
        }
    )

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        tools=[deepseek_tool],
    )

print("\nFinal Response:")
print(response.choices[0].message.content or "")
