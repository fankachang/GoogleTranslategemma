from fastapi import APIRouter, Request, HTTPException
from fastapi import status as http_status
from backend.src.schemas.translation import TranslationRequest, TranslationResponse
from backend.src.language_detect import detect_language

router = APIRouter()


@router.post("/translate", response_model=TranslationResponse)
def translate_endpoint(request: TranslationRequest, req: Request):
    """Simple non-streaming translate endpoint.
    Uses app.state.model if available, otherwise returns a placeholder translation.
    """
    text = request.text
    if not text or not text.strip():
        raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail="Text must not be empty")

    detected = request.source_lang or detect_language(text)
    target = request.target_lang or ("en" if detected == "zh-TW" else "zh-TW")

    model = getattr(req.app.state, "model", None)
    try:
        if model is not None:
            translated = model.translate(text, source_lang=detected, target_lang=target)
        else:
            translated = f"TRANSLATED: {text}"
    except Exception:
        raise HTTPException(status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Translation failed")

    return TranslationResponse(translated_text=translated, detected_source_lang=detected, model_name=getattr(req.app.state, "model_name", None))
