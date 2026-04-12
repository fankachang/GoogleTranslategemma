from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/health")
def health(request: Request):
    app = request.app
    backend = getattr(app.state, "model", None)
    model_loading = getattr(app.state, "model_loading", False)

    if backend is None:
        return {
            "status": "error",
            "backend": "unknown",
            "model": None,
            "model_name": None,
            "device": None,
            "resolved_device": None,
            "model_loaded": False,
            "ollama_url": None,
        }

    info = backend.health_info()

    # LocalBackend: 覆蓋狀態為 loading（載入任務在背景執行）
    if model_loading:
        info["status"] = "loading"

    return info
