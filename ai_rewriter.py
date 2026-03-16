import os
from dotenv import load_dotenv
from openai import OpenAI
from config import NVIDIA_API_KEY

load_dotenv()

def rewrite_post(original_text: str) -> str:
    """
    Takes the original post draft and uses an LLM to rewrite it into a highly engaging,
    attractive X (Twitter) post under 280 characters.
    """
    api_key = NVIDIA_API_KEY
    if not api_key or api_key == "add_your_nvidia_api_key_here":
        print("Warning: NVIDIA_API_KEY in config.py is invalid. Returning original text.")
        return original_text
        
    try:
        client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=api_key
        )
        
        prompt_text = (
            "You are an expert social media manager and copywriter. Your task is to rewrite the provided text into an exclusive, highly attractive, and engaging X (Twitter) post.\n\n"
            "CRITICAL CONSTRAINTS:\n"
            "1. MUST be strictly UNDER 280 characters. This is non-negotiable.\n"
            "2. Make it highly interactive (ask a question, run an informal poll, or include a clear call-to-action like 'Reply with your thoughts').\n"
            "3. Make it sound premium and exciting.\n"
            "4. Output ONLY the post content. NO conversational filler, NO quotation marks at the start/end, and avoid excessive hashtags."
        )
        
        # We loop a few times if the LLM hallucinatingly goes over 280
        for _ in range(3):
            response = client.chat.completions.create(
                model="meta/llama-3.1-405b-instruct",
                messages=[
                    {"role": "system", "content": prompt_text},
                    {"role": "user", "content": f"Original draft: {original_text}"}
                ],
                temperature=0.7,
                top_p=1,
                max_tokens=150,
            )
            
            rewritten = response.choices[0].message.content.strip()
            # Clean possible surrounding quotes just in case
            if rewritten.startswith('"') and rewritten.endswith('"'):
                rewritten = rewritten[1:-1]
                
            if len(rewritten) <= 280:
                return rewritten
                
        # If it fails 3 times, truncate it safely
        print("Warning: AI failed to keep it under 280 characters. Truncating.")
        return rewritten[:277] + "..."
    except Exception as e:
        print(f"Error during AI rewriting: {e}")
        return original_text

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
