import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles
from swagger_ui_bundle import swagger_ui_path
from .config import load_config
from .backends import create_backend, OllamaBackend, LocalBackend
from .session_manager import SessionManager

from .routes.health import router as health_router
from .routes.translate import router as translate_router
from .routes.languages import router as languages_router
from .routes.glossary import router as glossary_router
from .routes.config import router as config_router
from .routes.sessions import router as sessions_router
from .routes.stats import router as stats_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

config = load_config()


@asynccontextmanager
async def lifespan(app: FastAPI):
    model_cfg = config.get("model", {})
    backend = create_backend(config)
    app.state.model = backend
    app.state.model_name = model_cfg.get("name") if isinstance(backend, LocalBackend) else model_cfg.get("ollama_model")
    app.state.device = model_cfg.get("device") if isinstance(backend, LocalBackend) else None
    app.state.glossary = config.get("glossary", {"enabled": False, "entries": []})
    app.state.config = config
    
    # 初始化會話管理器
    session_manager = SessionManager(session_timeout_seconds=900)
    app.state.session_manager = session_manager
    await session_manager.start_cleanup_task(check_interval_seconds=60)

    if isinstance(backend, LocalBackend):
        app.state.model_loading = True

        async def _load_model():
            loop = asyncio.get_event_loop()
            try:
                await loop.run_in_executor(None, backend.load)
            except Exception:  # noqa: BLE001
                pass
            finally:
                app.state.model_loading = False

        asyncio.create_task(_load_model())
    else:
        app.state.model_loading = False
        # OllamaBackend: 非同步啟動驗證（非阻塞）
        asyncio.create_task(backend.startup())

    yield

    # Lifespan 結束：釋放會話管理器與後端資源
    await session_manager.stop_cleanup_task()
    if isinstance(backend, OllamaBackend):
        await backend.aclose()


app = FastAPI(title="TranslateGemma", lifespan=lifespan, docs_url=None)


def _custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    app.openapi_schema = get_openapi(
        title=app.title,
        version="0.1.0",
        openapi_version="3.0.3",
        routes=app.routes,
    )
    return app.openapi_schema


app.openapi = _custom_openapi

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.get("cors", {}).get("allow_origins", ["*"]),
    allow_methods=["*"],
    allow_headers=["*"],
)

# 掛載 swagger-ui 靜態檔案（離線支援）
app.mount("/swagger-ui-static", StaticFiles(directory=swagger_ui_path), name="swagger-ui-static")


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title=app.title + " - Swagger UI",
        swagger_js_url="/swagger-ui-static/swagger-ui-bundle.js",
        swagger_css_url="/swagger-ui-static/swagger-ui.css",
        swagger_favicon_url="/swagger-ui-static/favicon-32x32.png",
    )


# mount routers
app.include_router(health_router)
app.include_router(translate_router, prefix="/api")
app.include_router(languages_router, prefix="/api")
app.include_router(glossary_router, prefix="/api")
app.include_router(config_router, prefix="/api")
app.include_router(sessions_router, prefix="/api")
app.include_router(stats_router, prefix="/api")

