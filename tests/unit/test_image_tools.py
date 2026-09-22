import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.image_tools import generate_dish_image, BUCKET_NAME, PROJECT_ID


@pytest.mark.asyncio
async def test_generate_dish_image_success():
    mock_tool_context = AsyncMock()

    mock_part = MagicMock()
    mock_part.inline_data.data = b"fake-image-bytes"

    mock_candidate = MagicMock()
    mock_candidate.content.parts = [mock_part]

    mock_response = MagicMock()
    mock_response.candidates = [mock_candidate]

    with patch("google.genai.Client") as mock_genai_client_cls, \
         patch("google.cloud.storage.Client") as mock_storage_client_cls:

        mock_genai_instance = MagicMock()
        mock_genai_client_cls.return_value = mock_genai_instance
        mock_genai_instance.models.generate_content.return_value = mock_response

        mock_storage_instance = MagicMock()
        mock_storage_client_cls.return_value = mock_storage_instance
        mock_bucket = MagicMock()
        mock_storage_instance.bucket.return_value = mock_bucket
        mock_blob = MagicMock()
        mock_bucket.blob.return_value = mock_blob

        url = await generate_dish_image("Avocado Toast", mock_tool_context)

        assert url.startswith(f"https://storage.googleapis.com/{BUCKET_NAME}/dishes/dish_")
        assert url.endswith(".jpg")

        mock_genai_client_cls.assert_called_once_with(
            vertexai=True, project=PROJECT_ID, location="global"
        )
        mock_tool_context.save_artifact.assert_called_once()
        mock_blob.upload_from_string.assert_called_once_with(b"fake-image-bytes", content_type="image/jpeg")
