# proxy.py — G-Pattern Sovereign Identity Proxy
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sovereign_kernel import SovereignKernel

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler("proxy.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("G-Proxy")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

kernel = SovereignKernel()

@app.get("/v1/models")
async def list_models():
    logger.info("Model list requested")
    return JSONResponse(content={
        "object": "list",
        "data": [{
            "id": "g-pattern-sovereign",
            "object": "model",
            "created": 1677649200,
            "owned_by": "openai",
            "permission": [{
                "id": "modelperm-123",
                "object": "model_permission",
                "created": 1677649200,
                "allow_create_engine": False,
                "allow_sampling": True,
                "allow_logprobs": True,
                "allow_search_indices": False,
                "allow_view": True,
                "allow_fine_tuning": False,
                "organization": "*",
                "group": None,
                "is_blocking": False
            }],
            "root": "g-pattern-sovereign",
            "parent": None
        }]
    })

@app.post("/v1/chat/completions")
async def chat(request: Request):
    try:
        payload = await request.json()
        messages = payload.get("messages", [])
        
        # Extract last user message
        user_input = ""
        for m in reversed(messages):
            if m["role"] == "user":
                user_input = m["content"]
                break
        
        if not user_input:
            return JSONResponse(status_code=400, content={"error": "No user message found"})
        
        # Route through Sovereign Kernel
        response_text = kernel.process_prompt(user_input)
        
        # Format as OpenAI response
        return JSONResponse(content={
            "id": "sovereign-chat",
            "object": "chat.completion",
            "created": 0,
            "model": "g-pattern-sovereign",
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": response_text
                },
                "finish_reason": "stop"
            }]
        })
    except Exception as e:
        logger.error(f"Proxy Error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.on_event("shutdown")
def shutdown_event():
    kernel.shutdown()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
