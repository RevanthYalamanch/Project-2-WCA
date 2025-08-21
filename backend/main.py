from fastapi import FastAPI
from src.api import routes

app = FastAPI(
    title="Web Content Analyzer API",
    description="An API to scrape and analyze web content.",
    version="1.0.0"
)

# Include the API router
app.include_router(routes.router)

@app.get("/health")
def health_check():
    """
    Simple health check endpoint.
    """
    return {"status": "ok"}