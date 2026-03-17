import os
from dotenv import load_dotenv
from openai import OpenAI
from config import NVIDIA_API_KEY

load_dotenv()

def rewrite_post(event_data: dict) -> str:
    """
    Takes structured event data and uses an LLM to rewrite it into a highly engaging,
    attractive X (Twitter) post under 280 characters.
    """
    api_key = NVIDIA_API_KEY
    if not api_key or api_key == "add_your_nvidia_api_key_here":
        print("Warning: NVIDIA_API_KEY in config.py is invalid. Returning basic text.")
        return f"Event: {event_data.get('event title')} @ {event_data.get('location')}"
        
    try:
        client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=api_key
        )
        
        prompt_text = (
            "You are an expert social media manager. Rewrite the provided event details into a high-impact X (Twitter) post.\n\n"
            "STRICT REQUIREMENTS:\n"
            "1. MUST be under 280 characters.\n"
            "2. MUST include these specific fields: Event Name, Speaker, Venue (Location), Description, and Time.\n"
            "3. Format it cleanly with emojis or bullet points.\n"
            "4. Make it exciting and professional.\n"
            "5. Output ONLY the post content."
        )
        
        event_details = (
            f"Event Name: {event_data.get('event title')}\n"
            f"Speaker: {event_data.get('speaker')}\n"
            f"Venue: {event_data.get('location')}\n"
            f"Description: {event_data.get('event description')}\n"
            f"Time: {event_data.get('time')}\n"
            f"Link: {event_data.get('meetup link')}\n"
        )
        
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
    except Exception as e:
        print(f"Error during AI rewriting: {e}")
        return f"Join us for {event_data.get('event title')}!"

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
