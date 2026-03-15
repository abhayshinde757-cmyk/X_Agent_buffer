import requests
from config import API_KEY, CHANNEL_ID, GRAPHQL_URL


def create_post(text, due_at, image_url=None):

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

    query = f"""
    mutation CreatePost {{
      createPost(input: {{
        text: "{text}",
        channelId: "{CHANNEL_ID}",
        schedulingType: automatic,
        mode: customScheduled,
        dueAt: "{due_at}",
        {assets_section}
      }}) {{
        ... on PostActionSuccess {{
          post {{
            id
            text
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