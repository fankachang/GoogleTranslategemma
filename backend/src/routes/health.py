from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/health")
def health(request: Request):
    app = request.app
    model = getattr(app.state, "model", None)
    loaded = False
    if model is not None:
        # model.model is None when real model not loaded
        loaded = getattr(model, "model", None) is not None
    return {
        "status": "ok",
        "model_name": getattr(app.state, "model_name", None),
        "device": getattr(app.state, "device", None),
        "model_loaded": loaded,
    }
