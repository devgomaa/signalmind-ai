from .static_post import StaticPostGenerator
from .video_generator import VideoGenerator
import os


class MediaService:

    def __init__(self):
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.veo_key = os.getenv("AIML_API_KEY")


    def generate_static_posts(self, ideas_json):

        generator = StaticPostGenerator(
            api_key=self.gemini_key,
            aspect_ratio="4:5",
            output_dir="output_content"
        )

        return generator.generate_all(ideas_json)


    def generate_videos(self, ideas_json):

        generator = VideoGenerator(
            api_key=self.veo_key,
            image_url="https://your-product-image.png",
            aspect_ratio="9:16"
        )

        return generator.generate_all(ideas_json)