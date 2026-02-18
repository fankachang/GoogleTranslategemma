from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import load_config
from .model import TranslateGemmaModel

from .routes.health import router as health_router
from .routes.translate import router as translate_router

app = FastAPI(title="TranslateGemma")
config = load_config()
app.state.config = config

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.get("cors", {}).get("allow_origins", ["*"]),
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    model_cfg = config.get("model", {})
    app.state.model = TranslateGemmaModel(model_cfg.get("name"), model_cfg.get("device"))
    # load model lazily but attempt to load for startup
    try:
        app.state.model.load()
    except Exception:
        # keep going even if model cannot be loaded in dev environments
        pass
    app.state.model_name = model_cfg.get("name")
    app.state.device = model_cfg.get("device")


# mount routers
app.include_router(health_router)
app.include_router(translate_router, prefix="/api")
