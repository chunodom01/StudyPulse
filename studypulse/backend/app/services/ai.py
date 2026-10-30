import asyncio

from google import genai

from app.config import settings

client = genai.Client(api_key=settings.gemini_api_key) if settings.gemini_api_key else None

MODELS = [
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-3.8-flash",
]


def basic_tip(sessions: list[dict]) -> str:
    if not sessions:
        return "No sessions yet. Add your first study session to get a tip."

    total = sum(s["minutes"] for s in sessions)
    by_subject = {}
    for s in sessions:
        key = s["subject"].strip().lower()
        by_subject[key] = by_subject.get(key, 0) + s["minutes"]

    top = max(by_subject, key=by_subject.get)
    least = min(by_subject, key=by_subject.get)

    tip = f"You studied {total} minutes in total. Most time: {top} ({by_subject[top]} min)."
    if top != least:
        tip += f" Try giving {least} a bit more time ({by_subject[least]} min so far)."
    return tip


async def generate_tip(sessions: list[dict]) -> str:
    if not sessions:
        return basic_tip(sessions)
    if client is None:
        return basic_tip(sessions)

    summary = "\n".join(f"- {s['subject']}: {s['minutes']} min" for s in sessions)
    prompt = (
        "You are a friendly study coach. Based on these study sessions, "
        "give one short, practical tip (max 3 sentences). "
        "These sessions are from the last 7 days.\n\n" + summary
    )

    for model in MODELS:
        try:
            response = await asyncio.wait_for(
                client.aio.models.generate_content(model=model, contents=prompt),
                timeout=8,
            )
            return response.text.strip()
        except Exception as e:
            print(f"Gemini error ({model}):", repr(e))

    return basic_tip(sessions)