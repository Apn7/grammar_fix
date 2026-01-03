import google.generativeai as genai
from config import GEMINI_API_KEY

class GeminiClient:
    def __init__(self):
        genai.configure(api_key=GEMINI_API_KEY)
        # Using gemini-2.0-flash as selected from available models
        self.model = genai.GenerativeModel('gemini-2.0-flash')

    def fix_grammar(self, text):
        prompt = f"""
        Please fix the grammar and spelling of the following text. 
        Return ONLY the corrected text. Do not include any explanations, quotes, or markdown formatting unless the original text had it.
        If the text is already correct, return it exactly as is.
        
        Text to fix:
        {text}
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            try:
                print("Attempting to list available models...")
                for m in genai.list_models():
                    if 'generateContent' in m.supported_generation_methods:
                        print(m.name)
            except Exception as list_e:
                print(f"Could not list models: {list_e}")
            return None

    def translate_text(self, text):
        prompt = f"""
        You are a translator. 
        If the following text is in English, translate it to Bengali.
        If the following text is in Bengali, translate it to English.
        If it is mixed or another language, translate it to the other language (English or Bengali) that makes the most sense.
        Return ONLY the translated text. Do not include any explanations.
        
        Text to translate:
        {text}
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Error calling Gemini API for translation: {e}")
            return None
