import requests
from config import API_KEY, CHANNEL_ID, GRAPHQL_URL


import json

def create_post(text, image_url=None):

    assets_section = ""

    if image_url:
        assets_section = f"""
        assets: {{
            images: [
                {{
                    url: "{image_url}"
                }}
            ]
        }}
        """

    # We use json.dumps to safely escape any quotes or newlines in the text
    escaped_text = json.dumps(text)

    query = f"""
    mutation CreatePost {{
      createPost(input: {{
        text: {escaped_text},
        channelId: "{CHANNEL_ID}",
        schedulingType: automatic,
        mode: shareNow,
        {assets_section}
      }}) {{
        ... on PostActionSuccess {{
          post {{
            id
            text
            externalLink
          }}
        }}
        ... on MutationError {{
          message
        }}
      }}
    }}
    """

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        GRAPHQL_URL,
        json={"query": query},
        headers=headers
    )

    return response.json()