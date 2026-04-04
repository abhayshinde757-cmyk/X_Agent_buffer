import os
from dotenv import load_dotenv
from openai import OpenAI, APIStatusError
from config import NVIDIA_API_KEY

load_dotenv()

CORE_FIELD_LABELS = {
    "event title": "Event Name",
    "speaker": "Speaker",
    "location": "Venue",
    "event description": "Description",
    "time": "Time",
    "meetup link": "Link",
}


def _normalize_event_data(event_data) -> dict:
    """Support both structured row input and raw draft text."""
    if isinstance(event_data, dict):
        normalized = {}
        for key, value in event_data.items():
            text = str(value).strip()
            if text.lower() in {"", "nan", "none"}:
                continue
            normalized[str(key)] = text
        return normalized

    text = str(event_data).strip()
    return {"draft text": text} if text else {}


def _build_event_details(event_data: dict) -> str:
    lines = []
    seen = set()

    for key, label in CORE_FIELD_LABELS.items():
        value = event_data.get(key)
        if value:
            lines.append(f"{label}: {value}")
            seen.add(key)

    for key, value in event_data.items():
        if key in seen:
            continue
        label = str(key).replace("_", " ").strip().title()
        lines.append(f"{label}: {value}")

    return "\n".join(lines)


def rewrite_post(event_data) -> str:
    """
    Takes structured event data and uses an LLM to rewrite it into a highly engaging,
    attractive X (Twitter) post under 280 characters.
    """
    normalized_data = _normalize_event_data(event_data)
    if not normalized_data:
        raise ValueError("No event details provided for rewriting.")

    api_key = NVIDIA_API_KEY
    if not api_key or api_key == "add_your_nvidia_api_key_here":
        print("Warning: NVIDIA_API_KEY in config.py is invalid. Returning basic text.")
        title = normalized_data.get("event title") or normalized_data.get("draft text") or "Untitled event"
        location = normalized_data.get("location")
        return f"Event: {title}" + (f" @ {location}" if location else "")
        
    try:
        client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=api_key
        )
        
        prompt_text = (
            "You are an expert social media manager. Rewrite the provided event details into a high-impact X (Twitter) post.\n\n"
            "STRICT REQUIREMENTS:\n"
            "1. MUST be under 280 characters.\n"
            "2. Use the most important event details provided below and incorporate any extra columns only when they add useful context.\n"
            "3. Format it cleanly with emojis or bullet points.\n"
            "4. Make it exciting and professional.\n"
            "5. Output ONLY the post content."
        )
        
        event_details = _build_event_details(normalized_data)
        
        for _ in range(3):
            response = client.chat.completions.create(
                model="meta/llama-3.1-405b-instruct",
                messages=[
                    {"role": "system", "content": prompt_text},
                    {"role": "user", "content": f"Event Details:\n{event_details}"}
                ],
                temperature=0.7,
                max_tokens=200,
            )
            
            rewritten = response.choices[0].message.content.strip()
            if rewritten.startswith('"') and rewritten.endswith('"'):
                rewritten = rewritten[1:-1]
            if len(rewritten) <= 280:
                return rewritten
                
        # If it fails 3 times, truncate it safely
        print("Warning: AI failed to keep it under 280 characters. Truncating.")
        return rewritten[:277] + "..."
    except APIStatusError as e:
        if e.status_code == 403:
            print(
                "Error during AI rewriting: NVIDIA API authorization failed. "
                "Check NVIDIA_API_KEY access, model permissions, and account status."
            )
        else:
            print(f"Error during AI rewriting: API status {e.status_code} - {e}")
        title = normalized_data.get("event title") or normalized_data.get("draft text") or "our next event"
        return f"Join us for {title}!"
    except Exception as e:
        print(f"Error during AI rewriting: {e}")
        title = normalized_data.get("event title") or normalized_data.get("draft text") or "our next event"
        return f"Join us for {title}!"

def generate_qa_insights(posts: list) -> str:
    """
    Takes a list of scraped post dictionaries and uses the LLM to generate deep insights,
    topic clustering, and Q&A (solving user problems/queries found in the tweets).
    """
    api_key = NVIDIA_API_KEY
    if not api_key or api_key == "add_your_nvidia_api_key_here":
        return "Warning: NVIDIA_API_KEY in config.py is invalid. Cannot perform AI analysis."
        
    if not posts:
        return "No posts to analyze."

    # Extract text from the dictionaries
    combined_tweets = "\n".join([f"- {p['text']}" for p in posts])

    try:
        client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=api_key
        )
        
        prompt_text = (
            "You are an expert Social Media Data Analyst and Strategist. I will provide you with a list of raw posts scraped from X (Twitter).\n\n"
            "Your task is to analyze these posts and provide a concise intelligence report formatted precisely as follows:\n\n"
            "🧠 **KEY TAKEAWAYS**\n"
            "- [Provide a 2-3 sentence summary of the overall sentiment, primary topic clusters, and general vibe/testimonials of the crowd.]\n\n"
            "❓ **AUDIENCE Q&A & PROBLEM SOLVING**\n"
            "- [Identify 2 to 4 implicit or explicit questions, pain points, or problems the users in these posts are experiencing.]\n"
            "- [For each question/problem, provide a direct, strategic ANSWER or SOLUTION based on the context or general industry knowledge.]\n\n"
            "CRITICAL: Be concise, insightful, and formatting correctly. Do not include metadata or conversational filler."
        )

        response = client.chat.completions.create(
            model="meta/llama-3.1-405b-instruct",
            messages=[
                {"role": "system", "content": prompt_text},
                {"role": "user", "content": f"Here are the tweets:\n{combined_tweets}"}
            ],
            temperature=0.3,
            top_p=1,
            max_tokens=800,
        )
        
        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"Error during AI Data Analysis: {e}"


if __name__ == "__main__":
    # Test
    sample = "we are having an event tomorrow please come it will be fun"
    print("Original:", sample)
    print("Rewritten:\n", rewrite_post(sample))
