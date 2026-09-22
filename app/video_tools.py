import uuid
from google import genai
from google.genai import types
from google.cloud import storage
from google.adk.tools import ToolContext

PROJECT_ID = "qwiklabs-gcp-01-eb75fbb5d865"
BUCKET_NAME = "smart-pantry-chef-media-qwiklabs-gcp-01-eb75fbb5d865"


async def generate_dish_video(
    description: str, tool_context: ToolContext
) -> str:
    """Generates a short video for a dish or food item in the agent's domain using gemini-omni-flash-preview, saves it to agent artifacts, and uploads it to public Cloud Storage.

    Args:
        description: Description of the dish or culinary presentation to generate a video for.
        tool_context: ADK ToolContext used to save artifact for the Playground.

    Returns:
        The public HTTPS URL of the uploaded video on Cloud Storage.
    """
    client = genai.Client(
        vertexai=True, project=PROJECT_ID, location="global"
    )
    prompt = f"Generate a short video clip showing the preparation or culinary presentation of: {description}"

    interaction = client.interactions.create(
        model="gemini-omni-flash-preview",
        input=prompt,
    )

    video_bytes = None
    if getattr(interaction, "outputs", None):
        for output in interaction.outputs:
            if getattr(output, "content", None):
                for part in output.content:
                    if getattr(part, "inline_data", None) and part.inline_data.data:
                        video_bytes = part.inline_data.data
                        break
            if video_bytes:
                break

    if not video_bytes:
        raise RuntimeError(
            f"No video bytes returned from gemini-omni-flash-preview model for description: {description}"
        )

    # 1. Save artifact for Playground Artifacts panel
    filename = f"dish_video_{uuid.uuid4().hex[:8]}.mp4"
    artifact_part = types.Part.from_bytes(
        data=video_bytes, mime_type="video/mp4"
    )
    await tool_context.save_artifact(filename=filename, artifact=artifact_part)

    # 2. Upload video bytes to public Cloud Storage bucket
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(BUCKET_NAME)
    object_key = f"videos/{filename}"
    blob = bucket.blob(object_key)
    blob.upload_from_string(video_bytes, content_type="video/mp4")

    return f"https://storage.googleapis.com/{BUCKET_NAME}/{object_key}"
