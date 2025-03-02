from fastapi import FastAPI

from gradio.routes import mount_gradio_app


def create_api(CACHE_ROOT: str):
    from fastapi.middleware.cors import CORSMiddleware

    web_app = FastAPI(title="Mesh Convert")

    web_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @web_app.get("/health")
    async def health_check():

        return {
            "status": "healthy",
            "workflow_loaded": True,
        }

    from .gradio import gradio

    mount_gradio_app(web_app, gradio(), path="/", allowed_paths=[CACHE_ROOT])

    return web_app
