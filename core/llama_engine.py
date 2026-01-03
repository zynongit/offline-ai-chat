from llama_cpp import Llama
from core.config import MODEL_PATH, CTX_SIZE, MAX_TOKENS, TEMPERATURE

class LlamaEngine:
    def __init__(self):
        self.llm = Llama(
            model_path=MODEL_PATH,
            n_ctx=CTX_SIZE
        )

    def generate(self, prompt: str) -> str:
        output = self.llm(
            prompt,
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE,
            stop=["</s>"]
        )
        return output["choices"][0]["text"].strip()
