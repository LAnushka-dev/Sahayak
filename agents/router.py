from agents.state import AgentState
from ml.intent_classifier import LegalIntentClassifier

classifier = LegalIntentClassifier()

# Map language dropdown labels to codes
LANG_MAP = {
    "Hindi (हिंदी)": "hi",
    "Marathi (मराठी)": "mr",
    "Bengali (বাংলা)": "bn",
    "Tamil (தமிழ்)": "ta",
    "Telugu (తెలుగు)": "te",
    "Kannada (ಕನ್ನಡ)": "kn",
    "Malayalam (മലയാളം)": "ml",
    "Gujarati (ગુજરાતી)": "gu",
    "Punjabi (ਪੰਜਾਬੀ)": "pa",
    "Odia (ଓଡ଼ିଆ)": "or",
    "English": "en"
}

def router_node(state: AgentState) -> dict:
    """
    Router Agent: Analyzes user input across 10 Indian languages + English,
    classifies legal intent, detects language, and logs trace.
    """
    input_text = state["query"]
    if state.get("ocr_extracted_text"):
        input_text += f"\nDocument Context: {state['ocr_extracted_text']}"

    prediction = classifier.predict(input_text)
    intent = prediction["intent"]
    
    # If user explicitly specified a preferred language in state, respect it
    user_lang = state.get("detected_language")
    if user_lang and user_lang in LANG_MAP.values():
        lang = user_lang
    elif user_lang in LANG_MAP:
        lang = LANG_MAP[user_lang]
    else:
        lang = prediction["detected_language"]

    trace = state.get("agent_trace", [])
    trace.append(f"[Router Agent] Intent: {intent} (Conf: {prediction['confidence']:.2f}) | Language: {lang}")

    return {
        "intent": intent,
        "detected_language": lang,
        "agent_trace": trace,
        "retry_count": state.get("retry_count", 0)
    }
