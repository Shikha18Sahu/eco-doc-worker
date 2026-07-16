# import json
# import re

# import google.generativeai as genai

# from app.core.config import settings

# genai.configure(api_key=settings.gemini_api_key)

# EXTRACTION_PROMPT = """You are a strict information extraction engine.
# Given raw OCR text from a scanned/handwritten form, extract exactly these fields:
# - name
# - amount
# - date

# Rules:
# - Return ONLY valid JSON, no markdown, no explanation, no backticks.
# - If a field is not present or unclear, set its value to null.
# - Do not guess values that are not supported by the text.

# OCR TEXT:
# {ocr_text}

# Return JSON in this exact shape:
# {{"name": "...", "amount": "...", "date": "..."}}
# """


# class LLMService:
#     def __init__(self, model_name: str = "models/gemini-flash-lite-latest"):
#         self.model = genai.GenerativeModel(model_name)

#     def extract_fields(self, raw_text: str) -> dict:
#         fields = {"name": None, "amount": None, "date": None}

#         if not raw_text.strip():
#             return fields

#         try:
#             prompt = EXTRACTION_PROMPT.format(ocr_text=raw_text)
#             response = self.model.generate_content(
#                 prompt,
#                 generation_config={"temperature": 0.0},
#             )
#             text = response.text.strip()

#             text = re.sub(r"^```json\s*|\s*```$", "", text.strip())

#             parsed = json.loads(text)
#             fields["name"] = parsed.get("name")
#             fields["amount"] = parsed.get("amount")
#             fields["date"] = parsed.get("date")

#         except Exception as e:
#             print(f"[LLMService ERROR] {type(e).__name__}: {e}")

#         return fields



import json
import re

import google.generativeai as genai

from app.core.config import settings

genai.configure(api_key=settings.gemini_api_key)

EXTRACTION_PROMPT = """You are a strict information extraction engine.

Given raw OCR text from a scanned/handwritten document, extract EVERY
field-name : value pair you can find in the text — do not limit yourself
to a fixed list of fields. Use the field label as it appears in the
document (normalized to lowercase snake_case, e.g. "ID No" -> "id_no").

Rules:
- Return ONLY valid JSON, no markdown, no explanation, no backticks.
- Return a flat JSON object: {{"field_name": "value", ...}}
- If a labeled field has no readable value, set it to null.
- Do not invent fields that are not present in the text.
- Do not include any field named "raw_text" or similar meta fields.

OCR TEXT:
{ocr_text}
"""


class LLMService:
    def extract_fields_with_schema(self, raw_text: str, expected_fields: list[str]) -> dict:
        """Schema-aware extraction: only asks for the fields defined
        by the matched document schema. Never invents extra fields."""
        import json
        import re

        fields = {f: None for f in expected_fields}

        if not raw_text.strip():
            return fields

        prompt = f"""You are a strict information extraction engine.

Given raw OCR text from a scanned/handwritten document, extract ONLY
these exact fields: {", ".join(expected_fields)}

Rules:
- Return ONLY valid JSON, no markdown, no explanation, no backticks.
- Return a flat JSON object with exactly these keys: {expected_fields}
- If a field is not present or unclear in the text, set its value to null.
- Do not invent fields outside this list. Do not omit any listed field.

OCR TEXT:
{raw_text}
"""
        try:
            response = self.model.generate_content(
                prompt,
                generation_config={"temperature": 0.0},
            )
            text = response.text.strip()
            text = re.sub(r"^```json\s*|\s*```$", "", text.strip())
            parsed = json.loads(text)

            for f in expected_fields:
                fields[f] = parsed.get(f)

        except Exception as e:
            print(f"[LLMService ERROR] {type(e).__name__}: {e}")

        return fields
    
    def __init__(self, model_name: str = "models/gemini-flash-lite-latest"):
        self.model = genai.GenerativeModel(model_name)

    def extract_fields(self, raw_text: str) -> dict:
        if not raw_text.strip():
            return {}

        try:
            prompt = EXTRACTION_PROMPT.format(ocr_text=raw_text)
            response = self.model.generate_content(
                prompt,
                generation_config={"temperature": 0.0},
            )
            text = response.text.strip()
            text = re.sub(r"^```json\s*|\s*```$", "", text.strip())

            parsed = json.loads(text)
            if not isinstance(parsed, dict):
                return {}

            return parsed

        except Exception as e:
            print(f"[LLMService ERROR] {type(e).__name__}: {e}")
            return {}