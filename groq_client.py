import requests

from config import GROQ_API_KEY


class GroqClient:
    def __init__(self):
        self.api_key = GROQ_API_KEY
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "llama-3.3-70b-versatile"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

    def _make_request(self, messages):
        payload = {
            "model": self.model,
            "messages": messages,
        }
        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
        except requests.exceptions.RequestException as error:
            print(f"Error calling Groq API: {error}")
            return None
        except (KeyError, IndexError) as error:
            print(f"Error parsing Groq API response: {error}")
            return None

    def fix_grammar(self, text):
        messages = [
            {
                "role": "system",
                "content": "You are a grammar and spelling correction assistant. Fix the grammar and spelling of the given text. Return ONLY the corrected text. Do not include any explanations, quotes, or markdown formatting unless the original text had it. If the text is already correct, return it exactly as is.",
            },
            {
                "role": "user",
                "content": text,
            },
        ]
        return self._make_request(messages)

    def translate_text(self, text):
        messages = [
            {
                "role": "system",
                "content": "You are a translator. If the following text is in English, translate it to Bengali. If the following text is in Bengali, translate it to English. If it is mixed or another language, translate it to the other language (English or Bengali) that makes the most sense. Return ONLY the translated text. Do not include any explanations.",
            },
            {
                "role": "user",
                "content": text,
            },
        ]
        return self._make_request(messages)

    def explain_code(self, text):
        messages = [
            {
                "role": "system",
                "content": "You are a programming tutor. Explain the selected code line by line in plain, concise language so the user can quickly understand it. Return plain text only. Use the format 'Line N: explanation'. Keep each explanation brief. If a line is blank, a brace, or part of the structure only, explain it together with the nearest meaningful line instead of wasting space.",
            },
            {
                "role": "user",
                "content": text,
            },
        ]
        return self._make_request(messages)

    def summarize_text(self, text):
        messages = [
            {
                "role": "system",
                "content": "You are a concise summarization assistant. Summarize the selected text into short, easy bullet points. Return plain text only. Use simple language, keep it concise, and focus only on the most important ideas. Start every point with '- '.",
            },
            {
                "role": "user",
                "content": text,
            },
        ]
        return self._make_request(messages)

    def explain_text(self, text):
        messages = [
            {
                "role": "system",
                "content": "You are a clarity assistant. Explain the selected text in plain, simple language so it is easier to understand. Return plain text only. Be brief but helpful, and break the explanation into short paragraphs or compact bullet points when useful.",
            },
            {
                "role": "user",
                "content": text,
            },
        ]
        return self._make_request(messages)
