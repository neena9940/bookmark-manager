import httpx

# Ollama runs locally at this address
OLLAMA_API_URL = "http://localhost:11434/api/generate"


async def generate_bookmark_summary(title: str, url: str) -> str:
    """
    Sends the title and URL to Ollama (local AI) and asks for a 1-sentence summary.
    """
    try:
        print(f"DEBUG: Calling Ollama for '{title}'...")

        prompt = (
            "You are a helpful assistant. Provide a concise, 1-sentence summary "
            "of the webpage based on its title and URL. Do not use quotes.\n\n"
            f"Title: {title}\nURL: {url}"
        )

        # We use httpx to talk to the local Ollama server
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                OLLAMA_API_URL,
                json={
                    "model": "llama3.2",
                    "prompt": prompt,
                    "stream": False
                }
            )

        response.raise_for_status()
        data = response.json()
        summary = data.get("response", "").strip()

        print(f"DEBUG: Ollama returned: {summary}")
        return summary if summary else "AI summary unavailable."

    except Exception as e:
        print(f"ERROR: Ollama call failed! Type: {type(e).__name__}, Message: {str(e)}")
        return "AI summary unavailable."