import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import load_config
from .model import TranslateGemmaModel

from .routes.health import router as health_router
from .routes.translate import router as translate_router
from .routes.languages import router as languages_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

config = load_config()


@asynccontextmanager
async def lifespan(app: FastAPI):
    model_cfg = config.get("model", {})
    translation_cfg = config.get("translation", {})
    app.state.model = TranslateGemmaModel(
        model_name=model_cfg.get("name", "4b"),
        device=model_cfg.get("device", "auto"),
        base_path=model_cfg.get("base_path", "models"),
        dtype=model_cfg.get("dtype", "auto"),
        max_new_tokens=translation_cfg.get("max_new_tokens", 512),
    )
    try:
        app.state.model.load()
    except Exception:
        pass
    app.state.model_name = model_cfg.get("name")
    app.state.device = model_cfg.get("device")
    app.state.glossary = config.get("glossary", {"enabled": False, "entries": []})
    app.state.config = config
    yield


app = FastAPI(title="TranslateGemma", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.get("cors", {}).get("allow_origins", ["*"]),
    allow_methods=["*"],
    allow_headers=["*"],
)

# mount routers
app.include_router(health_router)
app.include_router(translate_router, prefix="/api")
app.include_router(languages_router, prefix="/api")

