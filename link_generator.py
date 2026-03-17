def extract_post_link(response):
    """
    Returns a pure URL string (or a helpful fallback) from the Buffer API response.
    """
    try:
        if not response:
            return "https://x.com"
            
        if "errors" in response:
            return "https://x.com"

        if "data" not in response or not response["data"]:
            return "https://x.com"

        create_post_data = response["data"].get("createPost", {})
        post_data = create_post_data.get("post")
        
        if not post_data:
            return "https://x.com"

        post_id = post_data.get("id", "")
        post_link = post_data.get("externalLink")
        
        # If Buffer hasn't provided the link yet, we can try a helpful fallback
        if not post_link or post_link == "None":
            if post_id:
                 # Standard Buffer post link format if available, or just X.com
                 return f"https://publish.buffer.com/profile/{post_id}" 
            return "https://x.com"

        return str(post_link)

    except Exception:
        return "https://x.com"