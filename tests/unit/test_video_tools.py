import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from app.video_tools import generate_dish_video


class TestVideoTools(unittest.IsolatedAsyncioTestCase):

    @patch("app.video_tools.storage.Client")
    @patch("app.video_tools.genai.Client")
    async def test_generate_dish_video_success(self, mock_genai, mock_storage):
        # Setup mock video bytes
        mock_video_bytes = b"\x00\x00\x00\x1cftypisomvideo"

        # Setup mock interaction response
        mock_part = MagicMock()
        mock_part.inline_data.data = mock_video_bytes
        mock_output = MagicMock()
        mock_output.content = [mock_part]
        mock_interaction = MagicMock()
        mock_interaction.outputs = [mock_output]

        mock_genai_instance = MagicMock()
        mock_genai_instance.interactions.create.return_value = mock_interaction
        mock_genai.return_value = mock_genai_instance

        # Setup mock GCS storage
        mock_storage_instance = MagicMock()
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_bucket.blob.return_value = mock_blob
        mock_storage_instance.bucket.return_value = mock_bucket
        mock_storage.return_value = mock_storage_instance

        # Setup mock ToolContext
        mock_tool_context = MagicMock()
        mock_tool_context.save_artifact = AsyncMock()

        url = await generate_dish_video("Sizzling garlic chicken pan", mock_tool_context)

        # Assertions
        mock_genai_instance.interactions.create.assert_called_once()
        mock_tool_context.save_artifact.assert_called_once()
        mock_blob.upload_from_string.assert_called_once_with(mock_video_bytes, content_type="video/mp4")
        self.assertTrue(url.startswith("https://storage.googleapis.com/smart-pantry-chef-media-qwiklabs-gcp-01-eb75fbb5d865/videos/"))
        self.assertTrue(url.endswith(".mp4"))


if __name__ == "__main__":
    unittest.main()
