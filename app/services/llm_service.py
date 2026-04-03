from __future__ import annotations


class LLMService:
    def __init__(self, api_key: str | None, model: str) -> None:
        self.api_key = api_key
        self.model = model
        self.client = None
        self.import_error: str | None = None

        if not api_key:
            return

        try:
            from openai import OpenAI
        except ImportError as exc:
            self.import_error = str(exc)
            return

        self.client = OpenAI(api_key=api_key)

    @property
    def enabled(self) -> bool:
        return self.client is not None

    def ask(self, message: str, system_prompt: str) -> str | None:
        if not self.client:
            return None

        response = self.client.responses.create(
            model=self.model,
            instructions=system_prompt,
            input=message,
            max_output_tokens=600,
        )
        return response.output_text.strip()
