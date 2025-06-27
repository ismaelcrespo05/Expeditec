# run.py
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "Expeditec.asgi:application",
        lifespan="off",
        host="0.0.0.0",
        port=80,
        reload=True
    )