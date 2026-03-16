import io
import requests
from PIL import Image
import re

def parse_gdrive_url(url: str) -> str:
    """Converts a viewable Google Drive link into a direct download link."""
    # Matches URLs like https://drive.google.com/file/d/FILE_ID/view...
    match = re.search(r"/file/d/([a-zA-Z0-9_-]+)/?", url)
    if match:
        file_id = match.group(1)
        return f"https://drive.google.com/uc?export=download&id={file_id}"
        
    # Matches URLs like https://drive.google.com/open?id=FILE_ID
    match_id = re.search(r"id=([a-zA-Z0-9_-]+)", url)
    if "drive.google.com" in url and match_id:
        file_id = match_id.group(1)
        return f"https://drive.google.com/uc?export=download&id={file_id}"
        
    return url

def pad_and_upload_image(image_url: str) -> str:
    """
    Downloads an image from a URL, pads it to exactly 1200x675 (16:9),
    and uploads it to a public host (Catbox) to get a Buffer-compatible URL.
    Returns the new URL, or raises an Exception if something fails.
    """
    if "drive.google.com/drive/folders" in image_url or "drive.google.com/drive/u" in image_url:
        raise ValueError("Provided URL is a Google Drive folder or generic drive link, not a direct file link. Please provide a link to a specific image file.")

    try:
        # Check if it's a Google Drive link
        direct_url = parse_gdrive_url(image_url)
        
        # Download image
        print(f"Downloading image from: {direct_url}")
        resp = requests.get(direct_url, timeout=10)
        resp.raise_for_status()
        
        # Open with Pillow
        image = Image.open(io.BytesIO(resp.content)).convert("RGB")
        target_width, target_height = 1200, 675
        
        original_width, original_height = image.size
        print(f"Original image size: {original_width}x{original_height}")
        
        # Calculate aspect ratio
        ratio = min(target_width / original_width, target_height / original_height)
        new_width = int(original_width * ratio)
        new_height = int(original_height * ratio)
        
        # Resize original image to fit inside 1200x675
        resized_img = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Create a new black 1200x675 canvas
        canvas = Image.new("RGB", (target_width, target_height), (0, 0, 0))
        
        # Calculate centering offsets
        x_offset = (target_width - new_width) // 2
        y_offset = (target_height - new_height) // 2
        
        # Paste the resized image into the center
        canvas.paste(resized_img, (x_offset, y_offset))
        print("Image padded to 1200x675 successfully.")
        
        # Save to memory
        byte_arr = io.BytesIO()
        canvas.save(byte_arr, format='JPEG', quality=90)
        byte_arr.seek(0)
        
        # Upload to an anonymous, public image host (uguu.se)
        print("Uploading padded image to public host...")
        upload_resp = requests.post(
            "https://uguu.se/upload.php",
            files={"files[]": ("padded.jpg", byte_arr, "image/jpeg")}
        )
        
        if upload_resp.status_code == 200:
            resp_json = upload_resp.json()
            if resp_json.get("success"):
                new_url = resp_json["files"][0]["url"]
                print(f"Uploaded successfully! Public URL: {new_url}")
                return new_url
            else:
                raise ValueError(f"Host returned 200 but failed: {resp_json}")
        else:
            raise ValueError(f"Failed to upload to host. Status code: {upload_resp.status_code}, Response: {upload_resp.text}")
            
    except Exception as e:
        print(f"Error processing image: {e}")
        raise ValueError(f"Image processing failed: {e}")

if __name__ == "__main__":
    # Test script with a dummy URL
    test_url = "https://dummyimage.com/400x400/000/fff.png"
    result = pad_and_upload_image(test_url)
    print(f"Final Image URL: {result}")
