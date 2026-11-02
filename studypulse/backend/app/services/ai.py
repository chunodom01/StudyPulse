import asyncio

from google import genai
from google.genai import types
from app.config import settings

client = genai.Client(api_key=settings.gemini_api_key) if settings.gemini_api_key else None

MODELS = [
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-3.8-flash",
]
STYLE = {
    "en": (
        "Reply in English. Sound like an upbeat friend who is proud of them: "
        "warm, energetic and casual. Use 1-2 emojis."
    ),
    "km": (
        "Reply in Khmer (ភាសាខ្មែរ) script. Write the way a friendly Cambodian "
        "older sibling or classmate talks in a chat: casual spoken Khmer, warm and "
        "energetic, with 1-2 emojis. Do NOT sound formal, like a textbook, or like "
        "a machine translation. Use short sentences and natural everyday words."
    ),
}


def basic_tip(sessions: list[dict], lang: str = "en") -> str:
    if not sessions:
        if lang == "km":
            return "មិនទាន់មានវគ្គសិក្សានៅឡើយទេ។ សូមបន្ថែមវគ្គសិក្សាដំបូងរបស់អ្នក។"
        return "No sessions yet. Add your first study session to get a tip."

    total = sum(s["minutes"] for s in sessions)
    by_subject = {}
    for s in sessions:
        key = s["subject"].strip().lower()
        by_subject[key] = by_subject.get(key, 0) + s["minutes"]

    top = max(by_subject, key=by_subject.get)
    least = min(by_subject, key=by_subject.get)

    if lang == "km":
        tip = f"អ្នកបានសិក្សាសរុប {total} នាទី។ មុខវិជ្ជាដែលសិក្សាច្រើនបំផុត៖ {top} ({by_subject[top]} នាទី)។"
        if top != least:
            tip += f" សូមសាកល្បងចំណាយពេលបន្ថែមលើ {least} ({by_subject[least]} នាទីប៉ុណ្ណោះ)។"
        return tip

    tip = f"You studied {total} minutes in total. Most time: {top} ({by_subject[top]} min)."
    if top != least:
        tip += f" Try giving {least} a bit more time ({by_subject[least]} min so far)."
    return tip


async def generate_tip(sessions: list[dict], lang: str = "en") -> str:
    if not sessions:
        return basic_tip(sessions, lang)
    if client is None:
        return basic_tip(sessions, lang)

    language_line = (
        "Reply in Khmer (ភាសាខ្មែរ), using Khmer script."
        if lang == "km"
        else "Reply in English."
    )

    summary = "\n".join(f"- {s['subject']}: {s['minutes']} min" for s in sessions)
    prompt = (
      "You are a fun, supportive study buddy, not a robot and not a strict teacher. "
        "Below are the student's study sessions from the last 7 days. "
        "First, cheer them on for something specific they did (mention a subject "
        "and the minutes). Then give one small, practical tip. "
        "Maximum 3 sentences. No bullet points, no headings, no greeting like 'Dear user'.\n\n"
        + STYLE.get(lang, STYLE["en"])
        + "\n\nSessions:\n"
        + summary
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

    return basic_tip(sessions, lang)