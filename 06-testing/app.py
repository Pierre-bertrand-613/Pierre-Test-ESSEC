"""FastAPI + Groq example from slide 93, fixed so it can be tested.

Changes compared to the slide version:
- `import os` was missing
- the Groq client is created lazily through a FastAPI dependency (`get_client`),
  so the app can be imported without an API key and tests can replace it with a mock
- `mixtral-8x7b-32768` has been decommissioned by Groq -> `llama-3.3-70b-versatile`
"""
import os
from functools import lru_cache

import groq
from fastapi import Depends, FastAPI, HTTPException
from groq import Groq
from pydantic import BaseModel

MODEL = "llama-3.3-70b-versatile"

app = FastAPI()


@lru_cache(maxsize=1)
def get_client() -> Groq:
    """One shared client for the whole app (created on first request)."""
    return Groq(
        api_key=os.environ.get("GROQ_API_KEY"),
        timeout=20.0,       # 20 seconds (default is 1 minute)
        max_retries=1,
    )


class Prompt(BaseModel):
    prompt: str


@app.get("/status")
async def get_status():
    return {"message": "OK"}


@app.post("/chat")
async def post_chat(prompt: Prompt, client: Groq = Depends(get_client)):
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt.prompt},
            ],
            model=MODEL,
        )
        return {"response": chat_completion.choices[0].message.content}

    except groq.APIConnectionError as e:
        print("The server could not be reached")
        print(e.__cause__)  # an underlying Exception, likely raised within httpx.
        raise HTTPException(status_code=500, detail="API Connection Error")

    except groq.RateLimitError:
        print("A 429 status code was received; we should back off a bit.")
        raise HTTPException(status_code=429, detail="Rate Limit Exceeded")

    except groq.APIStatusError as e:
        print("Another non-200-range status code was received")
        print(e.status_code)
        print(e.response)
        raise HTTPException(status_code=e.status_code, detail="API Status Error")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5000)
