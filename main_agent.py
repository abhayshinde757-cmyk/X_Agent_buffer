from validator import validate_post_text
from ai_rewriter import rewrite_post
from image_processor import pad_and_upload_image
from buffer_client import create_post
from link_generator import extract_post_link


def run_agent():

    print("\n📢 Event Outreach Posting Agent\n")

    # Input from master agent
    text = input("Enter post text received from master agent:\n")

    # Poster agent image
    image_url = input("Enter poster image URL (or press Enter if none): ")

    print("\n✨ AI is rewriting your post to make it more engaging...\n")
    rewritten_text = rewrite_post(text)

    try:
        validated_text = validate_post_text(rewritten_text)
    except ValueError as e:
        print("Validation failed after AI rewriting:", e)
        print("Using original text as fallback (if valid).")
        try:
            validated_text = validate_post_text(text)
        except ValueError as orig_e:
            print("Original text validation also failed:", orig_e)
            return

    print("---------------------------------")
    print("Original Draft:")
    print(text)
    print("\nAI Enhanced Post:")
    print(validated_text)
    print("---------------------------------")

    confirm = input("\nDo you want to post this on X? (yes/no): ")

    if confirm.lower() != "yes":
        print("Posting cancelled.")
        return

    print("\nPosting to Twitter immediately...\n")

    final_image_url = None
    if image_url:
        print("Processing and padding image to 1200x675 (16:9)...")
        try:
            final_image_url = pad_and_upload_image(image_url)
        except ValueError as e:
            print("\n" + str(e))
            print("Posting cancelled due to image failure.")
            return

    response = create_post(
        validated_text,
        final_image_url
    )

    link = extract_post_link(response)

    print("\nResult:")
    print(link)


if __name__ == "__main__":
    run_agent()