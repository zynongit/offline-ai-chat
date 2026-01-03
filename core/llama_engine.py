from llama_cpp import Llama
from core.config import MODEL_PATH, CTX_SIZE, TEMPERATURE

class LlamaEngine:
    def __init__(self):
        self.llm = Llama(
            model_path=MODEL_PATH,
            n_ctx=CTX_SIZE
        )

    def stream(self, prompt: str):
        for output in self.llm(
            prompt,
            temperature=TEMPERATURE,
            stream=True
        ):
            token = output["choices"][0]["text"]
            if token:
                yield token
