import uuid
from google import genai
from google.genai import types
from google.cloud import storage
from google.adk.tools import ToolContext

PROJECT_ID = "qwiklabs-gcp-01-eb75fbb5d865"
BUCKET_NAME = "smart-pantry-chef-media-qwiklabs-gcp-01-eb75fbb5d865"


async def generate_dish_image(
    description: str, tool_context: ToolContext
) -> str:
    """Generates an image for a dish or food item in the agent's domain, saves it to agent artifacts, and uploads it to public Cloud Storage.

    Args:
        description: Description of the dish or food presentation to generate.
        tool_context: ADK ToolContext used to save artifact for the Playground.

    Returns:
        The public HTTPS URL of the uploaded image on Cloud Storage.
    """
    client = genai.Client(
        vertexai=True, project=PROJECT_ID, location="global"
    )
    prompt = f"High-quality culinary presentation photo of: {description}"

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite-image",
        contents=prompt,
    )

    image_bytes = None
    if response.candidates:
        for part in response.candidates[0].content.parts:
            if part.inline_data:
                image_bytes = part.inline_data.data
                break

    if not image_bytes:
        raise RuntimeError(
            f"No image bytes returned from model for description: {description}"
        )

    # 1. Save artifact for Playground Artifacts panel
    filename = f"dish_{uuid.uuid4().hex[:8]}.jpg"
    artifact_part = types.Part.from_bytes(
        data=image_bytes, mime_type="image/jpeg"
    )
    await tool_context.save_artifact(filename=filename, artifact=artifact_part)

    # 2. Upload image bytes to public Cloud Storage bucket
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(BUCKET_NAME)
    object_key = f"dishes/{filename}"
    blob = bucket.blob(object_key)
    blob.upload_from_string(image_bytes, content_type="image/jpeg")

    return f"https://storage.googleapis.com/{BUCKET_NAME}/{object_key}"
