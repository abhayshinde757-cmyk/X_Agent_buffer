from validator import validate_post_text
from scheduler import convert_to_utc
from buffer_client import create_post
from link_generator import extract_post_link


def run_agent():

    print("\n📢 Event Outreach Posting Agent\n")

    # Input from master agent
    text = input("Enter post text received from master agent:\n")

    # Poster agent image
    image_url = input("Enter poster image URL (or press Enter if none): ")

    try:
        validated_text = validate_post_text(text)
    except ValueError as e:
        print("Validation failed:", e)
        return

    print("\nValidated Post:")
    print(validated_text)

    confirm = input("\nDo you want to post this on X? (yes/no): ")

    if confirm.lower() != "yes":
        print("Posting cancelled.")
        return

    user_time = input(
        "\nEnter schedule time in IST (YYYY-MM-DD HH:MM): "
    )

    due_at = convert_to_utc(user_time)

    print("\nScheduling post...\n")

    response = create_post(
        validated_text,
        due_at,
        image_url if image_url else None
    )

    link = extract_post_link(response)

    print("\nResult:")
    print(link)


if __name__ == "__main__":
    run_agent()