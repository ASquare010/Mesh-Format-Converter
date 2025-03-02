import os

from .api import create_api

CACHE_ROOT = os.environ.get("CACHE_ROOT", "/vizcom/.cache")
app = create_api(CACHE_ROOT)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "apps.mesh_convert.src:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 7200)),
        reload=True,
    )
