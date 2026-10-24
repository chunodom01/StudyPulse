import asyncio

from google import genai

from app.config import settings

client = genai.Client(api_key=settings.gemini_api_key) if settings.gemini_api_key else None

MODEL = "gemini-3.8-flash"


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
        "give one short, practical tip (max 3 sentences).\n\n" + summary
    )

    for attempt in range(3):
        try:
            response = await client.aio.models.generate_content(model=MODEL, contents=prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Gemini error (attempt {attempt + 1}):", e)
            if "503" not in str(e) and "429" not in str(e):
                break
            await asyncio.sleep(2 * (attempt + 1))

    return basic_tip(sessions)