from core.llama_engine import LlamaEngine
from core.memory import load_memory, save_memory

engine = LlamaEngine()
memory = load_memory()

print("Offline AI Chat 🤖 (type 'exit' to quit)\n")

while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        break

    prompt = "\n".join(memory + [f"User: {user_input}", "AI:"])
    response = engine.generate(prompt)

    print(f"AI: {response}\n")

    memory.append(f"User: {user_input}")
    memory.append(f"AI: {response}")
    save_memory(memory)
