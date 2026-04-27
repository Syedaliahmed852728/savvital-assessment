import json
from .config import (
    GROQ_API_KEY,
    GROQ_MODEL,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    TEMPERATURE,
    MAX_TOKENS,
    TIMEOUT,
    MAX_RETRIES,
)


# loading clients data from clients.json
def load_client_profiles(file_path: str) -> list[dict]:
    """Loads client profiles from a JSON file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            raise ValueError("clients.json must contain a list of profiles")

        return data

    except Exception as e:
        raise RuntimeError(f"Failed to load client profiles: {e}")


# building prompt based on client's data
def build_prompt(client: dict) -> str:
    """
    Builds a structured prompt for the LLM.
    Designed to enforce clean JSON output with no extra text.
    """
    children_text = (
        "has children" if client["has_children"] else "does not have children"
    )
    property_text = (
        "owns real estate/property"
        if client["owns_property"]
        else "does not own property"
    )
    business_text = (
        "owns a business" if client["has_business"] else "does not own a business"
    )

    prompt = f"""You are a senior estate planning attorney AI assistant.
Analyse the client profile below and recommend appropriate estate planning instruments.

CLIENT PROFILE:
- Name: {client["name"]}
- Age: {client["age"]}
- Marital Status: {client["marital_status"]}
- Children: {children_text}
- Property: {property_text}
- Business: {business_text}

ESTATE PLANNING INSTRUMENTS YOU MAY RECOMMEND:
- Will: Specifies asset distribution and names guardians for children
- Living Trust: Transfers assets without probate, ideal for property owners
- Healthcare Directive: Documents medical wishes if incapacitated
- Power of Attorney: Delegates financial/legal decisions to a trusted person
- Business Succession Plan: Ensures business continuity for business owners
- Guardianship Designation: Legally names guardian for minor children

INSTRUCTIONS:
Based on this client profile, return ONLY a valid JSON object.
No explanation, no preamble, no markdown, no extra text.

The JSON must contain exactly these fields:

{{
  "client_name": "<full name>",
  "recommended_instruments": ["<instrument 1>", "<instrument 2>", ...],
  "rationale": "<1 to 3 sentences explaining why these instruments suit this client>",
  "urgency_flag": "<High or Medium or Low>"
}}

URGENCY GUIDELINES:
- High  : Age 55+, OR owns property AND has children, OR owns a business
- Medium: Has children OR owns property, but not both
- Low   : Young, single, no assets, no dependents

Single, young, no assets -> Will + Healthcare Directive -> Low urgency
Married with kids + property ->  Living Trust + Will + POA + Healthcare Directive -> High urgency
Business owner -> Living Trust + Business Succession Plan + POA -> High urgency
Divorced with children -> Will + POA + Healthcare Directive -> Medium-High urgency

Return ONLY the JSON object. No other text."""

    return prompt


# llm callers function for both groq and ollama with structured output validation and retry mechanism on failure
def call_groq(prompt: str) -> str:
    """groq api using langchain"""

    messages = [
        {
            "role": "system",
            "content": "You are an expert estate planning attorney AI. Always respond with valid JSON only — no markdown, no preamble, no extra text.",
        },
        {"role": "user", "content": prompt},
    ]

    model = ChatGroq(
        model=GROQ_MODEL,
        api_key=GROQ_API_KEY,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
        timeout=TIMEOUT,
        max_retries=MAX_RETRIES,
    )

    structured_model = model.with_structured_output(EstatePlanningRecommendation)

    return structured_model.invoke(messages)


def call_ollama(prompt: str) -> str:
    """Calls local Ollama instance."""
    messages = [
        {
            "role": "system",
            "content": "You are an expert estate planning attorney AI. Always respond with valid JSON only — no markdown, no preamble, no extra text.",
        },
        {"role": "user", "content": prompt},
    ]

    model = ChatOllama(
        model=OLLAMA_MODEL,
        base_url=OLLAMA_BASE_URL,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
        timeout=TIMEOUT,
        max_retries=MAX_RETRIES,
    )

    structured_model = model.with_structured_output(EstatePlanningRecommendation)

    return structured_model.invoke(messages)
