def extract_post_link(response):
    try:
        # Check for mutation errors first
        if "data" in response and response["data"].get("createPost", {}).get("message"):
            return f"Buffer Error: {response['data']['createPost']['message']}"

        post_data = response["data"]["createPost"]["post"]
        post_id = post_data["id"]
        
        # Buffer often returns None if the link isn't ready on X's end yet
        post_link = post_data.get("externalLink")
        if not post_link or post_link == "None":
            post_link = "URL will be ready on X in a moment."

        return f"Post created successfully.\nBuffer Post ID: {post_id}\nTwitter Link: {post_link}"

    except Exception as e:
        return f"Unexpected Response Structure: {str(e)}"