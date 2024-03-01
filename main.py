from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from api.v1.apis import router as router_v1  # noqa: F401

app = FastAPI()
app.include_router(router_v1)


@app.get("/")
async def root():
    with open("static/index.html", "r") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)
