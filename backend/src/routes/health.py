from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/health")
def health(request: Request):
    app = request.app
    model = getattr(app.state, "model", None)
    model_loading = getattr(app.state, "model_loading", False)
    loaded = False
    if model is not None:
        loaded = getattr(model, "model", None) is not None

    if model_loading:
        status = "loading"
    elif loaded:
        status = "ok"
    elif model is not None:
        status = "degraded"  # model 物件存在但未載入
    else:
        status = "error"

    resolved_device = None
    if model is not None:
        resolved_device = getattr(model, "_resolved_device", None)

    return {
        "status": status,
        "model_name": getattr(app.state, "model_name", None),
        "device": getattr(app.state, "device", None),
        "resolved_device": resolved_device,
        "model_loaded": loaded,
    }
