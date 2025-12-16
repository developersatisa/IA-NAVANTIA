from fastapi import FastAPI
from app.api.routes import router as api_router

app = FastAPI(
    title="Social Security PDF Analyzer",
    description="API to analyze Social Security pension calculation PDFs using OpenAI",
    version="1.0.0",
    root_path="/ia_servicios"
)

app.include_router(api_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
