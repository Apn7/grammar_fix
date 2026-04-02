from google import genai
from google.genai import types

from config import VERTEX_PROJECT_ID, VERTEX_LOCATION


class VertexClient:
    def __init__(self, model="gemini-2.5-flash"):
        if not VERTEX_PROJECT_ID:
            raise ValueError("VERTEX_PROJECT_ID is not set in .env")
        self.model = model
        self.client = genai.Client(
            vertexai=True,
            project=VERTEX_PROJECT_ID,
            location=VERTEX_LOCATION,
        )

    def _generate_text(self, instruction: str, text: str) -> str | None:
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=f"{instruction}\n\nSelected text:\n{text}",
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    max_output_tokens=2048,
                ),
            )
            return response.text.strip() if response.text else None
        except Exception as error:
            print(f"Error calling Vertex AI API: {error}")
            return None

    def fix_grammar(self, text: str) -> str | None:
        return self._generate_text(
            "You are a grammar and spelling correction assistant. Fix the grammar and spelling of the given text. Return ONLY the corrected text. Do not include any explanations, quotes, or markdown formatting unless the original text had it. If the text is already correct, return it exactly as is.",
            text,
        )

    def translate_text(self, text: str) -> str | None:
        return self._generate_text(
            "You are a translator. If the following text is in English, translate it to Bengali. If the following text is in Bengali, translate it to English. If it is mixed or another language, translate it to the other language (English or Bengali) that makes the most sense. Return ONLY the translated text. Do not include any explanations.",
            text,
        )

    def explain_code(self, text: str) -> str | None:
        return self._generate_text(
            "You are a programming tutor. Explain the selected code line by line in plain, concise language so the user can quickly understand it. Return plain text only. Use the format 'Line N: explanation'. Keep each explanation brief. If a line is blank, a brace, or part of the structure only, explain it together with the nearest meaningful line instead of wasting space.",
            text,
        )

    def summarize_text(self, text: str) -> str | None:
        return self._generate_text(
            "You are a concise summarization assistant. Summarize the selected text into short, easy bullet points. Return plain text only. Use simple language, keep it concise, and focus only on the most important ideas. Start every point with '- '.",
            text,
        )

    def explain_text(self, text: str) -> str | None:
        return self._generate_text(
            "You are a clarity assistant. Explain the selected text in plain, simple language so it is easier to understand. Return plain text only. Be brief but helpful, and break the explanation into short paragraphs or compact bullet points when useful.",
            text,
        )
