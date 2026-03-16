def extract_post_link(response):

    try:
        post_data = response["data"]["createPost"]["post"]
        post_id = post_data["id"]
        post_link = post_data.get("externalLink", "Link not available yet")

        return f"Post created successfully.\nBuffer Post ID: {post_id}\nTwitter Link: {post_link}"

    except Exception:
        return response