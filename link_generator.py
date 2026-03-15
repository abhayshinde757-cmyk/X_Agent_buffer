def extract_post_link(response):

    try:
        post_id = response["data"]["createPost"]["post"]["id"]

        return f"Post created successfully. Buffer Post ID: {post_id}"

    except Exception:
        return response